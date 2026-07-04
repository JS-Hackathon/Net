# Context: Confidence Scoring Engine — MockAI

> **Agent context document**: mô tả theo hướng **kiến trúc + trách nhiệm + interface**. `ConfidenceEngine` là một service thuần deterministic, **không phụ thuộc vào LLM**.

## Purpose

`ConfidenceEngine` là domain service thuộc tầng **Application/Domain** trong MockAI, chịu trách nhiệm tính toán confidence score cho mỗi kết quả requirement matching.

Mục tiêu của service **không phải** là xác định kỹ năng có match hay không — đó là trách nhiệm của `JobMatchingService`. Thay vào đó, `ConfidenceEngine` đánh giá **độ tin cậy của quyết định matching** bằng cách kết hợp các tín hiệu deterministic và evidence từ CV.

Confidence score được dùng để:

* Phân loại requirement status: `SATISFIED`, `PARTIAL`, `CLARIFICATION`, `MISSING`.
* Xác định các match cần làm rõ thêm.
* Ưu tiên missing skills trong Skill Gap Analysis (Phase 4).
* Cung cấp transparency cho ứng viên và HR về lý do hệ thống kết luận.

**Quy tắc bất biến:**
- Confidence score phải deterministic — cùng input phải luôn ra cùng output.
- Tuyệt đối **không dùng** self-reported confidence từ LLM (Gemini hay bất kỳ model nào).

---

## Responsibilities

`ConfidenceEngine` phải:

* Tính confidence cho từng `RequirementMatch` nhận từ `JobMatchingService`.
* Kết hợp nhiều evidence signals độc lập.
* Tạo ra scores có thể tái tạo (reproducible).
* Hoàn toàn độc lập với Gemini và mọi LLM provider.
* Expose interface ổn định, không thay đổi khi thuật toán bên trong evolve.

`ConfidenceEngine` tuyệt đối **không** được:

* Thực hiện semantic matching.
* Normalize skills — đó là trách nhiệm của `SkillNormalizerService`.
* Generate learning plans — đó là trách nhiệm của `LearningRoadmapService`.
* Sinh câu hỏi phỏng vấn.

---

## Input Schema

Engine nhận kết quả từ `JobMatchingService`.

```python
# app/schemas/internal/requirement_match.py
from pydantic import BaseModel, Field
from typing import Literal


class MatchEvidence(BaseModel):
    section: Literal["skills", "experience", "projects", "certifications", "summary"] = Field(
        ..., description="CV section where the evidence was found."
    )
    text: str = Field(..., description="Raw text snippet that supports the match.")


class RequirementMatch(BaseModel):
    requirement: str = Field(..., description="Canonical skill required by the JD.")
    matched_skill: str = Field(..., description="Canonical skill found in the candidate profile.")
    matching_method: Literal["canonical", "alias", "ai", "cached", "none"] = Field(
        ..., description="Method used by SkillNormalizerService to produce this match."
    )
    semantic_similarity: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Cosine similarity score if embedding-based matching was used. 0.0 if unavailable."
    )
    evidence: list[MatchEvidence] = Field(
        default_factory=list,
        description="List of evidence items extracted from the CV supporting this match."
    )
```

**Ví dụ input:**

```json
{
    "requirement": "Containerization",
    "matched_skill": "Docker",
    "matching_method": "canonical",
    "semantic_similarity": 0.92,
    "evidence": [
        {
            "section": "projects",
            "text": "Built containerized backend using Docker Compose."
        },
        {
            "section": "experience",
            "text": "Deployed microservices with Docker on AWS EC2."
        }
    ]
}
```

---

## Output Schema

```python
# app/schemas/response/confidence_result.py
from pydantic import BaseModel, Field
from app.enums.match_status import MatchStatus


class ConfidenceSignals(BaseModel):
    matching_method_score: float = Field(..., ge=0.0, le=1.0)
    evidence_strength_score: float = Field(..., ge=0.0, le=1.0)
    evidence_frequency_score: float = Field(..., ge=0.0, le=1.0)
    semantic_similarity_score: float = Field(..., ge=0.0, le=1.0)
    context_consistency_score: float = Field(..., ge=0.0, le=1.0)


class ConfidenceResult(BaseModel):
    requirement: str = Field(..., description="Canonical skill that was evaluated.")
    matched_skill: str = Field(..., description="Canonical skill found in candidate profile.")
    matching_method: str = Field(..., description="Method used to produce the match.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Final composite confidence score.")
    evidence_score: float = Field(..., ge=0.0, le=1.0, description="Aggregated evidence strength score.")
    semantic_score: float = Field(..., ge=0.0, le=1.0, description="Semantic similarity score (0.0 if unavailable).")
    status: MatchStatus = Field(..., description="Requirement satisfaction status derived from confidence.")
    signals: ConfidenceSignals = Field(..., description="Breakdown of individual scoring signals.")
    evidence: list[dict] = Field(..., description="Evidence items that supported this result.")
    reasoning: list[str] = Field(..., description="Human-readable explanation for the confidence score.")
```

