import uuid
import time
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import NotFoundError, ValidationError, AIMatchingException
from app.models.job import Job
from app.models.job_match import JobMatch, SkillMatch, MatchQualityFeedback
from app.models.candidate_profile import CandidateProfile
from app.repositories.job_match_repository import JobMatchRepository
from app.repositories.job_repository import JobRepository
from app.repositories.candidate_profile_repository import CandidateProfileRepository
from app.services.interfaces.matching_service import IMatchingService
from app.services.interfaces.ai_provider import AIProvider

logger = logging.getLogger(__name__)

MATCHING_ALGO_VERSION = "match-1.0"
MATCH_CACHE_DAYS = 7
CONFIDENCE_REVIEW_THRESHOLD = 80.0
BATCH_LIMIT = 50
BATCH_CONCURRENCY = 5

# Composite score weights (Business Rule).
W_SKILLS, W_EXPERIENCE, W_EDUCATION, W_LOCATION = 0.40, 0.35, 0.15, 0.10


class MatchingServiceImpl(IMatchingService):
    def __init__(self, db: AsyncSession, ai: AIProvider):
        self.db = db
        self.ai = ai
        self.repo = JobMatchRepository(db)
        self.job_repo = JobRepository(db)
        self.profile_repo = CandidateProfileRepository(db)

    # ------------------------------------------------------------ single match
    async def calculate_match(self, user_id: uuid.UUID, job_id: uuid.UUID) -> Dict[str, Any]:
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundError("Không tìm thấy tin tuyển dụng")

        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise ValidationError("Bạn cần hoàn thiện hồ sơ ứng viên trước khi so khớp việc làm")

        # Cache: reuse a recent match unless the profile or job changed since.
        existing = await self.repo.get_by_user_and_job(user_id, job_id)
        if existing and self._is_cache_valid(existing, profile, job):
            return self._summary_from_match(existing)

        started = time.perf_counter()
        analysis = await self._run_ai_match(profile, job)
        duration_ms = int((time.perf_counter() - started) * 1000)

        scores = self._extract_scores(analysis)
        overall = self._composite_score(scores)
        confidence = self._num(analysis.get("overall_assessment", {}).get("confidence"), default=75.0)

        values = {
            "candidate_profile_id": profile.id,
            "overall_match_score": overall,
            "skills_match_score": scores["skills"],
            "experience_match_score": scores["experience"],
            "education_match_score": scores["education"],
            "location_match_score": scores["location"],
            "match_explanation": analysis.get("overall_assessment", {}).get("summary"),
            "strengths": analysis.get("strengths", []),
            "weaknesses": analysis.get("experience_analysis", {}).get("experience_gaps", []),
            "missing_skills": analysis.get("skills_analysis", {}).get("missing_skills", []),
            "skill_gaps": analysis.get("areas_for_improvement", []),
            "improvement_suggestions": analysis.get("areas_for_improvement", []),
            "recommendation": analysis.get("recommendation", {}),
            "gemini_model_version": getattr(self.ai, "model_version", "unknown"),
            "matching_algorithm_version": MATCHING_ALGO_VERSION,
            "processing_duration": duration_ms,
            "confidence_score": confidence,
            "needs_review": confidence < CONFIDENCE_REVIEW_THRESHOLD,
        }

        match = await self.repo.upsert_match(user_id, job_id, values)
        await self._store_skill_matches(match.id, analysis)

        return self._summary_from_match(match)

    async def _run_ai_match(self, profile: CandidateProfile, job: Job) -> Dict[str, Any]:
        """Call the AI provider, falling back to a deterministic mock when no key is set."""
        profile_dict = self._profile_to_dict(profile)
        job_dict = self._job_to_dict(job)

        if not getattr(self.ai, "api_key", None):
            logger.warning("AI provider has no API key; returning mock match analysis.")
            return self._mock_analysis(profile_dict, job_dict)

        try:
            return await self.ai.match_job(profile_dict, job_dict)
        except Exception as e:  # noqa: BLE001
            logger.error(f"AI match failed: {e}", exc_info=True)
            raise AIMatchingException()

    # ------------------------------------------------------------ batch match
    async def batch_match(self, user_id: uuid.UUID, job_ids: List[uuid.UUID]) -> Dict[str, Any]:
        if not job_ids:
            raise ValidationError("Danh sách job cần so khớp đang trống")
        if len(job_ids) > BATCH_LIMIT:
            raise ValidationError(f"Chỉ có thể so khớp tối đa {BATCH_LIMIT} việc làm mỗi lần")

        semaphore = asyncio.Semaphore(BATCH_CONCURRENCY)
        started = time.perf_counter()

        async def match_one(job_id: uuid.UUID):
            async with semaphore:
                try:
                    result = await self.calculate_match(user_id, job_id)
                    return {"job_id": str(job_id), "match_id": result["match_id"],
                            "overall_score": result["overall_score"], "status": "completed"}
                except Exception as e:  # noqa: BLE001
                    logger.warning(f"Batch match failed for job {job_id}: {e}")
                    return {"job_id": str(job_id), "match_id": None,
                            "overall_score": None, "status": "failed"}

        results = await asyncio.gather(*[match_one(j) for j in job_ids])
        total_ms = int((time.perf_counter() - started) * 1000)

        successful = [r for r in results if r["status"] == "completed"]
        failed = [r for r in results if r["status"] == "failed"]
        avg = int(total_ms / len(results)) if results else 0

        return {
            "matches": results,
            "processing_summary": {
                "total_jobs": len(job_ids),
                "successful": len(successful),
                "failed": len(failed),
                "average_processing_time": avg,
            },
        }

    # ------------------------------------------------------------ read
    async def get_match_detail(self, user_id: uuid.UUID, match_id: uuid.UUID) -> Dict[str, Any]:
        match = await self.repo.get_by_id(match_id)
        if not match or match.user_id != user_id:
            raise NotFoundError("Không tìm thấy kết quả so khớp")

        job = await self.job_repo.get_by_id(match.job_id)
        skill_rows = await self.repo.get_skill_matches(match_id)

        return {
            "id": str(match.id),
            "job": self._job_brief(job) if job else None,
            "overall_score": float(match.overall_match_score),
            "skills_score": self._opt_float(match.skills_match_score),
            "experience_score": self._opt_float(match.experience_match_score),
            "education_score": self._opt_float(match.education_match_score),
            "location_score": self._opt_float(match.location_match_score),
            "confidence_score": self._opt_float(match.confidence_score),
            "needs_review": match.needs_review,
            "analysis": {
                "summary": match.match_explanation,
                "strengths": match.strengths or [],
                "weaknesses": match.weaknesses or [],
                "missing_skills": match.missing_skills or [],
                "areas_for_improvement": match.improvement_suggestions or [],
                "recommendation": match.recommendation or {},
                "skills_matches": [
                    {
                        "skill_name": s.skill_name,
                        "skill_category": s.skill_category,
                        "required_proficiency": s.required_proficiency,
                        "candidate_proficiency": s.candidate_proficiency,
                        "match_type": s.match_type,
                        "match_score": self._opt_float(s.match_score),
                    }
                    for s in skill_rows
                ],
            },
            "processing_time": match.processing_duration,
            "created_at": match.created_at,
        }

    async def get_user_matches(
        self,
        user_id: uuid.UUID,
        min_score: Optional[float] = None,
        sort: str = "score",
        order: str = "desc",
        page: int = 1,
        per_page: int = 20,
    ) -> Dict[str, Any]:
        rows, total = await self.repo.list_matches(
            user_id, min_score=min_score, sort=sort, order=order, page=page, per_page=per_page
        )
        matches = [
            {
                "match_id": str(match.id),
                "job": self._job_brief(job),
                "overall_score": float(match.overall_match_score),
                "match_summary": match.match_explanation,
                "needs_review": match.needs_review,
                "created_at": match.created_at,
            }
            for match, job in rows
        ]
        total_pages = (total + per_page - 1) // per_page if per_page else 0
        return {
            "matches": matches,
            "pagination": {"page": page, "per_page": per_page, "total": total, "total_pages": total_pages},
        }

    async def submit_feedback(
        self,
        user_id: uuid.UUID,
        match_id: uuid.UUID,
        feedback_type: Optional[str],
        user_rating: Optional[int],
        feedback_notes: Optional[str],
    ) -> bool:
        match = await self.repo.get_by_id(match_id)
        if not match or match.user_id != user_id:
            raise NotFoundError("Không tìm thấy kết quả so khớp")
        if user_rating is not None and not (1 <= user_rating <= 5):
            raise ValidationError("Đánh giá phải nằm trong khoảng 1-5")

        await self.repo.add_feedback(MatchQualityFeedback(
            job_match_id=match_id,
            user_id=user_id,
            feedback_type=feedback_type,
            user_rating=user_rating,
            feedback_notes=feedback_notes,
        ))
        return True

    # ------------------------------------------------------------ helpers
    @staticmethod
    def _is_cache_valid(match: JobMatch, profile: CandidateProfile, job: Job) -> bool:
        created = match.created_at
        if created is None:
            return False
        now = datetime.now(timezone.utc)
        if created < now - timedelta(days=MATCH_CACHE_DAYS):
            return False
        # Invalidate if profile or job changed after the match was computed.
        if profile.updated_at and profile.updated_at > created:
            return False
        if job.updated_at and job.updated_at > created:
            return False
        return True

    async def _store_skill_matches(self, match_id: uuid.UUID, analysis: Dict[str, Any]) -> None:
        skills = analysis.get("skills_analysis", {})
        for s in skills.get("matching_skills", []) or []:
            await self.repo.add_skill_match(SkillMatch(
                job_match_id=match_id,
                skill_name=s.get("skill", "unknown"),
                required_proficiency=s.get("required_level"),
                candidate_proficiency=s.get("candidate_level"),
                match_type="exact" if s.get("match_quality") == "excellent" else "partial",
                match_score=self._quality_to_score(s.get("match_quality")),
            ))
        for s in skills.get("missing_skills", []) or []:
            await self.repo.add_skill_match(SkillMatch(
                job_match_id=match_id,
                skill_name=s.get("skill", "unknown"),
                required_proficiency=s.get("required_level"),
                match_type="missing",
                match_score=0.0,
            ))
        for s in skills.get("bonus_skills", []) or []:
            await self.repo.add_skill_match(SkillMatch(
                job_match_id=match_id,
                skill_name=s.get("skill", "unknown"),
                match_type="bonus",
                match_score=100.0,
            ))

    def _extract_scores(self, analysis: Dict[str, Any]) -> Dict[str, float]:
        return {
            "skills": self._num(analysis.get("skills_analysis", {}).get("skills_score")),
            "experience": self._num(analysis.get("experience_analysis", {}).get("experience_score")),
            "education": self._num(analysis.get("education_analysis", {}).get("education_score")),
            "location": self._num(analysis.get("location_compatibility", {}).get("location_score")),
        }

    @staticmethod
    def _composite_score(scores: Dict[str, float]) -> float:
        overall = (
            scores["skills"] * W_SKILLS
            + scores["experience"] * W_EXPERIENCE
            + scores["education"] * W_EDUCATION
            + scores["location"] * W_LOCATION
        )
        return round(min(100.0, max(0.0, overall)), 2)

    def _summary_from_match(self, match: JobMatch) -> Dict[str, Any]:
        return {
            "match_id": str(match.id),
            "overall_score": float(match.overall_match_score),
            "skills_score": self._opt_float(match.skills_match_score),
            "experience_score": self._opt_float(match.experience_match_score),
            "education_score": self._opt_float(match.education_match_score),
            "location_score": self._opt_float(match.location_match_score),
            "confidence_score": self._opt_float(match.confidence_score),
            "needs_review": match.needs_review,
            "processing_time": match.processing_duration,
            "created_at": match.created_at,
        }

    @staticmethod
    def _job_brief(job: Job) -> Dict[str, Any]:
        return {
            "id": str(job.id),
            "title": job.title,
            "company": job.company_name,
            "location": job.location,
            "employment_type": job.employment_type,
        }

    @staticmethod
    def _num(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _opt_float(value: Any) -> Optional[float]:
        return float(value) if value is not None else None

    @staticmethod
    def _quality_to_score(quality: Optional[str]) -> float:
        return {"excellent": 100.0, "good": 75.0, "fair": 50.0}.get(quality or "", 60.0)

    @staticmethod
    def _profile_to_dict(profile: CandidateProfile) -> Dict[str, Any]:
        return {
            "full_name": profile.full_name,
            "professional_summary": profile.professional_summary,
            "years_of_experience": profile.years_of_experience,
            "current_role": profile.current_role,
            "location": profile.location,
            "salary_expectation_min": profile.salary_expectation_min,
            "salary_expectation_max": profile.salary_expectation_max,
            "work_experience": profile.work_experience or [],
            "education": profile.education or [],
            "technical_skills": profile.technical_skills or [],
            "soft_skills": profile.soft_skills or [],
            "certifications": profile.certifications or [],
            "projects": profile.projects or [],
        }

    @staticmethod
    def _job_to_dict(job: Job) -> Dict[str, Any]:
        return {
            "title": job.title,
            "company": job.company_name,
            "location": job.location,
            "employment_type": job.employment_type,
            "experience_level": job.experience_level,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "description": job.description,
            "requirements": job.requirements,
            "skills_required": job.skills_required or [],
        }

    # ------------------------------------------------------------ mock analysis
    def _mock_analysis(self, profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Deterministic analysis used when no AI key is configured (demo/tests)."""
        profile_skills = {
            str(s.get("name") if isinstance(s, dict) else s).lower().strip()
            for s in profile.get("technical_skills", []) if s
        }
        job_skills = {str(s).lower().strip() for s in job.get("skills_required", []) if s}

        matched = sorted(profile_skills & job_skills)
        missing = sorted(job_skills - profile_skills)
        bonus = sorted(profile_skills - job_skills)[:5]

        skills_score = round(len(matched) / len(job_skills) * 100, 2) if job_skills else 60.0
        exp_years = profile.get("years_of_experience") or 0
        experience_score = min(100.0, 40.0 + exp_years * 10.0)
        education_score = 70.0 if profile.get("education") else 40.0
        location_score = 100.0 if (job.get("employment_type") == "remote") else 70.0

        return {
            "overall_assessment": {
                "match_score": skills_score,
                "confidence": 85.0,
                "summary": (
                    f"Hồ sơ trùng khớp {len(matched)}/{max(len(job_skills), 1)} kỹ năng yêu cầu "
                    f"cho vị trí {job.get('title')}."
                ),
            },
            "skills_analysis": {
                "matching_skills": [
                    {"skill": s, "candidate_level": "intermediate", "required_level": "intermediate",
                     "match_quality": "good"} for s in matched
                ],
                "missing_skills": [
                    {"skill": s, "required_level": "intermediate", "importance": "high",
                     "learning_effort": "medium"} for s in missing
                ],
                "bonus_skills": [{"skill": s, "value": "Kỹ năng bổ trợ giá trị"} for s in bonus],
                "skills_score": skills_score,
            },
            "experience_analysis": {
                "relevant_experience": f"Ứng viên có khoảng {exp_years} năm kinh nghiệm.",
                "experience_gaps": missing[:3],
                "experience_score": experience_score,
                "career_progression_fit": "Phù hợp ở mức khá với lộ trình của vị trí.",
            },
            "education_analysis": {
                "education_fit": "Nền tảng học vấn đáp ứng yêu cầu cơ bản.",
                "education_score": education_score,
                "additional_education_needs": [],
            },
            "location_compatibility": {
                "location_score": location_score,
                "remote_work_fit": "Phù hợp làm việc từ xa." if location_score == 100 else "Cần cân nhắc địa điểm.",
                "relocation_considerations": "",
            },
            "strengths": [f"Thành thạo: {s}" for s in matched[:3]] or ["Hồ sơ nền tảng ổn định"],
            "areas_for_improvement": [
                {"area": s, "priority": "high", "suggestion": f"Nên bổ sung/nâng cao kỹ năng {s}"}
                for s in missing[:3]
            ],
            "recommendation": {
                "should_apply": skills_score >= 60,
                "likelihood_of_success": "high" if skills_score >= 80 else ("medium" if skills_score >= 60 else "low"),
                "key_selling_points": [f"Kỹ năng {s}" for s in matched[:2]],
                "preparation_advice": "Nhấn mạnh các dự án thực tế liên quan đến yêu cầu công việc.",
            },
        }
