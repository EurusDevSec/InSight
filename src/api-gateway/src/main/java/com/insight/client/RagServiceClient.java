package com.insight.client;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * HTTP client for the RAG Service (FastAPI on port 8001).
 *
 * Forwards meal data + patient context to POST /api/rag/advise.
 */
@Component
public class RagServiceClient {

    private static final Logger log = LoggerFactory.getLogger(RagServiceClient.class);

    private final RestTemplate restTemplate;
    private final String baseUrl;

    public RagServiceClient(
            RestTemplate restTemplate,
            @Value("${insight.services.rag-url}") String baseUrl
    ) {
        this.restTemplate = restTemplate;
        this.baseUrl = baseUrl;
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> getAdvice(
            String mealDescription,
            Double glycemicLoad,
            Double carbsG,
            Map<String, Object> patientContext
    ) {
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("meal_description", mealDescription);
        if (glycemicLoad != null) requestBody.put("glycemic_load", glycemicLoad);
        if (carbsG != null) requestBody.put("carbs_g", carbsG);
        if (patientContext != null) requestBody.put("patient_context", patientContext);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

        log.info("POST {}/api/rag/advise (meal={})", baseUrl, mealDescription);

        ResponseEntity<Map> response = restTemplate.postForEntity(
                baseUrl + "/api/rag/advise",
                entity,
                Map.class
        );

        return response.getBody();
    }

    public boolean isHealthy() {
        try {
            ResponseEntity<Map> response = restTemplate.getForEntity(
                    baseUrl + "/health", Map.class);
            return response.getStatusCode().is2xxSuccessful();
        } catch (Exception e) {
            return false;
        }
    }
}
