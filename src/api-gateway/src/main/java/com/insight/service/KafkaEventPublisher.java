package com.insight.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

import java.util.Map;

/**
 * Publishes meal analysis events to Kafka for auditing and analytics.
 */
@Component
public class KafkaEventPublisher {

    private static final Logger log = LoggerFactory.getLogger(KafkaEventPublisher.class);

    private final KafkaTemplate<String, String> kafkaTemplate;
    private final ObjectMapper objectMapper;
    private final String topic;

    public KafkaEventPublisher(
            KafkaTemplate<String, String> kafkaTemplate,
            @Value("${insight.kafka.topic.meal-analysis:meal-analysis-events}") String topic) {
        this.kafkaTemplate = kafkaTemplate;
        this.objectMapper = new ObjectMapper();
        this.topic = topic;
    }

    public void publishMealAnalysis(Map<String, Object> analysisResult) {
        try {
            String json = objectMapper.writeValueAsString(analysisResult);
            kafkaTemplate.send(topic, json);
            log.info("Published meal analysis event to topic: {}", topic);
        } catch (Exception e) {
            // Kafka failure should not break the pipeline
            log.warn("Failed to publish Kafka event: {}", e.getMessage());
        }
    }
}
