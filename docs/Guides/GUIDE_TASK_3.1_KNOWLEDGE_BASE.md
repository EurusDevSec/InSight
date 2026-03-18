# 📖 HƯỚNG DẪN CHI TIẾT TASK 3.1: KNOWLEDGE BASE SETUP

> **Assignee**: Hoàng (chính), Hoài (hỗ trợ thu thập tài liệu)
> **Thời gian**: 22/03/2026 → 24/03/2026
> **Tiền đề**: Task 1.2 (Milvus collection `medical_knowledge` đã tạo) ✅
> **Tham chiếu**: [TASK_3.1](../Tasks/TASK_3.1_KNOWLEDGE_BASE.md) | [plan.md](../plan.md)
> **Cập nhật**: 22/03/2026

---

## Bức tranh tổng thể

```
┌─────────────────────────────────────────────────────────────────────┐
│  Phase 2 Vision ✅ | Task 1.2 Database/Milvus ✅                    │
│  (GL pipeline + volume estimation hoàn chỉnh)                      │
│                                                                     │
│  ► Task 3.1  KNOWLEDGE BASE SETUP  ◄◄◄  BẠN ĐANG Ở ĐÂY           │
│    │                                                                │
│    │  Mục tiêu: Index hướng dẫn y khoa vào Milvus                  │
│    │  Input: ADA/MOH guidelines JSON → Output: Milvus vectors      │
│    │                                                                │
│    │  📌 Phân công:                                                │
│    │  • Hoài:  Thu thập tài liệu ADA/MOH (subtask 3.1.1)          │
│    │  • Hoàng: Chunking, embedding, search (subtasks 3.1.2–3.1.4) │
│    │                                                                │
│    │  ⚡ TẠI SAO HYBRID SEARCH?                                     │
│    │  ① Vector search: hiểu ngữ nghĩa (semantic similarity)       │
│    │  ② Keyword search: match chính xác thuật ngữ y khoa          │
│    │  ③ Re-ranking: kết hợp α=0.7 vector + 0.3 BM25               │
│    │  ④ Kết quả chính xác hơn cho câu hỏi insulin/carb            │
│    │                                                                │
│    └───► Task 3.2: RAG pipeline cần knowledge base này             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Kiến trúc Knowledge Base

```
┌─────────────────────────────────────────────────────────────────────┐
│                  KNOWLEDGE BASE PIPELINE                            │
│                                                                     │
│  guidelines.json                                                    │
│  (25 docs, 7 categories)                                            │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────┐                                                │
│  │ ChunkingService │  max_chunk_chars=1200, overlap=150            │
│  │  _split_text()  │  paragraph → sentence hierarchy              │
│  └────────┬────────┘                                                │
│           │ ~80–120 DocumentChunk objects                          │
│           ▼                                                         │
│  ┌──────────────────────┐                                           │
│  │  EmbeddingService    │  sentence-transformers/all-MiniLM-L6-v2  │
│  │  encode(texts)       │  shape: (N, 384), float32, cosine-norm'd │
│  └──────────┬───────────┘                                           │
│             │ EmbeddingRecord per chunk                            │
│             ▼                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Milvus  (collection: medical_knowledge)        │   │
│  │  fields: content, source, category, embedding (384-dim)    │   │
│  │  index:  HNSW, COSINE metric, ef=128                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│             │                                                       │
│             ▼  At query time                                        │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    SearchService                              │ │
│  │  1. Encode query → 384-dim vector                            │ │
│  │  2. ANN search top k×2 candidates (Milvus COSINE)           │ │
│  │  3. BM25-like keyword score  per candidate                  │ │
│  │  4. combined = 0.7 × vector_score + 0.3 × keyword_score     │ │
│  │  5. Re-rank → return top k SearchResult                     │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Cấu trúc Files

