# 📖 HƯỚNG DẪN CHI TIẾT TASK 3.2: RAG PIPELINE

> **Assignee**: Hoàng (chính), Việt, Hoài
> **Sprint**: Sprint 7 - RAG Pipeline
> **Tiền đề**: Task 3.1 (Knowledge Base ✅ — 26 docs → 46 chunks → Milvus)
> **Tham chiếu**: [TASK_3.2](../Tasks/TASK_3.2_RAG_PIPELINE.md) | [plan.md](../plan.md)
> **Cập nhật**: 11/03/2026

---

## Bức tranh tổng thể

```
┌─────────────────────────────────────────────────────────────────────┐
│  Task 3.1  Knowledge Base ✅                                        │
│  (26 docs → 46 chunks → Milvus, hybrid search ready)              │
│                                                                     │
│  ► Task 3.2  RAG PIPELINE  ◄◄◄  BẠN ĐANG Ở ĐÂY                  │
│    │                                                                │
│    │  Mục tiêu: Orchestrate query → retrieve → generate           │
│    │  Input: AdviceRequest (meal, GL, patient context)             │
│    │  Output: AdviceResponse (advice, insulin rec, sources)        │
│    │                                                                │
│    │  ⚡ THAY ĐỔI SO VỚI PLAN GỐC:                               │
│    │  Stack: Python FastAPI + OpenAI SDK (Gemini API)           │
│    │  LLM: Gemini 2.0 Flash (free tier, OpenAI-compatible)     │
│    │  KB + embedding + Milvus đều Python, tối ưu               │
│    │  LLM client: OpenAI-compatible (Gemini, Ollama, vLLM)     │
│    │                                                                │
│    │  Pipeline flow:                                               │
│    │  AdviceRequest → SearchService.search()                       │
│    │                → PromptBuilder.build_prompts()                │
│    │                → LLMClient.generate_json()                    │
│    │                → Rule-based insulin calc                       │
│    │                → AdviceResponse                                │
│    │                                                                │
│    └───► Task 3.3: Personalization (emergency, grounding)          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Module Structure

```
src/rag-service/
├── knowledge_base/          # Task 3.1 ✅
│   ├── schemas.py           # MedicalDocument, SearchResult, etc.
│   ├── chunking.py          # ChunkingService
│   ├── embedding.py         # EmbeddingService (all-MiniLM-L6-v2)
│   └── search.py            # SearchService (hybrid vector + BM25)
│
├── rag_pipeline/            # Task 3.2 ✅
│   ├── __init__.py          # Exports: LLMClient, PromptBuilder, RAGService
│   ├── schemas.py           # AdviceRequest, AdviceResponse, PatientContext
│   ├── llm_client.py        # OpenAI-compatible LLM client
│   ├── prompt_builder.py    # System/user prompt construction
│   └── rag_service.py       # Main RAG orchestrator
│
├── tests/
│   ├── test_knowledge_base.py   # 50 tests (Task 3.1)
│   └── test_rag_pipeline.py     # 56 tests (Task 3.2)
│
└── main.py                  # FastAPI: POST /api/rag/advise, GET /health
```

---

## Chi tiết Implementation

### 3.2.1 LLM Client (Gemini API)

**File**: `rag_pipeline/llm_client.py`

Sử dụng Python `openai` SDK với Gemini API (OpenAI-compatible endpoint):

```python
# Hỗ trợ: Ollama (default), OpenAI, vLLM, LM Studio
client = LLMClient(
    model="gpt-3.5-turbo",
    base_url="http://localhost:11434/v1",  # Ollama
    api_key="not-needed",
)
client.connect()
result = client.generate_json(system_prompt, user_prompt)
```

**Tính năng:**

- `generate()`: Text response
- `generate_json()`: JSON response với fallback (strip markdown fences, wrap raw text)
- Lazy connection: `connect()` phải gọi trước `generate()`

### 3.2.2 Prompt Builder

**File**: `rag_pipeline/prompt_builder.py`

4 phần trong user prompt:

1. **Patient Context**: glucose, diabetes type, medications, ICR, CF
2. **Meal Information**: tên món, carbs, glycemic load
3. **Medical Guidelines**: numbered chunks từ Milvus retrieval
4. **Question**: insulin dosing request (hoặc emergency protocol nếu nguy hiểm)

**Glucose Classification** (6 levels):

| Level         | Range (mg/dL) | Emergency?    |
| ------------- | ------------- | ------------- |
| SEVERE_HYPO   | < 54          | ✅ Glucagon   |
| HYPO          | 54-69         | ✅ Rule of 15 |
| NORMAL        | 70-180        | ❌            |
| HIGH          | 181-250       | ❌            |
| VERY_HIGH     | 251-300       | ❌            |
| CRITICAL_HIGH | > 300         | ✅ DKA risk   |

### 3.2.3 RAG Service (Orchestrator)

**File**: `rag_pipeline/rag_service.py`

Core method: `advise(request: AdviceRequest) → AdviceResponse`

Pipeline:

1. **Classify glucose** → determine if emergency
2. **Retrieve** → SearchService.search() (emergency: add category filter)
3. **Build prompts** → system (normal vs emergency) + user (augmented with chunks)
4. **Generate** → LLMClient.generate_json()
5. **Calculate insulin** (rule-based, NOT from LLM):
   - `meal_dose = carbs / ICR`
   - `correction_dose = max(0, (glucose - target) / CF)`
6. **Build emergency alert** nếu cần
7. **Assess confidence** (HIGH/MEDIUM/LOW base on retrieval quality + data completeness)

### 3.2.4 API Endpoint

**File**: `main.py`

```
POST /api/rag/advise
  Body: AdviceRequest (JSON)
  Response: AdviceResponse (JSON)

