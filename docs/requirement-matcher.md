# Context: Requirement Matcher Service — MockAI

> **Agent context document**: mô tả theo hướng **kiến trúc + trách nhiệm + interface**. `JobMatchingService` là intelligence core của Phase 3, phối hợp với `SkillNormalizerService` và `ConfidenceEngineService` để tạo ra kết quả matching hoàn chỉnh.

---

## Purpose

`JobMatchingService` là service trung tâm của **Phase 3 — Job Matching** trong MockAI. Trách nhiệm của service là đánh giá từng job requirement của JD đối chiếu với `CandidateProfile` đã được chuẩn hoá, xác định requirement đó có được đáp ứng không và cung cấp kết quả explainable cho ứng viên.

Khác với `SkillNormalizerService`, service này thực hiện **semantic reasoning** và tạo ra kết quả có thể giải thích được.

Thiết kế xoay quanh **atomic requirement evaluation** — mỗi job requirement được đánh giá độc lập trước khi được tổng hợp thành Requirement Matrix.

---

## Objectives

Với mỗi requirement, `JobMatchingService` phải trả lời:

* Ứng viên có đáp ứng requirement này không?
* Nếu không, mức độ gần bao nhiêu?
* Bằng chứng nào hỗ trợ quyết định?
* Quyết định đó đáng tin cậy đến mức nào?
* Requirement này quan trọng đến đâu trong JD?

Kết quả phải luôn explainable — không chấp nhận "black box" output.

---

## Responsibilities

`JobMatchingService` phải:

* So sánh canonical skills của `CandidateProfile` với canonical requirements từ JD.
* Ưu tiên matching deterministic trước semantic reasoning.
* Đánh giá từng requirement như một đơn vị độc lập (atomic evaluation).
* Delegate confidence scoring sang `ConfidenceEngineService`.
* Delegate skill normalization sang `SkillNormalizerService`.
* Thu thập evidence từ các section của CV.
* Tính `contribution = priority_score × confidence`.
* Tổng hợp kết quả thành Requirement Matrix.

`JobMatchingService` tuyệt đối **không** được:

* Parse resume — đó là trách nhiệm của `ResumeAnalysisService`.
* Normalize skills — đó là trách nhiệm của `SkillNormalizerService`.
* Tính confidence score — đó là trách nhiệm của `ConfidenceEngineService`.
* Generate learning plans — đó là trách nhiệm của `LearningRoadmapService`.
* Xếp hạng ứng viên toàn cục.
* Sinh câu hỏi phỏng vấn.

---

## Input Schemas

### CandidateProfile (từ Phase 2)

```python
# app/schemas/internal/candidate_profile_input.py
from pydantic import BaseModel, Field
from app.schemas.response.skill_normalizer_response import NormalizedSkill


class ProfileSkill(BaseModel):
    canonical: str = Field(..., description="Canonical skill name from SkillNormalizerService.")
    category: str = Field(..., description="High-level skill category.")
    confidence: float = Field(..., ge=0.0, le=1.0)
    mapping_method: str = Field(..., description="How the skill was mapped.")


class ProfileExperience(BaseModel):
    title: str
    company: str
    duration_months: int
    description: str


class ProfileProject(BaseModel):
    name: str
    description: str
    technologies: list[str]


class CandidateProfileInput(BaseModel):
    user_id: str
    skills: list[ProfileSkill] = Field(default_factory=list)
    experience: list[ProfileExperience] = Field(default_factory=list)
    projects: list[ProfileProject] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    summary: str = Field(default="")
```

### JobRequirement (từ JSearch API / JD parsing)

```python
# app/schemas/internal/job_requirement.py
from pydantic import BaseModel, Field
from typing import Literal
from app.enums.requirement_priority import RequirementPriority


class JobRequirement(BaseModel):
    id: str = Field(..., description="Unique requirement identifier within the JD.")
    text: str = Field(..., description="Raw requirement text from JD.")
    canonical: str = Field(..., description="Canonical form after SkillNormalizerService.")
    category: str = Field(..., description="Skill category.")
    section: Literal["must_have", "required", "preferred", "nice_to_have"] = Field(
        ..., description="JD section this requirement belongs to."
    )
    priority: RequirementPriority = Field(
        ..., description="Business importance derived from section."
    )
```

**Ví dụ input:**

```json
{
    "id": "REQ001",
    "text": "Experience with Docker and container orchestration",
    "canonical": "Containerization",
    "category": "DevOps",
    "section": "must_have",
    "priority": "CRITICAL"
}
```

---

## Enums