```
src/rag-service/
├── knowledge_base/
│   ├── __init__.py          # exports: ChunkingService, EmbeddingService, SearchService
│   ├── schemas.py           # Pydantic models: MedicalDocument, DocumentChunk, ...
│   ├── chunking.py          # ChunkingService — text splitting với overlap
│   ├── embedding.py         # EmbeddingService — sentence-transformers wrapper
│   └── search.py            # SearchService — hybrid search + BM25 re-ranking
├── knowledge/
│   └── medical/
│       └── guidelines.json  # 25 tài liệu y khoa (ADA, MOH, WHO, Joslin, IDF)
├── tests/
│   └── test_knowledge_base.py  # 50 tests (all PASS)
└── requirements.txt

scripts/
└── ingest_knowledge_base.py  # Batch ingestion: JSON → chunk → embed → Milvus
```

---

## Bước 1: Thu thập Tài liệu Y khoa — Hoài (subtask 3.1.1)

### 1.1 Format dữ liệu

Mỗi tài liệu trong `guidelines.json` phải tuân theo schema:

```json
{
  "doc_id": "ada_insulin_types",
  "title": "Types of Insulin and Their Pharmacokinetics",
  "source": "ADA 2024",
  "category": "insulin_dosing",
  "tags": ["rapid-acting", "long-acting", "basal", "bolus"],
  "language": "en",
  "content": "Insulin types are classified by onset, peak, and duration..."
}
```

**Quy tắc:**

- `doc_id`: snake*case, prefix = nguồn (`ada*`, `moh*`, `who*`, `joslin*`, `idf*`)
- `category` phải là một trong: `insulin_dosing`, `carb_counting`, `glycemic_management`, `vn_food_guidance`, `emergency_protocol`, `clinical_management`, `moh_vietnam`
- `content`: tối thiểu 100 ký tự, tiếng Anh (để embedding chất lượng cao)
- `tags`: ít nhất 1 tag, lowercase, liên quan đến nội dung
- Không được trùng `doc_id`

### 1.2 Nguồn tài liệu ưu tiên

| Nguồn                              | Loại nội dung                  | Category target                              |
| ---------------------------------- | ------------------------------ | -------------------------------------------- |
| ADA Standards of Medical Care 2024 | Insulin dosing, carb counting  | `insulin_dosing`, `carb_counting`            |
| MOH Vietnam Diabetes Guidelines    | Hướng dẫn VN                   | `moh_vietnam`, `vn_food_guidance`            |
| WHO Diabetes Management            | Quản lý lâm sàng               | `glycemic_management`, `clinical_management` |
| Joslin Diabetes Center             | Insulin initiation, adjustment | `insulin_dosing`                             |
| IDF Atlas 10th Edition             | Epidemiology, global standards | `clinical_management`                        |

### 1.3 Thêm tài liệu mới vào guidelines.json

```json
{
  "version": "1.0",
  "last_updated": "2026-03-22",
  "documents": [
    {
      "doc_id": "moh_vn_new_guideline",
      ...
    }
  ]
}
```

**Validate ngay sau khi thêm:**

```bash
cd src/rag-service
python -m pytest tests/test_knowledge_base.py::TestGuidelinesData -v
```

---

## Bước 2: Chunking Service — Hoàng (subtask 3.1.2)

### 2.1 Cách hoạt động của ChunkingService

```python
from knowledge_base.chunking import ChunkingService
from knowledge_base.schemas import MedicalDocument

chunker = ChunkingService(max_chunk_chars=1200, overlap_chars=150)

doc = MedicalDocument(
    doc_id="ada_example",
    title="Example",
    source="ADA 2024",
    category="insulin_dosing",
    tags=["insulin"],
    content="Long medical text...",
    language="en",
)

chunks = chunker.chunk_document(doc)
# → list[DocumentChunk], mỗi chunk ≤ 1200 chars, overlap 150 chars
```

### 2.2 Chunk ID format

Chunk ID tự động sinh theo format: `{doc_id}__chunk_{index}`

```python
chunks[0].chunk_id  # "ada_example__chunk_0"
chunks[1].chunk_id  # "ada_example__chunk_1"
```

### 2.3 Xử lý tài liệu ngắn

