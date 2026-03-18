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
 *   1. Send image to Vision service → volume, weight, carbs, GL
 *   2. Send meal info + patient context to RAG → advice, insulin dose
 *   3. Combine results + publish Kafka event
 */
@Service
public class PipelineService {

    private static final Logger log = LoggerFactory.getLogger(PipelineService.class);
    private static final String DISCLAIMER =
            "Kết quả chỉ mang tính tham khảo. Không thay thế chỉ định của bác sĩ.";

    private final VisionServiceClient visionClient;
    private final RagServiceClient ragClient;
    private final KafkaEventPublisher kafkaPublisher;

    public PipelineService(
            VisionServiceClient visionClient,
            RagServiceClient ragClient,
            KafkaEventPublisher kafkaPublisher
    ) {
        this.visionClient = visionClient;
        this.ragClient = ragClient;
        this.kafkaPublisher = kafkaPublisher;
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> analyzeFull(
            MultipartFile image,
            String foodId,
            Double glucoseLevel,
            String diabetesType,
            Double insulinCarbRatio,
            Double correctionFactor,
            Double targetGlucose
    ) throws IOException {
        long startTime = System.currentTimeMillis();
        List<String> warnings = new ArrayList<>();

        // ── Step 1: Vision Service ────────────────────────────────────
        log.info("Step 1/2: Calling Vision service...");
        Map<String, Object> visionResult = visionClient.estimateVolume(image, foodId);

        String foodName = getStr(visionResult, "food_name_vi", "Unknown");
        double volumeMl = getNum(visionResult, "volume_ml", 0);
        double weightG = getNum(visionResult, "weight_g", 0);
        double carbG = getNum(visionResult, "carb_g", 0);
        double glycemicLoad = getNum(visionResult, "glycemic_load", 0);
        String estimationQuality = getStr(visionResult, "estimation_quality", "medium");

        // GL level classification
        String glLevel;
        if (glycemicLoad < 10) glLevel = "low";
        else if (glycemicLoad <= 20) glLevel = "medium";
        else glLevel = "high";

        // Confidence from estimation quality
        double confidence;
        switch (estimationQuality) {
            case "high" -> confidence = 0.9;
            case "medium" -> confidence = 0.7;
            default -> confidence = 0.5;
        }
        if ("low".equals(estimationQuality)) {
            warnings.add("Volume estimation quality is low — result may be inaccurate.");
        }

        // ── Step 2: RAG Service ───────────────────────────────────────
        String advice = null;
        String insulinSuggestion = null;

        try {
            log.info("Step 2/2: Calling RAG service...");
            Map<String, Object> patientCtx = buildPatientContext(
                    glucoseLevel, diabetesType, insulinCarbRatio,
                    correctionFactor, targetGlucose
            );

            Map<String, Object> ragResult = ragClient.getAdvice(
                    foodName, glycemicLoad, carbG, patientCtx
            );

            advice = (String) ragResult.get("advice");

            // Extract insulin recommendation
            Object insulinRecObj = ragResult.get("insulin_recommendation");
            if (insulinRecObj instanceof Map) {
                Map<String, Object> insulinRec = (Map<String, Object>) insulinRecObj;
                double totalUnits = getNum(insulinRec, "total_units", 0);
                String calcDetails = getStr(insulinRec, "calculation_details", "");
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
        response.put("disclaimer", DISCLAIMER);

        // ── Publish Kafka event (async, non-blocking) ─────────────────
        kafkaPublisher.publishMealAnalysis(response);

        log.info("Pipeline complete: {} → GL={} ({}) in {}ms",
                foodName, glycemicLoad, glLevel, pipelineMs);
        return response;
    }

    private Map<String, Object> buildPatientContext(
            Double glucoseLevel, String diabetesType,
            Double insulinCarbRatio, Double correctionFactor, Double targetGlucose
    ) {
        Map<String, Object> ctx = new HashMap<>();
        if (glucoseLevel != null) ctx.put("current_glucose_mg_dl", glucoseLevel);
        ctx.put("diabetes_type", diabetesType != null ? diabetesType : "type_2");
        ctx.put("medications", List.of());
        if (insulinCarbRatio != null) ctx.put("insulin_to_carb_ratio", insulinCarbRatio);
        if (correctionFactor != null) ctx.put("correction_factor", correctionFactor);
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
}