```python
# app/enums/requirement_priority.py
from enum import Enum

class RequirementPriority(str, Enum):
    CRITICAL = "CRITICAL"   # must_have
    HIGH = "HIGH"           # required
    MEDIUM = "MEDIUM"       # preferred
    LOW = "LOW"             # nice_to_have
```

```python
# app/enums/match_status.py
# (tái sử dụng từ ConfidenceEngineService — không định nghĩa lại)
from enum import Enum

class MatchStatus(str, Enum):
    SATISFIED = "SATISFIED"
    PARTIAL = "PARTIAL"
    CLARIFICATION = "CLARIFICATION"
    MISSING = "MISSING"
```

**Priority score mapping** (load từ `app/static/priority_scores.json`, không hardcode):

| Priority | Score |
|---|---|
| `CRITICAL` | 1.00 |
| `HIGH` | 0.80 |
| `MEDIUM` | 0.60 |
| `LOW` | 0.40 |

---

## Output Schema

```python
# app/schemas/response/requirement_match_result.py
from pydantic import BaseModel, Field
from app.enums.match_status import MatchStatus
from app.enums.requirement_priority import RequirementPriority


class PriorityInfo(BaseModel):
    level: RequirementPriority
    score: float = Field(..., ge=0.0, le=1.0)


class MatchEvidence(BaseModel):
    section: str = Field(..., description="CV section: skills, experience, projects, certifications, summary.")
    text: str = Field(..., description="Raw text snippet supporting the match.")


class RequirementMatchResult(BaseModel):
    requirement_id: str = Field(..., description="Unique ID of the requirement.")
    requirement: str = Field(..., description="Canonical skill required by the JD.")
    status: MatchStatus = Field(..., description="Requirement satisfaction status.")
    priority: PriorityInfo = Field(..., description="Requirement priority and score.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence from ConfidenceEngineService.")
    evidence_score: float = Field(..., ge=0.0, le=1.0, description="Aggregated evidence strength.")
    matched_skill: str = Field(..., description="Candidate canonical skill matched against requirement.")
    matching_method: str = Field(..., description="canonical | alias | ai | cached | none")
    evidence: list[MatchEvidence] = Field(default_factory=list)
    reasoning: list[str] = Field(..., description="Human-readable explanation of the match decision.")
    contribution: float = Field(
        ..., ge=0.0, le=1.0,
        description="Weighted contribution to overall match score. = priority.score × confidence"
    )
```

**Ví dụ output:**

```json
{
    "requirement_id": "REQ001",
    "requirement": "Containerization",
    "status": "SATISFIED",
    "priority": { "level": "CRITICAL", "score": 1.0 },
    "confidence": 0.96,
    "evidence_score": 0.95,
    "matched_skill": "Docker",
    "matching_method": "canonical",
    "evidence": [
        { "section": "projects", "text": "Built Docker containers for microservice deployment." },
        { "section": "experience", "text": "Managed Docker Compose environments for 3 services." }
    ],
    "reasoning": [
        "Exact canonical match: 'Docker' → 'Containerization'.",
        "Evidence found in 2 CV sections: projects, experience.",
        "High semantic similarity: 0.94."
    ],
    "contribution": 0.96
}
```

---

## Processing Pipeline

```text
CandidateProfile + JobRequirement
            │
            ▼
[1] Priority Assessment
    (RequirementPriority → priority_score)
            │
            ▼
[2] Matching Engine (3-stage strategy)
    │
    ├─ Stage 1: Exact Canonical Match   → SkillNormalizerService output
    ├─ Stage 2: Related Skill Match     → category + alias lookup
    └─ Stage 3: AI Semantic Evaluation  → Gemini 2.5 Flash Lite (fallback only)
            │
            ▼
[3] Evidence Collection
    (extract relevant text from CV sections)
            │
            ▼
[4] Confidence Scoring
    → delegates to ConfidenceEngineService.score(RequirementMatch)
            │
            ▼
[5] Contribution Calculation
    contribution = priority.score × confidence
            │
            ▼
RequirementMatchResult
```

Mỗi stage phải độc lập và có thể test riêng lẻ.

---

## Matching Strategy

### Stage 1 — Exact Canonical Match

So sánh trực tiếp canonical skill.

```text
JD Requirement canonical:  "Containerization"
Candidate skill canonical:  "Containerization"
→ MATCH → status: SATISFIED (nếu confidence ≥ 0.90)
```

Đây là matching nhanh nhất và đáng tin cậy nhất — luôn thử trước.

### Stage 2 — Related Skill Match (Category Fallback)

Nếu exact match thất bại, tìm candidate skills cùng category.

