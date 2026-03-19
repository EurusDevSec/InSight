package com.insight.service;

import com.insight.client.RagServiceClient;
import com.insight.client.VisionServiceClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.*;

/**
 * Orchestrates the full analysis pipeline: Vision → RAG → combined response.
 *
 * Pipeline:
 * 1. Send image to Vision service → volume, weight, carbs, GL
 * 2. Send meal info + patient context to RAG → advice, insulin dose
 * 3. Combine results + publish Kafka event
 */
@Service
public class PipelineService {

    private static final Logger log = LoggerFactory.getLogger(PipelineService.class);
    private static final String DISCLAIMER = "Kết quả chỉ mang tính tham khảo. Không thay thế chỉ định của bác sĩ.";

    private final VisionServiceClient visionClient;
    private final RagServiceClient ragClient;
    private final KafkaEventPublisher kafkaPublisher;
    private final CacheService cacheService;

    public PipelineService(
            VisionServiceClient visionClient,
            RagServiceClient ragClient,
            KafkaEventPublisher kafkaPublisher,
            CacheService cacheService) {
        this.visionClient = visionClient;
        this.ragClient = ragClient;
        this.kafkaPublisher = kafkaPublisher;
        this.cacheService = cacheService;
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> analyzeFull(
            MultipartFile image,
            String foodId,
            String customFoodName,
            Double glucoseLevel,
            String diabetesType,
            Double insulinCarbRatio,
            Double correctionFactor,
            Double targetGlucose,
            boolean debug) throws IOException {
        long startTime = System.currentTimeMillis();
        List<String> warnings = new ArrayList<>();

        // ── Step 1: Vision Service ────────────────────────────────────
        long visionStart = System.currentTimeMillis();
        log.info("Step 1/2: Calling Vision service...");
        Map<String, Object> visionResult = visionClient.estimateVolume(image, foodId, debug);
        long visionMs = System.currentTimeMillis() - visionStart;

        String foodName = getStr(visionResult, "food_name_vi", "Unknown");

        // Override food name with custom input for RAG (better advice for unknown
        // foods)
        if (customFoodName != null && !customFoodName.isBlank()) {
            log.info("Custom food name provided: '{}' (overriding '{}')", customFoodName, foodName);
            foodName = customFoodName;
        }

        double volumeMl = getNum(visionResult, "volume_ml", 0);
        double weightG = getNum(visionResult, "weight_g", 0);
        double carbG = getNum(visionResult, "carb_g", 0);
        double glycemicLoad = getNum(visionResult, "glycemic_load", 0);
        String estimationQuality = getStr(visionResult, "estimation_quality", "medium");

        // ── Sanity checks — flag unrealistic values ──────────────────
        boolean volumeClamped = volumeMl >= 800.0;
        if (volumeClamped) {
            warnings.add(
                    "⚠️ Thể tích ước lượng quá lớn (≥800 mL) — có thể do lỗi depth/calibration. Kết quả chỉ mang tính tham khảo.");
            estimationQuality = "low";
        }
        if (weightG > 800) {
            warnings.add("⚠️ Khối lượng ước lượng (" + String.format("%.0f", weightG)
                    + "g) vượt mức thực tế cho 1 phần ăn (thường ≤500g).");
        }
        if (carbG > 150) {
            warnings.add("⚠️ Lượng Carb ước lượng (" + String.format("%.0f", carbG)
                    + "g) quá cao — một phần ăn thường chỉ 30-100g Carb.");
        }

        // GL level classification
        String glLevel;
        if (glycemicLoad < 10)
            glLevel = "low";
        else if (glycemicLoad <= 20)
            glLevel = "medium";
        else
            glLevel = "high";

        // Confidence from estimation quality
        double confidence;
        switch (estimationQuality) {
            case "high" -> confidence = 0.9;
            case "medium" -> confidence = 0.7;
            default -> confidence = 0.5;
        }
        if ("low".equals(estimationQuality)) {
            warnings.add("⚠️ Chất lượng ước lượng thấp — kết quả có thể không chính xác.");
        }

        // ── Step 2: RAG Service (with Redis cache) ──────────────────
        String advice = null;
        String insulinSuggestion = null;
        long ragMs = 0;
        Map<String, Object> ragResult = null;

        try {
            long ragStart = System.currentTimeMillis();
            log.info("Step 2/2: Calling RAG service...");

            // Check cache first
            String cacheKey = cacheService.buildKey(foodName, carbG, glycemicLoad, glucoseLevel);
            ragResult = cacheService.get(cacheKey);

            if (ragResult != null) {
                log.info("RAG cache HIT for {}", foodName);
            } else {
                Map<String, Object> patientCtx = buildPatientContext(
                        glucoseLevel, diabetesType, insulinCarbRatio,
                        correctionFactor, targetGlucose);

                ragResult = ragClient.getAdvice(
                        foodName, glycemicLoad, carbG, patientCtx, debug);

                // Cache the result for future requests
                cacheService.put(cacheKey, ragResult);
            }
            ragMs = System.currentTimeMillis() - ragStart;

            advice = cleanAdviceText((String) ragResult.get("advice"));

            // Extract insulin recommendation
            Object insulinRecObj = ragResult.get("insulin_recommendation");
            if (insulinRecObj instanceof Map) {
                Map<String, Object> insulinRec = (Map<String, Object>) insulinRecObj;
                double totalUnits = getNum(insulinRec, "total_units", 0);
                String calcDetails = getStr(insulinRec, "calculation_details", "");

                // Hard safety cap: max 30 units total (ADA guideline)
                if (totalUnits > 30) {
                    warnings.add("⚠️ CẢNH BÁO: Liều insulin tính toán (" +
                            String.format("%.1f", totalUnits) +
                            "U) quá cao bất thường! Đã giới hạn về 30U. " +
                            "Vui lòng kiểm tra lại hoặc tham khảo bác sĩ NGAY.");
                    totalUnits = 30.0;
                }

                if (totalUnits > 0) {
                    insulinSuggestion = String.format("%.1f units — %s", totalUnits, calcDetails);
                }
            }

            // Check emergency alert
            Object emergencyObj = ragResult.get("emergency_alert");
            if (emergencyObj instanceof Map) {
                Map<String, Object> emergency = (Map<String, Object>) emergencyObj;
                String alertType = (String) emergency.get("alert_type");
                String immediateAction = (String) emergency.get("immediate_action");
                warnings.add("⚠️ " + alertType + ": " + immediateAction);
            }
        } catch (Exception e) {
            log.warn("RAG service unavailable, returning Vision-only results: {}", e.getMessage());
            warnings.add("Advisory service unavailable — showing volume analysis only.");
        }

        long pipelineMs = System.currentTimeMillis() - startTime;

        // ── Build response ────────────────────────────────────────────
        Map<String, Object> response = new LinkedHashMap<>();
        response.put("food_name", foodName);
        response.put("volume_ml", volumeMl);
        response.put("weight_g", weightG);
        response.put("carbs_g", carbG);
        response.put("glycemic_load", glycemicLoad);
        response.put("gl_level", glLevel);
        response.put("confidence", confidence);
        response.put("advice", advice);
        response.put("insulin_suggestion", insulinSuggestion);
        response.put("warnings", warnings);
        response.put("pipeline_time_ms", pipelineMs);
        response.put("vision_time_ms", visionMs);
        response.put("rag_time_ms", ragMs);
        response.put("disclaimer", DISCLAIMER);

        // ── Debug / Developer Mode data (pass-through from services) ────
        if (debug) {
            Map<String, Object> debugData = new LinkedHashMap<>();
            // Vision debug
            debugData.put("depth_preview", visionResult.get("debug_depth_preview"));
            debugData.put("food_mask_preview", visionResult.get("debug_food_mask_preview"));
            debugData.put("reference_objects", visionResult.get("debug_reference_objects"));
            debugData.put("scale_px_per_cm", visionResult.get("debug_scale_px_per_cm"));
            debugData.put("table_level_cm", visionResult.get("debug_table_level_cm"));
            debugData.put("formula", visionResult.get("debug_formula"));
            // RAG debug (may be null if RAG failed)
            if (ragResult != null) {
                debugData.put("retrieved_chunks", ragResult.get("debug_retrieved_chunks"));
                debugData.put("prompt_preview", ragResult.get("debug_prompt_preview"));
                debugData.put("llm_raw", ragResult.get("debug_llm_raw"));
            }
            response.put("debug", debugData);
        }

        // ── Publish Kafka event (async, non-blocking) ─────────────────
        kafkaPublisher.publishMealAnalysis(response);

        log.info("Pipeline complete: {} → GL={} ({}) in {}ms (vision={}ms, rag={}ms)",
                foodName, glycemicLoad, glLevel, pipelineMs, visionMs, ragMs);
        return response;
    }

    private Map<String, Object> buildPatientContext(
            Double glucoseLevel, String diabetesType,
            Double insulinCarbRatio, Double correctionFactor, Double targetGlucose) {
        Map<String, Object> ctx = new HashMap<>();
        if (glucoseLevel != null)
            ctx.put("current_glucose_mg_dl", glucoseLevel);
        ctx.put("diabetes_type", diabetesType != null ? diabetesType : "type_2");
        ctx.put("medications", List.of());
        if (insulinCarbRatio != null)
            ctx.put("insulin_to_carb_ratio", insulinCarbRatio);
        if (correctionFactor != null)
            ctx.put("correction_factor", correctionFactor);
        ctx.put("target_glucose_mg_dl", targetGlucose != null ? targetGlucose : 120.0);
        return ctx;
    }

    private double getNum(Map<String, Object> map, String key, double fallback) {
        Object val = map.get(key);
        return val instanceof Number ? ((Number) val).doubleValue() : fallback;
    }

    private String getStr(Map<String, Object> map, String key, String fallback) {
        Object val = map.get(key);
        return val instanceof String ? (String) val : fallback;
    }

    /**
     * Strip residual markdown/JSON artifacts from LLM advice text.
     */
    private String cleanAdviceText(String raw) {
        if (raw == null || raw.isBlank())
            return raw;

        String text = raw.trim();

        // If the advice text is a JSON object (LLM returned full JSON),
        // extract just the "advice" field value.
        if (text.startsWith("{") && text.contains("\"advice\"")) {
            // Try Jackson first (for well-formed JSON)
            try {
                var mapper = new com.fasterxml.jackson.databind.ObjectMapper();
                var node = mapper.readTree(text);
                if (node.has("advice")) {
                    text = node.get("advice").asText();
                }
            } catch (Exception e) {
                // JSON may be truncated — use regex fallback to extract advice value
                log.debug("Jackson parse failed, trying regex: {}", e.getMessage());
                var m = java.util.regex.Pattern
                        .compile("\"advice\"\\s*:\\s*\"((?:[^\\\\\"]*(?:\\\\.[^\\\\\"]*)*))")
                        .matcher(text);
                if (m.find()) {
                    text = m.group(1)
                            .replace("\\n", "\n")
                            .replace("\\t", "\t")
                            .replace("\\\"", "\"");
                }
            }
        }

        // Remove code fences (```json ... ```)
        text = text.replaceAll("```\\w*\\n?", "");
        // Remove markdown bold **text**
        text = text.replaceAll("\\*\\*(.+?)\\*\\*", "$1");
        // Remove markdown italic *text*
        text = text.replaceAll("\\*(.+?)\\*", "$1");
        // Collapse excessive blank lines
        text = text.replaceAll("\\n{3,}", "\n\n");
        return text.trim();
    }
}
