package com.insight.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.StringRedisTemplate;

/**
 * Redis configuration with graceful degradation.
 *
 * Task 4.4.2 — If Redis is unavailable, the CacheService methods
 * will catch exceptions and skip caching (pipeline still works).
 */
@Configuration
public class RedisConfig {

    private static final Logger log = LoggerFactory.getLogger(RedisConfig.class);

    @Bean
    public StringRedisTemplate stringRedisTemplate(RedisConnectionFactory connectionFactory) {
        StringRedisTemplate template = new StringRedisTemplate();
        template.setConnectionFactory(connectionFactory);
        try {
            connectionFactory.getConnection().ping();
            log.info("Redis connected successfully");
        } catch (Exception e) {
            log.warn("Redis not available — caching disabled: {}", e.getMessage());
        }
        return template;
    }
}
