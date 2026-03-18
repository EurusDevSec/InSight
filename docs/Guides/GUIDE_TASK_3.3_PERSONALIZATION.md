# 📖 HƯỚNG DẪN CHI TIẾT TASK 3.3: PERSONALIZATION

> **Assignee**: Hoàng (chính), Hoài
> **Sprint**: Sprint 8 - Cá nhân hóa
> **Tiền đề**: Task 3.2 (RAG Pipeline ✅ — rag_pipeline module, 56 tests)
> **Tham chiếu**: [TASK_3.3](../Tasks/TASK_3.3_PERSONALIZATION.md) | [plan.md](../plan.md)
> **Cập nhật**: 11/03/2026

---

## Bức tranh tổng thể

```
┌─────────────────────────────────────────────────────────────────────┐
│  Task 3.1  Knowledge Base ✅  →  Task 3.2  RAG Pipeline ✅         │
│                                                                     │
│  ► Task 3.3  PERSONALIZATION  ◄◄◄  BẠN ĐANG Ở ĐÂY               │
│    │                                                                │
│    │  3 pillars:                                                   │
│    │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          │
│    │  │  Emergency   │ │   Clinical   │ │  Grounding   │          │
│    │  │  Detection   │ │    Rules     │ │  Validation  │          │
│    │  │              │ │              │ │              │          │
│    │  │ Rule of 15   │ │ meal_dose =  │ │ Anti-hallu-  │          │
│    │  │ Glucagon     │ │ carbs / ICR  │ │ cination     │          │
│    │  │ DKA protocol │ │ correction = │ │ Source check  │          │
│    │  │              │ │ (gl-tgt)/CF  │ │              │          │
│    │  └──────────────┘ └──────────────┘ └──────────────┘          │
│    │                                                                │
│    └───► Task 4.x: Integration (Flutter + gRPC + E2E)             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Module Structure

```
src/rag-service/
├── personalization/            # Task 3.3 ✅
│   ├── __init__.py             # Exports: EmergencyDetector, ClinicalRules, GroundingValidator
│   ├── emergency.py            # Emergency detection & protocols
│   ├── clinical_rules.py       # Rule-based insulin dose engine
│   └── grounding.py            # Strict RAG grounding validator
│
├── tests/
│   └── test_personalization.py # 48 tests (Task 3.3)
```

---

## Chi tiết Implementation

### 3.3.1 Dynamic Prompt (glucose + thuốc)

Đã tích hợp trong `PromptBuilder` (Task 3.2):

- **Glucose level** → chọn system prompt (normal vs emergency)
- **Medications** → inject vào patient context section
- **ICR + CF** → inject cho insulin calculation context
- **Diabetes type** → adjust recommendation framing

6 glucose classifications:
| Level | Range | Prompt Behavior |
|-------|-------|----------------|
| SEVERE_HYPO | < 54 | Emergency prompt, glucagon protocol |
| HYPO | 54-69 | Emergency prompt, Rule of 15 |
| NORMAL | 70-180 | Standard advisory prompt |
| HIGH | 181-250 | Standard + correction dose context |
| VERY_HIGH | 251-300 | Standard + ketone check advice |
| CRITICAL_HIGH | > 300 | Emergency prompt, DKA protocol |

### 3.3.2 Emergency Detection & Protocols

**File**: `personalization/emergency.py`

`EmergencyDetector.evaluate(glucose_mg_dl) → EmergencyProtocol`

**Protocols:**

| Protocol               | Glucose | Severity | Actions                                   |
| ---------------------- | ------- | -------- | ----------------------------------------- |
| `glucagon`             | < 54    | CRITICAL | Glucagon, call 115/911, recovery position |
| `rule_of_15`           | 54-69   | MODERATE | 15g fast-acting carbs, recheck 15min      |
| `dka`                  | > 300   | CRITICAL | Check ketones, hydrate, seek ER           |
| `very_high_correction` | 251-300 | SEVERE   | Check ketones, correction insulin         |
| `high_correction`      | 181-250 | MILD     | Correction dose, low-GI foods             |
| `normal`               | 70-180  | NONE     | Continue routine                          |

**Key design**: `EmergencyProtocol` is a frozen dataclass:

```python
@dataclass(frozen=True)
class EmergencyProtocol:
    is_emergency: bool
    severity: EmergencySeverity
    glucose_level: GlucoseLevel | None
    protocol_name: str
    immediate_actions: list[str]
    follow_up_actions: list[str]
    call_emergency_services: bool
