# Context: Skill Normalizer Service — MockAI

> **Agent context document**: mô tả theo hướng **kiến trúc + trách nhiệm + interface**, không phải implementation chi tiết.

---

## Purpose

The Skill Normalizer là một domain service thuộc tầng **Application/Domain** trong MockAI, chịu trách nhiệm chuyển đổi các kỹ năng thô trích xuất từ CV ứng viên và Job Descriptions thành một biểu diễn chuẩn hoá (canonical representation).

Mục tiêu duy nhất của service này là **chuẩn hoá tên kỹ năng** — không đánh giá ứng viên, không so khớp CV với JD. Kết quả đầu ra được tiêu thụ bởi `JobMatchingService` (Phase 3) và `SkillGapService` (Phase 4).

**Ví dụ chuẩn hoá:**

```text
FastAPI  →  Backend Development
Spring Boot  →  Backend Development
Express.js   →  Backend Development
```

```text
Docker          →  Containerization
Docker Compose  →  Containerization
Container Engine  →  Containerization
```

---

## Responsibilities

Service này phải:

* Chuẩn hoá tên kỹ năng kỹ thuật.
* Loại bỏ bất nhất về định dạng.
* Giải quyết alias và viết tắt.
* Ánh xạ kỹ năng thô thành canonical skills.
* Trả về confidence score và metadata ánh xạ.
* Cache kết quả từ AI để tránh gọi Gemini trùng lặp.
* **Tuyệt đối không** thực hiện so khớp candidate–job.

Service phải ưu tiên xử lý deterministic. AI chỉ được dùng làm **fallback cuối cùng** khi mapping dạng dictionary thất bại.

---

## Processing Pipeline

```text
Raw Skill
    │
    ▼
[1] Text Cleaning
    │
    ▼
[2] Alias Resolution
    │
    ▼
[3] Canonical Mapping (dictionary)
    │
    ▼ (nếu không tìm thấy)
[4] AI Fallback — Gemini 2.5 Flash Lite
    │
    ▼
Normalized Skill (NormalizedSkill schema)
```

---

## Processing Steps

### 1. Text Cleaning

Chuẩn hoá input bằng cách:

* lowercase
* trim whitespace
* loại bỏ dấu câu và ký tự đặc biệt
* normalize unicode
* collapse khoảng trắng thừa

```
"Docker (Basic)"  →  "docker"
"  React.JS  "    →  "reactjs"
```

### 2. Alias Resolution

Chuyển đổi alias phổ biến thành tên chuẩn.

```
js             → javascript
ts             → typescript
postgres       → postgresql
docker compose → docker
k8s            → kubernetes
```

Alias được load từ file tĩnh `app/static/aliases.json`. Không hardcode trong code.

### 3. Canonical Mapping

Ánh xạ tên đã chuẩn hoá sang khái niệm kỹ thuật canonical.

```
docker       → Containerization
fastapi      → Backend Development
redis        → Caching
postgresql   → SQL Database
tensorflow   → Machine Learning
```

Canonical mappings được load từ `app/static/canonical_mappings.json`. Không hardcode.

### 4. AI Fallback — Gemini 2.5 Flash Lite

Nếu không tìm thấy canonical mapping, service gọi **Gemini 2.5 Flash Lite** để phân loại kỹ năng.

**Lý do chọn Gemini 2.5 Flash Lite:**
- Đủ nhanh cho luồng xử lý đồng bộ trong request cycle
- Chi phí thấp phù hợp với khối lượng phân loại kỹ năng lớn
- Đủ năng lực cho tác vụ phân loại kỹ năng có structured JSON output

**Input ví dụ:**

```
LangGraph
```

**Expected output từ Gemini:**

```json
{
    "canonical": "LLM Framework",
    "category": "Artificial Intelligence",
    "confidence": 0.88
}
```

**Ràng buộc:**
- Prompt phải được versioned, lưu trong `prompts/skill_classify_v1.txt`.
- Không hardcode prompt bên trong class service.
- Gemini **phải trả về structured JSON**. Không parse natural language.
- Kết quả phải được cache ngay sau khi nhận được.

---

## Output Model (Response Schema)

```python
# app/schemas/response/skill_normalizer_response.py
from pydantic import BaseModel, Field
from typing import Literal


class NormalizedSkill(BaseModel):
    raw: str = Field(..., description="Original skill string as extracted from CV or JD.")
    normalized: str = Field(..., description="Cleaned, lowercased version before canonical mapping.")
    canonical: str = Field(..., description="Final canonical skill name.")
    category: str = Field(..., description="High-level skill category (e.g., DevOps, Backend Development).")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the mapping.")
    mapping_method: Literal["dictionary", "alias", "ai", "cached"] = Field(
        ..., description="Method used to produce this mapping."
    )
```