GET /health
  Response: {"status": "ok", "service": "rag-service", "version": "0.3.0"}
```

**Environment variables:**

- `LLM_MODEL`, `LLM_BASE_URL`, `LLM_API_KEY`
- `LLM_MAX_TOKENS`, `LLM_TEMPERATURE`
- `MILVUS_HOST`, `MILVUS_PORT`
- `RAG_TOP_K`

---

## Schemas

### AdviceRequest

```json
{
  "meal_description": "Pho bo",
  "glycemic_load": 16.0,
  "carbs_g": 45.0,
  "patient_context": {
    "current_glucose_mg_dl": 150,
    "diabetes_type": "type_2",
    "medications": ["metformin 500mg"],
    "insulin_to_carb_ratio": 10,
    "correction_factor": 50,
    "target_glucose_mg_dl": 120
  }
}
```

### AdviceResponse

```json
{
  "advice": "Based on your current glucose...",
  "insulin_recommendation": {
    "meal_dose_units": 4.5,
    "correction_dose_units": 0.6,
    "total_units": 5.1,
    "calculation_details": "Meal: 45g/10 = 4.5U\nCorrection: ..."
  },
  "emergency_alert": null,
  "glucose_classification": "normal",
  "sources": [
    {"chunk_id": "ada_bolus__chunk_0", "source": "ADA 2024", ...}
  ],
  "confidence": "high",
  "disclaimer": "This is educational information only..."
}
```

---

## Tests

**56 tests** trong `tests/test_rag_pipeline.py`:

| Test Class                  | Count | Covers                                     |
| --------------------------- | ----- | ------------------------------------------ |
| TestGlucoseClassification   | 14    | 6 levels + boundaries + None               |
| TestEmergencyDetection      | 7     | 3 emergency + 4 non-emergency              |
| TestPromptBuilder           | 8     | System/user prompts, chunks, context       |
| TestLLMClient               | 3     | JSON parse, connect, error handling        |
| TestInsulinCalculation      | 10    | Meal dose, correction, hypo, missing data  |
| TestEmergencyAlert          | 5     | Severe hypo, moderate hypo, DKA, normal    |
| TestConfidenceAssessment    | 4     | HIGH/MEDIUM/LOW based on data completeness |
| TestRAGServiceOrchestration | 8     | Full pipeline mocked, sources, disclaimer  |
| TestSchemas                 | 4     | Pydantic validation, serialization         |

Chạy tests:

```bash
cd src/rag-service
python -m pytest tests/test_rag_pipeline.py --tb=short -q
# Expected: 56 passed
```

---

## Chạy service (development)

```bash
cd src/rag-service

# Cần Milvus + Ollama running
docker compose -f ../../infra/docker/docker-compose.yml up -d milvus

# Start Ollama (nếu dùng local LLM)
ollama serve

# Start RAG service
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

---

## Verify Checklist

- [x] LLM Client setup → Python OpenAI-compatible (Gemini API)
- [x] RAG pipeline: query → retrieve chunks → generate response
- [x] API endpoint `POST /api/rag/advise` hoạt động
- [x] Response quality: 56 test scenarios pass (>10 required)