```text
JD Requirement: "Backend Development" (category: Backend)
Candidate: không có "Backend Development"
         nhưng có "FastAPI" → category: Backend
→ PARTIAL hoặc SATISFIED (tùy confidence)
```

Implementation phải cho phép tích hợp ontology hoặc knowledge graph trong tương lai mà không thay đổi interface.

### Stage 3 — AI Semantic Evaluation (Gemini 2.5 Flash Lite — Fallback)

Chỉ gọi khi Stage 1 và Stage 2 đều không cho kết quả đủ tin cậy.

**LLM nhận:**

```json
{
    "requirement": "Containerization",
    "candidate_skills": ["Docker", "Kubernetes"],
    "candidate_evidence": ["Built containerized services using Docker Compose."],
    "instruction": "Evaluate if the candidate satisfies this requirement. Return structured JSON only."
}
```

**LLM phải trả về structured JSON:**

```json
{
    "is_satisfied": true,
    "confidence_hint": 0.82,
    "reasoning": "Candidate has direct Docker experience which maps to Containerization."
}
```

**Ràng buộc bất biến:**
- LLM **không được** tự tính confidence cuối cùng — `confidence_hint` chỉ là gợi ý đầu vào cho `ConfidenceEngineService`.
- Prompt phải versioned, lưu trong `prompts/requirement_eval_v1.txt`.
- Không hardcode prompt bên trong service class.
- Kết quả AI phải validate trước khi dùng.

---

## Architecture

Tuân theo **Clean/Layered Architecture** của MockAI:

```text
app/services/job_matching/

    interfaces/
        job_matching_service.py           ← typing.Protocol (public contract)

    impl/
        job_matching_service_impl.py      ← Orchestrates full matching pipeline

    stages/
        priority_assessor.py             ← Stage 1: priority_score lookup
        canonical_matcher.py             ← Stage 2a: exact canonical match
        related_skill_matcher.py         ← Stage 2b: category-based match
        ai_evaluator.py                  ← Stage 3: Gemini 2.5 Flash Lite fallback
        evidence_collector.py            ← Extract evidence from CV sections
        contribution_calculator.py       ← priority.score × confidence

    prompts/
        requirement_eval_v1.txt          ← Versioned Gemini prompt

app/static/
    priority_scores.json                 ← CRITICAL/HIGH/MEDIUM/LOW → float
    related_skills.json                  ← Category → related canonical skills

app/schemas/
    internal/
        candidate_profile_input.py       ← CandidateProfileInput
        job_requirement.py               ← JobRequirement
    response/
        requirement_match_result.py      ← RequirementMatchResult

app/enums/
    requirement_priority.py              ← RequirementPriority Enum
    match_status.py                      ← MatchStatus Enum (shared)
```

---

## Service Integration

```text
ResumeAnalysisService (Phase 2)
        │  produces CandidateProfile
        ▼
SkillNormalizerService
        │  normalizes skills in CandidateProfile + JD requirements
        ▼
JobMatchingService   ← THIS SERVICE
        │  atomic evaluation per requirement
        │  delegates confidence → ConfidenceEngineService
        ▼
RequirementMatrix (list[RequirementMatchResult])
        │
        ├─► JobMatchRepository     (persist to DB)
        ├─► SkillGapService        (Phase 4)
        └─► CareerSnapshotService  (Phase 6)
```

---

## Public Interface

Định nghĩa bằng `typing.Protocol` theo chuẩn MockAI:

```python
# app/services/interfaces/job_matching_service.py
from typing import Protocol
from app.schemas.internal.candidate_profile_input import CandidateProfileInput
from app.schemas.internal.job_requirement import JobRequirement
from app.schemas.response.requirement_match_result import RequirementMatchResult


class IJobMatchingService(Protocol):

    async def evaluate(
        self,
        candidate_profile: CandidateProfileInput,
        requirement: JobRequirement,
    ) -> RequirementMatchResult:
        """Evaluate a single job requirement against the candidate profile.

        Args:
            candidate_profile (CandidateProfileInput): Structured candidate profile
                from ResumeAnalysisService with normalized skills and CV sections.
            requirement (JobRequirement): A single normalized JD requirement with
                canonical form and priority section.

        Returns:
            RequirementMatchResult: Atomic evaluation result including status,
                confidence, evidence, reasoning, and weighted contribution.
        """
        ...

    async def evaluate_all(
        self,
        candidate_profile: CandidateProfileInput,
        requirements: list[JobRequirement],
    ) -> list[RequirementMatchResult]:
        """Evaluate all job requirements against the candidate profile.

        Args:
            candidate_profile (CandidateProfileInput): Candidate profile.
            requirements (list[JobRequirement]): Full list of JD requirements.

        Returns:
            list[RequirementMatchResult]: One result per requirement, in same order.
                Aggregated as the Requirement Matrix for downstream services.
        """
        ...
```

