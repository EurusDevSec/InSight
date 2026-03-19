package com.insight.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.security.MessageDigest;
import java.time.Duration;
import java.util.HexFormat;
import java.util.Map;

/**
 * Redis caching for RAG advisory results.
 *
 * Cache key: SHA-256 hash of (food_name, carbs_g, glycemic_load,
 * glucose_level).
 * TTL: 1 hour (matching application.yml config).
 *
 * Task 4.4.2 — Redis caching cho kết quả frequent.
 */
@Service
public class CacheService {

    private static final Logger log = LoggerFactory.getLogger(CacheService.class);
    private static final String PREFIX = "insight:rag:";
    private static final Duration TTL = Duration.ofHours(1);

    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper objectMapper;

    public CacheService(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
        this.objectMapper = new ObjectMapper();
    }

    /**
     * Build a cache key from RAG request parameters.
     */
    public String buildKey(String foodName, double carbsG, double glycemicLoad, Double glucoseLevel) {
        String raw = String.format("%s|%.1f|%.1f|%s",
                foodName, carbsG, glycemicLoad,
                glucoseLevel != null ? String.format("%.0f", glucoseLevel) : "null");
        try {
            byte[] hash = MessageDigest.getInstance("SHA-256").digest(raw.getBytes());
            return PREFIX + HexFormat.of().formatHex(hash).substring(0, 16);
        } catch (Exception e) {
            return PREFIX + raw.hashCode();
        }
    }

    /**
     * Get cached RAG result.
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> get(String key) {
        try {
            String json = redisTemplate.opsForValue().get(key);
            if (json != null) {
                log.debug("Cache HIT: {}", key);
                return objectMapper.readValue(json, new TypeReference<>() {
                });
            }
        } catch (Exception e) {
            log.warn("Cache read error: {}", e.getMessage());
        }
        return null;
    }

    /**
     * Store RAG result in cache.
     */
    public void put(String key, Map<String, Object> value) {
        try {
            String json = objectMapper.writeValueAsString(value);
            redisTemplate.opsForValue().set(key, json, TTL);
            log.debug("Cache PUT: {}", key);
        } catch (Exception e) {
            log.warn("Cache write error: {}", e.getMessage());
        }
    }

    /**
     * Check if Redis is available.
     */
    public boolean isAvailable() {
        try {
            redisTemplate.getConnectionFactory().getConnection().ping();
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
