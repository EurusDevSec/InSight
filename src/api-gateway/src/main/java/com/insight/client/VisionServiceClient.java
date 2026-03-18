package com.insight.client;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Map;

/**
 * HTTP client for the Vision Service (FastAPI on port 8000).
 *
 * Forwards image + food_id to POST /api/vision/estimate-volume.
 */
@Component
public class VisionServiceClient {

    private static final Logger log = LoggerFactory.getLogger(VisionServiceClient.class);

    private final RestTemplate restTemplate;
    private final String baseUrl;

    public VisionServiceClient(
            RestTemplate restTemplate,
            @Value("${insight.services.vision-url}") String baseUrl) {
        this.restTemplate = restTemplate;
        this.baseUrl = baseUrl;
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> estimateVolume(MultipartFile image, String foodId) throws IOException {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        byte[] imageBytes = image.getBytes();
        String originalName = image.getOriginalFilename() != null
                ? image.getOriginalFilename()
                : "image.jpg";

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("image", new ByteArrayResource(imageBytes) {
            @Override
            public String getFilename() {
                return originalName;
            }
        });
        if (foodId != null && !foodId.isBlank()) {
            body.add("food_id", foodId);
        }

        HttpEntity<MultiValueMap<String, Object>> request = new HttpEntity<>(body, headers);

        log.info("POST {}/api/vision/estimate-volume (food_id={})", baseUrl, foodId);

        ResponseEntity<Map> response = restTemplate.postForEntity(
                baseUrl + "/api/vision/estimate-volume",
                request,
                Map.class);

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