---

## Overall Architecture Diagram (MockAI Phase 3)

```text
ResumeAnalysisService
        │  CandidateProfile (normalized skills, experience, projects)
        ▼
SkillNormalizerService
        │  NormalizedSkill[] (canonical, category, confidence, mapping_method)
        ▼
JobMatchingService
        ├── [1] PriorityAssessor       → priority_score per requirement
        ├── [2] CanonicalMatcher       → exact canonical match
        ├── [3] RelatedSkillMatcher    → category fallback
        ├── [4] AIEvaluator            → Gemini 2.5 Flash Lite (last resort)
        ├── [5] EvidenceCollector      → text snippets from CV sections
        ├── [6] ConfidenceEngineService → deterministic confidence score
        └── [7] ContributionCalculator → priority.score × confidence
        │
        ▼
Requirement Matrix (list[RequirementMatchResult])
        │
        ├─► JobMatchRepository      → persist to database
        ├─► SkillGapService         → Phase 4: identify gaps
        ├─► CareerRecommendationService → Phase 4: career paths
        └─► CareerSnapshotService   → Phase 6: immutable snapshot
```

---

## Downstream Consumers

| Consumer | Phase | Usage |
|---|---|---|
| `JobMatchRepository` | Phase 3 | Persist `RequirementMatchResult[]` to DB |
| `SkillGapService` | Phase 4 | Filter `MISSING` + `PARTIAL` results để phân tích gap |
| `CareerRecommendationService` | Phase 4 | Dùng match matrix để gợi ý career paths |
| `LearningRoadmapService` | Phase 4 | Dùng missing skills để tạo roadmap |
| `CareerSnapshotService` | Phase 6 | Lưu match matrix vào immutable career snapshot |
| Frontend Match UI | Phase 3 | Hiển thị `status`, `confidence`, `evidence`, `reasoning` |

`IJobMatchingService` được inject qua FastAPI Dependency Injection.

---

## Design Principles

* **Atomic evaluation**: mỗi requirement = một lần evaluate độc lập.
* **Deterministic-first**: canonical match và category match trước, AI sau cùng.
* **AI as last resort**: Gemini 2.5 Flash Lite chỉ được gọi khi Stage 1 và Stage 2 thất bại.
* **Delegation**: confidence scoring delegate sang `ConfidenceEngineService`, không tự tính.
* **Explainable**: mọi result phải có `reasoning[]` và `evidence[]` không rỗng.
* **Configuration-driven**: priority scores và related skills load từ external JSON.
* **Prompt versioning**: Gemini prompt lưu trong `prompts/` với suffix version.
* **Async**: tất cả method đều `async def`.
* **Stateless**: không phụ thuộc vào request trước, không có internal state.
* **Extensible**: có thể thay thế matching stages bằng ESCO, embedding, Knowledge Graph mà không đổi `IJobMatchingService`.

---

## Future Extensions

Kiến trúc `stages/` cho phép thay thế từng bước matching mà không thay đổi `IJobMatchingService`:

* ESCO ontology reasoning
* Knowledge Graph traversal
* Vector similarity search (embedding-based)
* Hybrid retrieval (BM25 + embeddings)
* Learning-to-Rank models
* Human feedback calibration loop

---

## Acceptance Criteria

* [ ] Nhận `CandidateProfileInput` và `list[JobRequirement]`, trả về `list[RequirementMatchResult]`.
* [ ] Mỗi requirement được evaluate độc lập (atomic).
* [ ] Output bắt buộc: `status`, `confidence`, `evidence_score`, `matched_skill`, `matching_method`, `evidence`, `reasoning`, `contribution`.
* [ ] `reasoning` và `evidence` không được là empty list với `SATISFIED` hoặc `PARTIAL` status.
* [ ] `contribution = priority.score × confidence` — không được hardcode priority scores.
* [ ] Stage 3 (Gemini) chỉ được gọi khi Stage 1 và Stage 2 thất bại.
* [ ] Gemini prompt phải versioned và lưu ngoài service class.
* [ ] Confidence scoring phải delegate sang `ConfidenceEngineService`, không tự tính.
* [ ] `MatchStatus` và `RequirementPriority` dùng Enum trong `app/enums/`.
* [ ] Tất cả method đều là `async def`.
* [ ] Expose `IJobMatchingService` (typing.Protocol) cho downstream injection.
* [ ] `evaluate_all()` trả về kết quả đúng thứ tự với input requirements.
