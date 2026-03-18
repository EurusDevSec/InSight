package com.insight.service;

import com.insight.client.RagServiceClient;
import com.insight.client.VisionServiceClient;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mock.web.MockMultipartFile;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PipelineServiceTest {

    @Mock
    private VisionServiceClient visionClient;
    @Mock
    private RagServiceClient ragClient;
    @Mock
    private KafkaEventPublisher kafkaPublisher;

    private PipelineService service;

    @BeforeEach
    void setUp() {
        service = new PipelineService(visionClient, ragClient, kafkaPublisher);
    }

    @Test
    @SuppressWarnings("unchecked")
    void fullPipelineReturnsCorrectResult() throws Exception {
        MockMultipartFile image = mockImage();

        when(visionClient.estimateVolume(any(), any())).thenReturn(visionResult(
                "Cơm trắng", 433.2, 350.0, 45.5, 13.7, "high"));
        when(ragClient.getAdvice(any(), any(), any(), any())).thenReturn(Map.of(
                "advice", "Adjust insulin accordingly",
                "insulin_recommendation", Map.of(
                        "total_units", 4.5,
                        "calculation_details", "ICR=10, 45g carbs")));

        Map<String, Object> result = service.analyzeFull(
                image, "vn_com_trang", 120.0, "type_2", 10.0, 50.0, 120.0);

        assertThat(result.get("food_name")).isEqualTo("Cơm trắng");
        assertThat((Double) result.get("volume_ml")).isEqualTo(433.2);
        assertThat((Double) result.get("glycemic_load")).isEqualTo(13.7);
        assertThat(result.get("gl_level")).isEqualTo("medium");
        assertThat((Double) result.get("confidence")).isEqualTo(0.9);
        assertThat(result.get("advice")).isEqualTo("Adjust insulin accordingly");
        assertThat((String) result.get("insulin_suggestion")).contains("4.5 units");
        assertThat(result.get("disclaimer")).isNotNull();

        verify(kafkaPublisher).publishMealAnalysis(any());
    }

    @Test
    @SuppressWarnings("unchecked")
    void pipelineGracefullyHandlesRagFailure() throws Exception {
        when(visionClient.estimateVolume(any(), any())).thenReturn(visionResult(
                "Phở bò", 500.0, 400.0, 50.0, 25.0, "high"));
        when(ragClient.getAdvice(any(), any(), any(), any()))
                .thenThrow(new RuntimeException("RAG service unavailable"));

        Map<String, Object> result = service.analyzeFull(
                mockImage(), null, null, null, null, null, null);

        assertThat(result.get("food_name")).isEqualTo("Phở bò");
        assertThat(result.get("gl_level")).isEqualTo("high");
        assertThat(result.get("advice")).isNull();
        List<String> warnings = (List<String>) result.get("warnings");
        assertThat(warnings).anyMatch(w -> w.contains("unavailable"));
    }

    @Test
    void glLevelLow() throws Exception {
        when(visionClient.estimateVolume(any(), any())).thenReturn(visionResult(
                "Rau xào", 200.0, 100.0, 8.0, 3.0, "high"));
        when(ragClient.getAdvice(any(), any(), any(), any())).thenReturn(Map.of("advice", "ok"));

        Map<String, Object> result = service.analyzeFull(
                mockImage(), null, null, null, null, null, null);
        assertThat(result.get("gl_level")).isEqualTo("low");
    }

    @Test
    void glLevelMedium() throws Exception {
        when(visionClient.estimateVolume(any(), any())).thenReturn(visionResult(
                "Cháo", 300.0, 200.0, 30.0, 15.0, "medium"));
        when(ragClient.getAdvice(any(), any(), any(), any())).thenReturn(Map.of("advice", "ok"));

        Map<String, Object> result = service.analyzeFull(
                mockImage(), null, null, null, null, null, null);
        assertThat(result.get("gl_level")).isEqualTo("medium");
    }

    @Test
    void glLevelHigh() throws Exception {
        when(visionClient.estimateVolume(any(), any())).thenReturn(visionResult(
                "Cơm tấm", 500.0, 400.0, 60.0, 35.0, "high"));
        when(ragClient.getAdvice(any(), any(), any(), any())).thenReturn(Map.of("advice", "ok"));

        Map<String, Object> result = service.analyzeFull(
                mockImage(), null, null, null, null, null, null);
        assertThat(result.get("gl_level")).isEqualTo("high");
    }

    @Test
    @SuppressWarnings("unchecked")
    void emergencyAlertAddedToWarnings() throws Exception {
        when(visionClient.estimateVolume(any(), any())).thenReturn(visionResult(
                "Cơm", 400.0, 300.0, 45.0, 33.0, "medium"));
        when(ragClient.getAdvice(any(), any(), any(), any())).thenReturn(Map.of(
                "advice", "Seek medical attention",
                "emergency_alert", Map.of(
                        "alert_type", "hyperglycemia",
                        "immediate_action", "Check glucose immediately")));

        Map<String, Object> result = service.analyzeFull(
                mockImage(), null, 280.0, null, null, null, null);

        List<String> warnings = (List<String>) result.get("warnings");
        assertThat(warnings).anyMatch(w -> w.contains("hyperglycemia"));
    }

    @Test
    @SuppressWarnings("unchecked")
    void lowQualityEstimationAddsWarning() throws Exception {
        when(visionClient.estimateVolume(any(), any())).thenReturn(visionResult(
                "Unknown", 100.0, 50.0, 10.0, 5.0, "low"));
        when(ragClient.getAdvice(any(), any(), any(), any())).thenReturn(Map.of("advice", "ok"));

        Map<String, Object> result = service.analyzeFull(
                mockImage(), null, null, null, null, null, null);

        assertThat((Double) result.get("confidence")).isEqualTo(0.5);
        List<String> warnings = (List<String>) result.get("warnings");
        assertThat(warnings).anyMatch(w -> w.toLowerCase().contains("quality"));
    }

    @Test
    void responseAlwaysHasDisclaimer() throws Exception {
        when(visionClient.estimateVolume(any(), any())).thenReturn(visionResult(
                "Phở", 400.0, 300.0, 50.0, 30.0, "high"));
        when(ragClient.getAdvice(any(), any(), any(), any())).thenReturn(Map.of("advice", "ok"));

        Map<String, Object> result = service.analyzeFull(
                mockImage(), null, null, null, null, null, null);

        assertThat(result.get("disclaimer")).isNotNull();
        assertThat((String) result.get("disclaimer")).contains("tham khảo");
    }

    @Test
    @SuppressWarnings("unchecked")
    void pipelineTimeMsIsTracked() throws Exception {
        when(visionClient.estimateVolume(any(), any())).thenReturn(visionResult(
                "Bún", 300.0, 250.0, 40.0, 20.0, "medium"));
        when(ragClient.getAdvice(any(), any(), any(), any())).thenReturn(Map.of("advice", "ok"));

        Map<String, Object> result = service.analyzeFull(
                mockImage(), null, null, null, null, null, null);

        assertThat(result).containsKey("pipeline_time_ms");
        assertThat(((Number) result.get("pipeline_time_ms")).doubleValue()).isGreaterThanOrEqualTo(0);
    }

    // ── Helpers ──────────────────────────────────────────────────────

    private MockMultipartFile mockImage() {
        return new MockMultipartFile(
                "image", "test.jpg", "image/jpeg", "fake-image-data".getBytes());
    }

    private Map<String, Object> visionResult(
            String foodName, double volumeMl, double weightG,
            double carbG, double gl, String quality) {
        Map<String, Object> m = new HashMap<>();
        m.put("food_name_vi", foodName);
        m.put("volume_ml", volumeMl);
        m.put("weight_g", weightG);
        m.put("carb_g", carbG);
        m.put("glycemic_load", gl);
        m.put("estimation_quality", quality);
        return m;
    }
}