```

### 3.3.3 Strict RAG Grounding (anti-hallucination)

**File**: `personalization/grounding.py`

`GroundingValidator.validate(llm_response, retrieved_chunks) → GroundingResult`

**Strategy:**

1. Extract medical claims from LLM response (regex: dosing, units, recommendations)
2. For each claim, check keyword overlap with retrieved chunks (≥ 40% significant words)
3. Score = grounded_claims / total_claims
4. `is_grounded = score >= min_grounding_score` (default 0.5)

**GroundingResult:**

```python
@dataclass
class GroundingResult:
    is_grounded: bool         # Overall grounding verdict
    grounding_score: float    # 0.0 - 1.0
    matched_sources: list[str]
    ungrounded_claims: list[str]  # Claims NOT supported by chunks
    explanation: str
```

### 3.3.4 Clinical Rules Engine

**File**: `personalization/clinical_rules.py`

`ClinicalRules.calculate_insulin(request, glucose_level) → InsulinRecommendation`

**ADA 2024 Formulas:**

- $\text{meal\_dose} = \frac{\text{carbs\_g}}{\text{ICR}}$
- $\text{correction\_dose} = \max\left(0, \frac{\text{glucose} - \text{target}}{\text{CF}}\right)$
- $\text{total} = \text{meal\_dose} + \text{correction\_dose}$

**Safety guards:**

- **DoseLimit**: max_meal=25U, max_correction=10U, max_total=30U
- **Hypo block**: NO insulin when glucose < 70 mg/dL
- **Missing data**: Returns None when ICR or carbs unavailable

---

## Tests

**48 tests** trong `tests/test_personalization.py`:

| Test Class             | Count | Covers                                               |
| ---------------------- | ----- | ---------------------------------------------------- |
| TestEmergencyDetector  | 14    | All 6 protocols, boundaries, pre-classified          |
| TestClinicalRules      | 12    | Meal dose, correction, hypo block, dose cap, helpers |
| TestGroundingValidator | 6     | Grounded, hallucinated, partial, empty               |
| TestClinicalScenarios  | 7     | Pho bo, com tam, hypo, DKA, Type 1, gestational      |

Chạy tests:

```bash
cd src/rag-service
python -m pytest tests/test_personalization.py --tb=short -q
# Expected: 48 passed
```

---

## Clinical Scenario Examples

### Scenario 1: Normal Glucose + Pho Bo

```
Input:  glucose=110, carbs=45g, ICR=10, CF=50
Result: meal=4.5U, correction=0U, total=4.5U
Emergency: False
```

### Scenario 2: High Glucose + Com Tam

```
Input:  glucose=230, carbs=75g, ICR=12, CF=40
Result: meal=6.2U, correction=2.8U, total=9.0U
Emergency: False, severity=MILD
```

### Scenario 3: Hypoglycemia Before Meal

```
Input:  glucose=58
Result: total=0U (NO INSULIN)
Emergency: True, protocol=rule_of_15
Action: 15g fast-acting carb, recheck 15min
```

### Scenario 4: DKA Risk

```
Input:  glucose=320
Result: Emergency=True, protocol=dka
Action: Check ketones, call ER, hydrate
```

---

## Verify Checklist

- [x] Dynamic prompt thay đổi dựa trên glucose level + thuốc
- [x] Giao thức khẩn cấp: phát hiện hạ đường huyết → hướng dẫn cấp cứu
- [x] Strict RAG Grounding: response chỉ từ chunks hợp lệ (chống hallucination)
- [x] Test scenarios lâm sàng pass (glucose thấp/bình thường/cao)