**Ví dụ output:**

```json
{
    "requirement": "Containerization",
    "matched_skill": "Docker",
    "matching_method": "canonical",
    "confidence": 0.94,
    "evidence_score": 0.95,
    "semantic_score": 0.92,
    "status": "SATISFIED",
    "signals": {
        "matching_method_score": 1.00,
        "evidence_strength_score": 0.92,
        "evidence_frequency_score": 0.90,
        "semantic_similarity_score": 0.92,
        "context_consistency_score": 0.88
    },
    "evidence": [
        { "section": "projects", "text": "Built containerized backend using Docker Compose." },
        { "section": "experience", "text": "Deployed microservices with Docker on AWS EC2." }
    ],
    "reasoning": [
        "Exact canonical match: 'Docker' → 'Containerization'.",
        "Evidence found in 2 sections: projects, experience.",
        "High semantic similarity: 0.92.",
        "Context is consistent across CV sections."
    ]
}
```

> **Lưu ý**: `evidence_score`, `semantic_score`, và `evidence` là **bắt buộc** trong output — không phải optional. Đây là nền tảng để frontend hiển thị match explanation và để các downstream service (Skill Gap, Career Snapshot) có đủ dữ liệu audit.

---

## Enums

```python
# app/enums/match_status.py
from enum import Enum

class MatchStatus(str, Enum):
    SATISFIED = "SATISFIED"
    PARTIAL = "PARTIAL"
    CLARIFICATION = "CLARIFICATION"
    MISSING = "MISSING"
```

---

## Scoring Philosophy

Confidence được tính từ evidence deterministic, **không** từ LLM intuition.

Score phải trả lời câu hỏi:

> "Hệ thống có bao nhiêu bằng chứng để hỗ trợ quyết định matching này?"

Không phải:

> "AI tự tin bao nhiêu phần trăm?"

---

## Confidence Signals

Engine kết hợp 5 tín hiệu độc lập.

### 1. Matching Method Score

Đánh giá phương thức match được dùng bởi `SkillNormalizerService`.

| Matching Method | Base Score |
|---|---|
| `canonical` (Exact Canonical) | 1.00 |
| `alias` (Alias Mapping) | 0.95 |
| `ai` hoặc `cached` (AI Classification) | 0.75 |
| `none` (No Match) | 0.00 |

### 2. Evidence Strength Score

Đánh giá nguồn gốc của evidence trong CV.

| CV Section | Score |
|---|---|
| `skills` | 1.00 |
| `experience` | 0.95 |
| `projects` | 0.90 |
| `certifications` | 0.90 |
| `summary` | 0.60 |

Evidence xuất hiện ở nhiều section → tăng score.

### 3. Evidence Frequency Score

Số lần kỹ năng xuất hiện trong CV.

```text
Docker xuất hiện trong: skills + projects + experience
→ score cao hơn

Docker xuất hiện 1 lần duy nhất trong summary
→ score thấp hơn
```

### 4. Semantic Similarity Score

Nếu embedding-based matching được sử dụng, cosine similarity đóng góp vào confidence.

Nếu embedding không khả dụng trong MVP, signal này mặc định `0.0` và weight của nó tự động phân phối lại.

### 5. Context Consistency Score

Evidence phải nhất quán xuyên suốt CV.

```text
skills: Docker
projects: "Build and deploy containers with Docker Compose"
experience: "DevOps Engineer – containerized 12 microservices"
→ consistent → score cao

skills: Docker
summary: "Familiar with virtual machines and servers"
→ inconsistent signals → score giảm
```

---

## Scoring Formula

```text
confidence =
    w1 × matching_method_score
  + w2 × evidence_strength_score
  + w3 × evidence_frequency_score
  + w4 × semantic_similarity_score
  + w5 × context_consistency_score
```

**Default weights (MVP):**

```python
# app/core/config.py hoặc app/static/confidence_weights.json
CONFIDENCE_WEIGHTS = {
    "matching_method": 0.35,
    "evidence_strength": 0.25,
    "evidence_frequency": 0.15,
    "semantic_similarity": 0.15,
    "context_consistency": 0.10,
}
```

Weights **không được hardcode** bên trong service class. Phải load từ config hoặc external JSON để có thể calibrate mà không cần deploy lại code.

---

## Confidence Classification

Engine chuyển đổi numeric score thành `MatchStatus`.

| Score | Status | Ý nghĩa |
|---|---|---|
| ≥ 0.90 | `SATISFIED` | Kỹ năng được xác nhận rõ ràng |
| 0.70 – 0.89 | `PARTIAL` | Có bằng chứng nhưng chưa đủ mạnh |
| 0.40 – 0.69 | `CLARIFICATION` | Cần thêm thông tin để xác nhận |
| < 0.40 | `MISSING` | Không có bằng chứng đủ thuyết phục |