**Possible mapping methods:**

| Value | Ý nghĩa |
|---|---|
| `dictionary` | Tìm thấy trong `canonical_mappings.json` |
| `alias` | Đã resolve qua `aliases.json` rồi map |
| `ai` | Phân loại bởi Gemini 2.5 Flash Lite |
| `cached` | Trả từ cache, không gọi Gemini |

---

## Non-Goals

Skill Normalizer **tuyệt đối không**:

* So sánh CV với JD
* Tính matching score
* Generate learning roadmap
* Sinh câu hỏi phỏng vấn
* Đánh giá năng lực ứng viên

Các trách nhiệm đó thuộc về `JobMatchingService`, `SkillGapService`, `LearningRoadmapService`.

---

## Architecture

Tuân theo **Clean/Layered Architecture** của MockAI:

```text
app/services/skill_normalizer/

    interfaces/
        skill_normalizer_service.py       ← typing.Protocol (public contract)

    impl/
        skill_normalizer_service_impl.py  ← Orchestrates full pipeline

    cleaner.py                            ← Text normalization
    alias_resolver.py                     ← Load + resolve aliases.json
    canonical_mapper.py                   ← Load + map canonical_mappings.json
    ai_mapper.py                          ← Gemini 2.5 Flash Lite fallback
    cache.py                              ← Cache AI results

    prompts/
        skill_classify_v1.txt             ← Versioned Gemini prompt

app/static/
    aliases.json                          ← Alias dictionary
    canonical_mappings.json               ← Canonical mapping dictionary
```

---

## Public Interface

Định nghĩa bằng `typing.Protocol` theo chuẩn MockAI:

```python
# app/services/interfaces/skill_normalizer_service.py
from typing import Protocol
from app.schemas.response.skill_normalizer_response import NormalizedSkill


class ISkillNormalizerService(Protocol):

    async def normalize(self, skill: str) -> NormalizedSkill:
        """Normalize a single raw skill string into a canonical representation.

        Args:
            skill (str): Raw skill string extracted from a CV or JD.

        Returns:
            NormalizedSkill: Canonical name, category, confidence, mapping method.
        """
        ...

    async def normalize_batch(self, skills: list[str]) -> list[NormalizedSkill]:
        """Normalize a list of raw skill strings.

        Args:
            skills (list[str]): Raw skill strings.

        Returns:
            list[NormalizedSkill]: List of normalized outputs.
        """
        ...
```

Interface này phải ổn định kể cả khi implementation bên trong thay đổi.

**Các implementation tương lai có thể thay thế:**
* ESCO ontology
* O*NET taxonomy
* Knowledge Graph
* Embedding similarity
* Hybrid semantic retrieval

mà không ảnh hưởng đến `JobMatchingService` hay các consumer khác.

---

## Downstream Consumers

| Consumer | Phase | Usage |
|---|---|---|
| `JobMatchingService` | Phase 3 | Normalize skills từ CandidateProfile và JD trước khi tính match score |
| `SkillGapService` | Phase 4 | Normalize skills trước khi phân tích gap |
| `CareerRecommendationService` | Phase 4 | Normalize skill sets trước khi sinh career paths |

`ISkillNormalizerService` được inject qua FastAPI Dependency Injection.

---

## Design Principles

* **Single Responsibility**: chỉ normalize skills, không matching, không evaluation.
* **Deterministic-first**: ưu tiên dictionary mapping trước LLM.
* **AI as last resort**: Gemini 2.5 Flash Lite chỉ được gọi khi dictionary và alias đều thất bại.
* **Configuration-driven**: `aliases.json` và `canonical_mappings.json` là external config, không hardcode.
* **Prompt versioning**: mọi prompt lưu trong `prompts/` với suffix version (`_v1`, `_v2`, ...).
* **Cache AI results**: tránh gọi Gemini trùng lặp cho cùng một kỹ năng.
* **Stateless**: normalization không phụ thuộc vào request trước (ngoại trừ cache lookup).
* **Async**: tất cả method đều phải là `async def` để align với FastAPI async runtime.

---

## Acceptance Criteria

* [ ] Nhận raw skills từ cả CV (CandidateProfile) và JD.
* [ ] Trả về canonical representation cho mỗi skill.
* [ ] Xử lý đúng alias và bất nhất định dạng.
* [ ] Gọi Gemini 2.5 Flash Lite **chỉ khi** deterministic mapping thất bại.
* [ ] Trả về structured metadata: confidence score + mapping method.
* [ ] Cache kết quả AI mapping để tránh gọi Gemini trùng lặp.
* [ ] Expose `ISkillNormalizerService` interface dùng được bởi `JobMatchingService` và các module AI tương lai.
* [ ] Prompt phải versioned, lưu ngoài service class.
* [ ] Mọi method đều là `async def`.
