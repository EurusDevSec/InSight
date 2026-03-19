package com.insight.controller;

import com.insight.service.PipelineService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@ExtendWith(MockitoExtension.class)
class AnalysisControllerTest {

        private MockMvc mockMvc;

        @Mock
        private PipelineService pipelineService;

        @BeforeEach
        void setUp() {
                mockMvc = MockMvcBuilders.standaloneSetup(
                                new AnalysisController(pipelineService)).build();
        }

        @Test
        void analyzeShouldReturnMealResult() throws Exception {
                Map<String, Object> mockResult = createMockResult();

                when(pipelineService.analyzeFull(any(), any(), any(), any(), any(), any(), any(), anyBoolean()))
                                .thenReturn(mockResult);

                MockMultipartFile image = new MockMultipartFile(
                                "image", "test.jpg", "image/jpeg", "fake-image-data".getBytes());

                mockMvc.perform(multipart("/api/gateway/analyze")
                                .file(image)
                                .param("food_id", "vn_com_trang")
                                .param("glucose_level", "120"))
                                .andExpect(status().isOk())
                                .andExpect(jsonPath("$.food_name").value("Cơm trắng"))
                                .andExpect(jsonPath("$.glycemic_load").value(13.7))
                                .andExpect(jsonPath("$.gl_level").value("medium"))
                                .andExpect(jsonPath("$.advice").value("Test advice"))
                                .andExpect(jsonPath("$.disclaimer").exists());
        }

        @Test
        void analyzeShouldWorkWithImageOnly() throws Exception {
                when(pipelineService.analyzeFull(any(), any(), any(), any(), any(), any(), any(), anyBoolean()))
                                .thenReturn(createMockResult());

                MockMultipartFile image = new MockMultipartFile(
                                "image", "photo.png", "image/png", "png-data".getBytes());

                mockMvc.perform(multipart("/api/gateway/analyze").file(image))
                                .andExpect(status().isOk())
                                .andExpect(jsonPath("$.food_name").exists())
                                .andExpect(jsonPath("$.warnings").isArray());
        }

        @Test
        void analyzeShouldReturn400WithoutImage() throws Exception {
                mockMvc.perform(multipart("/api/gateway/analyze"))
                                .andExpect(status().isBadRequest());
        }

        @Test
        void analyzeShouldIncludeAllPatientParams() throws Exception {
                when(pipelineService.analyzeFull(any(), any(), any(), any(), any(), any(), any(), anyBoolean()))
                                .thenReturn(createMockResult());

                MockMultipartFile image = new MockMultipartFile(
                                "image", "test.jpg", "image/jpeg", "data".getBytes());

                mockMvc.perform(multipart("/api/gateway/analyze")
                                .file(image)
                                .param("food_id", "vn_pho_bo")
                                .param("glucose_level", "180")
                                .param("diabetes_type", "type_1")
                                .param("insulin_carb_ratio", "10")
                                .param("correction_factor", "50")
                                .param("target_glucose", "100"))
                                .andExpect(status().isOk())
                                .andExpect(jsonPath("$.food_name").exists());
        }

        private Map<String, Object> createMockResult() {
                Map<String, Object> result = new LinkedHashMap<>();
                result.put("food_name", "Cơm trắng");
                result.put("volume_ml", 433.2);
                result.put("weight_g", 350.0);
                result.put("carbs_g", 45.5);
                result.put("glycemic_load", 13.7);
                result.put("gl_level", "medium");
                result.put("confidence", 0.9);
                result.put("advice", "Test advice");
                result.put("insulin_suggestion", "4.5 units — ICR=10");
                result.put("warnings", List.of());
                result.put("pipeline_time_ms", 2500);
                result.put("disclaimer", "Test disclaimer");
                return result;
        }
}