Thresholds phải configurable — không hardcode trong service class.

---

## Architecture

Tuân theo **Clean/Layered Architecture** của MockAI:

```text
app/services/confidence_engine/

    interfaces/
        confidence_engine_service.py      ← typing.Protocol (public contract)

    impl/
        confidence_engine_service_impl.py ← Orchestrates signal calculation

    signals/
        matching_method_scorer.py         ← Signal 1: method-based score
        evidence_strength_scorer.py       ← Signal 2: section-based score
        evidence_frequency_scorer.py      ← Signal 3: frequency-based score
        semantic_similarity_scorer.py     ← Signal 4: cosine similarity score
        context_consistency_scorer.py     ← Signal 5: consistency score

    classifier.py                         ← float → MatchStatus conversion

app/enums/
    match_status.py                       ← MatchStatus Enum

app/schemas/
    internal/
        requirement_match.py              ← Input schema
    response/
        confidence_result.py              ← Output schema

app/static/
    confidence_weights.json              ← Configurable scoring weights
    confidence_thresholds.json           ← Configurable classification thresholds
```

---

## Public Interface

Định nghĩa bằng `typing.Protocol` theo chuẩn MockAI:

```python
# app/services/interfaces/confidence_engine_service.py
from typing import Protocol
from app.schemas.internal.requirement_match import RequirementMatch
from app.schemas.response.confidence_result import ConfidenceResult


class IConfidenceEngineService(Protocol):

    async def score(self, match_result: RequirementMatch) -> ConfidenceResult:
        """Calculate a deterministic confidence score for a single requirement match.

        Args:
            match_result (RequirementMatch): Output from JobMatchingService containing
                matched skill, matching method, semantic similarity, and evidence.

        Returns:
            ConfidenceResult: Composite confidence score, status classification,
                per-signal breakdown, evidence, and human-readable reasoning.
        """
        ...

    async def score_batch(
        self, match_results: list[RequirementMatch]
    ) -> list[ConfidenceResult]:
        """Calculate confidence scores for a list of requirement matches.

        Args:
            match_results (list[RequirementMatch]): List of match results from JobMatchingService.

        Returns:
            list[ConfidenceResult]: Confidence results in same order as input.
        """
        ...
```

Interface này phải ổn định kể cả khi thuật toán scoring bên trong thay đổi.

---

## Downstream Consumers

| Consumer | Phase | Usage |
|---|---|---|
| `JobMatchingService` | Phase 3 | Nhận `ConfidenceResult` để tổng hợp match score cuối cùng |
| `SkillGapService` | Phase 4 | Dùng `status` để phân loại missing/partial skills |
| `CareerSnapshotService` | Phase 6 | Lưu `ConfidenceResult` vào immutable career snapshot |
| Frontend Match UI | Phase 3 | Hiển thị `reasoning`, `evidence`, `signals` cho ứng viên |

`IConfidenceEngineService` được inject qua FastAPI Dependency Injection.

---

## Design Principles

* **Deterministic over probabilistic**: cùng input → cùng output, mọi lần.
* **Explainable over opaque**: mọi score đều kèm `reasoning` và `signals` breakdown.
* **LLM-independent**: không có Gemini call nào trong engine này.
* **Configuration-driven**: weights và thresholds load từ external JSON, không hardcode.
* **Async**: tất cả method đều `async def` để align với FastAPI async runtime.
* **Pure logic**: không có database call, không có side effects — chỉ nhận input, trả output.
* **Extensible**: architecture cho phép thay thế heuristic scoring bằng ML models mà không đổi public interface.

---

## Future Extensions

Kiến trúc phải cho phép thay thế heuristic scoring bằng kỹ thuật tiên tiến hơn mà không thay đổi `IConfidenceEngineService`:

* Embedding-based confidence calibration.
* Machine learning ranking models.
* Bayesian confidence estimation.
* Expected Calibration Error (ECE) calibration.
* Human feedback loop calibration.
* Recruiter acceptance rate calibration.

---

## Acceptance Criteria

* [ ] Nhận `RequirementMatch` từ `JobMatchingService` và trả về `ConfidenceResult`.
* [ ] Output bắt buộc gồm: `confidence`, `evidence_score`, `semantic_score`, `status`, `signals`, `evidence`, `reasoning`.
* [ ] `evidence_score` và `reasoning` không được là `null` hoặc empty list.
* [ ] Scoring weights và classification thresholds load từ external config, không hardcode.
* [ ] `MatchStatus` dùng Enum `app/enums/match_status.py`.
* [ ] Không có Gemini call nào trong toàn bộ module.
* [ ] Tất cả method đều là `async def`.
* [ ] Score phải reproducible: cùng input → cùng output mọi lần.
* [ ] Expose `IConfidenceEngineService` (typing.Protocol) cho downstream injection.