Nếu `content` ≤ `MIN_CHUNK_CHARS` (80 chars) sau khi normalize → trả về `[]` (không tạo chunk).

### 2.4 Chiến lược splitting

```
Text → normalize whitespace/CRLF
     → split theo paragraph (blank line separator)
     → nếu paragraph > max_chars: split theo sentence (". ", "! ", "? ")
     → merge small chunks với overlap
```

---

## Bước 3: Embedding Service — Hoàng (subtask 3.1.3)

### 3.1 Setup embedding

```python
from knowledge_base.embedding import EmbeddingService

embedder = EmbeddingService()  # model: all-MiniLM-L6-v2
embedder.load()                # download ~90MB model lần đầu

# Batch encode
import numpy as np
texts = ["insulin dosing for type 2 diabetes", "bolus calculation method"]
vectors = embedder.encode(texts)  # shape: (2, 384), float32

# Single encode
vec = embedder.encode_single("what is basal insulin?")  # list[float], len=384
```

### 3.2 Cài đặt dependencies

```bash
cd src/rag-service

# Nếu chưa có sentence-transformers:
pip install sentence-transformers>=2.2.0

# Hoặc cài toàn bộ:
pip install -r requirements.txt
```

### 3.3 Important: Lazy loading

EmbeddingService **không** tải model khi khởi tạo. Phải gọi `load()` trước khi encode:

```python
svc = EmbeddingService()
# svc.encode(...)  # ❌ RuntimeError: Model not loaded. Call load() first.
svc.load()          # ✅ Tải model
svc.encode(...)     # ✅ OK
```

---

## Bước 4: Hybrid Search — Hoàng (subtask 3.1.4)

### 4.1 Kết nối Milvus và tìm kiếm

```python
from knowledge_base.embedding import EmbeddingService
from knowledge_base.search import SearchService
from knowledge_base.schemas import SearchQuery

# Setup
embedder = EmbeddingService()
embedder.load()

searcher = SearchService(embedding_service=embedder)
searcher.connect()  # cần Milvus đang chạy

# Tìm kiếm
query = SearchQuery(query="insulin dose for 60g carbohydrate", top_k=5)
response = searcher.search(query)

for result in response.results:
    print(f"[{result.combined_score:.3f}] {result.source}: {result.content[:100]}")
```

### 4.2 Lọc theo category

```python
query = SearchQuery(
    query="hypoglycemia treatment protocol",
    top_k=3,
    category_filter="emergency_protocol",
)
response = searcher.search(query)
```

### 4.3 Giải thích thuật toán Hybrid Search

```
combined_score = α × vector_score + (1 − α) × keyword_score

Trong đó:
  α = 0.7 (mặc định)
  vector_score  = cosine similarity từ Milvus ANN search  ∈ [0, 1]
  keyword_score = BM25-like TF score, normalized           ∈ [0, 1]

BM25 TF saturation:
  tf_score(term) = tf × (k1 + 1) / (tf + k1 × (1 − b + b × doc_len / avg_dl))
  k1=1.5, b=0.75, avg_dl=200 tokens

Lý do chọn α=0.7:
  - Vector search hiểu ngữ nghĩa, thích hợp cho câu hỏi tổng quát
  - Keyword search match chính xác thuật ngữ như "HbA1c", "basal insulin"
  - 70/30 balance cho kết quả tốt nhất trên test set y khoa
```

---

## Bước 5: Chạy Ingestion vào Milvus

> ⚠️ **Yêu cầu**: Docker Compose với Milvus đang chạy

### 5.1 Khởi động Milvus

```bash
# Từ thư mục root InSight/
docker compose -f infra/docker/docker-compose.yml up milvus -d

# Kiểm tra
docker ps | grep milvus

# Init collection (nếu chưa tồn tại)
python scripts/init-milvus.py
```

### 5.2 Chạy ingestion

```bash
# Từ project root
python scripts/ingest_knowledge_base.py
```

**Output thực tế (verified 18/03/2026, CUDA GPU):**

