package com.insight.controller;

import com.insight.service.PipelineService;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Map;

/**
 * REST API Gateway — unified entry point for the InSight pipeline.
 *
 * Accepts image + parameters from the Flutter app, orchestrates
 * Vision → RAG services, and returns a combined response.
 */
@RestController
@RequestMapping("/api/gateway")
public class AnalysisController {

    private final PipelineService pipelineService;

    public AnalysisController(PipelineService pipelineService) {
        this.pipelineService = pipelineService;
    }

    /**
     * Full analysis pipeline: Image → Vision (volume/GL) → RAG (advice).
     *
     * @param image            Food image (JPEG/PNG, max 10MB)
     * @param foodId           Nutrition DB food ID (e.g. "vn_com_trang",
     *                         "vn_pho_bo")
     * @param glucoseLevel     Current blood glucose in mg/dL
     * @param diabetesType     Diabetes type: type_1, type_2, gestational
     * @param insulinCarbRatio Insulin-to-Carb Ratio (1 Unit per X grams)
     * @param correctionFactor Correction Factor (mg/dL per 1 Unit)
     * @param targetGlucose    Target blood glucose in mg/dL
     */
    @PostMapping(value = "/analyze", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<Map<String, Object>> analyze(
            @RequestParam("image") MultipartFile image,
            @RequestParam(value = "food_id", required = false) String foodId,
            @RequestParam(value = "glucose_level", required = false) Double glucoseLevel,
            @RequestParam(value = "diabetes_type", required = false, defaultValue = "type_2") String diabetesType,
            @RequestParam(value = "insulin_carb_ratio", required = false) Double insulinCarbRatio,
            @RequestParam(value = "correction_factor", required = false) Double correctionFactor,
            @RequestParam(value = "target_glucose", required = false, defaultValue = "120") Double targetGlucose)
            throws IOException {
        Map<String, Object> result = pipelineService.analyzeFull(
                image, foodId, glucoseLevel, diabetesType,
                insulinCarbRatio, correctionFactor, targetGlucose);
        return ResponseEntity.ok(result);
    }
}