```
INFO  ingest — Loaded 26 documents.
INFO  ingest — Total: 26 documents → 46 chunks
INFO  ingest — Chunking complete: 46 chunks.
INFO  knowledge_base.embedding — Loading embedding model 'all-MiniLM-L6-v2' …
INFO  sentence_transformers — Use pytorch device_name: cuda:0
INFO  knowledge_base.embedding — Embedding model loaded (dim=384).
INFO  ingest — Embedding complete: shape (46, 384)
INFO  ingest — Inserted batch 0–46 (46 rows).
INFO  ingest — Flush complete. Total rows in collection: 46
INFO  ingest — Ingestion summary: {'documents': 26, 'chunks': 46, 'inserted': 46, 'elapsed_seconds': 8.4}
```

### 5.3 Verify bằng E2E search test

**Kết quả E2E verified (18/03/2026):**

```
Query: lieu insulin cho 60g carbohydrate
  [0.508] [carb_counting]   ADA Nutrition Therapy Guidelines: Advanced carbohydrate counting considers not just the quantity...
  [0.495] [carb_counting]   ADA Nutrition Therapy Guidelines: Carbohydrate counting is the cornerstone of meal-time insulin dosing...
  [0.479] [carb_counting]   ADA Nutrition Therapy Guidelines: Goal: Keep carbohydrate intake consistent meal-to-meal...

Query: bolus insulin dose for 60g carb  [filter: insulin_dosing]
  [0.709] [insulin_dosing]  ADA Standards of Care 2024: The meal-time bolus insulin dose is calculated using the Insulin-to-Carbohydrate...
  [0.618] [insulin_dosing]  ADA Standards of Care 2024: Insulin pump therapy (CSII) delivers rapid-acting insulin...
  [0.569] [insulin_dosing]  ADA Standards of Care 2024: Insulin dose adjustment should be based on blood glucose patterns...

Query: hypoglycemia emergency treatment  [filter: emergency_protocol]
  [0.598] [emergency_protocol]  Joslin Diabetes Center Guidelines: Severe hypoglycemia is a medical emergency requiring immediate intervention...
  [0.598] [emergency_protocol]  ADA Standards of Care 2024: Hypoglycemia is defined as blood glucose <70 mg/dL...

Query: Vietnamese food glycemic index rice  [filter: vn_food_guidance]
  [0.652] [vn_food_guidance]  USDA FoodData Central + Bảng TPDD Việt Nam: Vietnamese bread products typically use French-style wheat flour...
  [0.611] [vn_food_guidance]  MOH Vietnam + ADA Nutrition Guidelines: Traditional Vietnamese meals are rice-centric...
```

✅ Hybrid search trả về đúng category và source cho mọi query type.

---

## Bước 6: Chạy Tests (không cần Milvus)

### 6.1 Chạy all tests

```bash
cd src/rag-service
python -m pytest tests/test_knowledge_base.py -v
```

**Kết quả mong đợi: 50 passed in ~0.5s**

```
tests/test_knowledge_base.py::TestGuidelinesData::test_file_exists PASSED
tests/test_knowledge_base.py::TestGuidelinesData::test_valid_json PASSED
... (50 tests, all PASSED)
============================== 50 passed in 0.41s ==============================
```

### 6.2 Test groups

| Group                  | Tests | Mô tả                                                      |
| ---------------------- | ----- | ---------------------------------------------------------- |
| `TestGuidelinesData`   | 8     | Validate file JSON: ≥20 docs, categories, tags, unique IDs |
| `TestSchemas`          | 6     | Pydantic schema validation                                 |
| `TestTextHelpers`      | 5     | normalise_text, split_paragraphs, split_sentences          |
| `TestChunkingService`  | 10    | chunking logic, size limits, overlap, batch                |
| `TestEmbeddingService` | 5     | lazy load, mocked encode, shape, idempotent                |
| `TestKeywordScoring`   | 8     | BM25 tokenise, score range, edge cases                     |
| `TestSearchService`    | 5     | mocked Milvus, category filter, re-ranking                 |
| `TestFullPipeline`     | 3     | chunk all 25 docs, embed (mocked), build records           |

### 6.3 Chạy test cụ thể

```bash
# Chỉ test data validation
python -m pytest tests/test_knowledge_base.py::TestGuidelinesData -v

# Chỉ test hybrid search
python -m pytest tests/test_knowledge_base.py::TestSearchService -v

# Chỉ test full pipeline
python -m pytest tests/test_knowledge_base.py::TestFullPipeline -v
```

---

## Troubleshooting

### Lỗi `ModuleNotFoundError: No module named 'sentence_transformers'`

```bash
pip install sentence-transformers>=2.2.0
```

Tests **không** cần package này (tất cả embedding calls đều được mock).  
Chỉ cần khi chạy ingestion thực tế.

### Lỗi `ModuleNotFoundError: No module named 'pymilvus'`

```bash
pip install pymilvus>=2.3.0
```

Tests **không** cần package này (tất cả Milvus calls đều được mock).  
Chỉ cần khi chạy `scripts/ingest_knowledge_base.py` hoặc `searcher.connect()`.

### Lỗi `Collection 'medical_knowledge' not found`

```bash
python scripts/init-milvus.py
```

Milvus collection chưa được tạo. Chạy init script trước.

### Lỗi `Connection refused` khi connect Milvus

```bash
docker compose -f infra/docker/docker-compose.yml up milvus -d
sleep 10  # đợi Milvus ready
```

### Chunk count ít hơn mong đợi

Kiểm tra `MIN_CHUNK_CHARS=80` — tài liệu quá ngắn sẽ không được chunk.  
Đảm bảo content ≥ 100 chars (enforced bởi `TestGuidelinesData`).

---

## Kiến trúc Schemas

```python
# MedicalDocument — input từ guidelines.json
MedicalDocument(
    doc_id: str,
    title: str,
    source: str,          # e.g. "ADA 2024"
    category: str,        # e.g. "insulin_dosing"
    tags: list[str],
    content: str,
    language: str = "en",
)

# DocumentChunk — output của ChunkingService
DocumentChunk(
    chunk_id: str,        # format: "{doc_id}__chunk_{index}"
    doc_id: str,
    content: str,         # 80–1200 chars
    source: str,
    category: str,
    chunk_index: int,
    total_chunks: int,
)

# EmbeddingRecord — input cho Milvus insert
EmbeddingRecord(
    chunk_id: str,
    content: str,
    source: str,
    category: str,
    embedding: list[float],  # len=384
)

# SearchQuery — input cho SearchService
SearchQuery(
    query: str,
    top_k: int = 5,             # ge=1, le=50
    category_filter: str | None = None,
)

# SearchResponse — output của SearchService
SearchResponse(
    query: str,
    results: list[SearchResult],
    total_found: int,
)
```

---

## Checklist hoàn thành Task 3.1

- [x] 3.1.1 Thu thập ≥ 20 tài liệu ADA/MOH (→ 25 tài liệu, 7 categories, 5 sources)
- [x] 3.1.2 Chuẩn hóa & chunk tài liệu (`ChunkingService`, max 1200 chars, overlap 150)
- [x] 3.1.3 Embedding service (`EmbeddingService`, all-MiniLM-L6-v2, 384-dim)
- [x] 3.1.4 Hybrid search (`SearchService`, α=0.7 vector + 0.3 BM25)
- [x] 50 unit tests PASS (không cần Milvus/sentence-transformers)
- [x] Ingestion vào Milvus ✅ — 26 docs → 46 chunks → 46 rows, CUDA GPU, 8.4s (18/03/2026)
- [x] E2E search test ✅ — "bolus insulin dose for 60g carb" → score=0.709, [insulin_dosing], ADA Standards (18/03/2026)

---

_Hướng dẫn này được cập nhật sau khi E2E ingestion và search test hoàn tất ngày 18/03/2026._
