import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import NotFoundError, JSearchAPIException
from app.models.job import Job, SavedSearch, JobRecommendation
from app.repositories.job_repository import JobRepository
from app.repositories.candidate_profile_repository import CandidateProfileRepository
from app.services.interfaces.job_discovery_service import IJobDiscoveryService
from app.services.interfaces.jsearch_service import JSearchService

logger = logging.getLogger(__name__)

# Cache freshness window for job postings (Business Rule: refresh every 4 hours).
CACHE_TTL_HOURS = 4
RECOMMENDATION_ALGO_VERSION = "reco-1.0"


class JobDiscoveryServiceImpl(IJobDiscoveryService):
    def __init__(self, db: AsyncSession, jsearch: JSearchService):
        self.db = db
        self.jsearch = jsearch
        self.repo = JobRepository(db)
        self.profile_repo = CandidateProfileRepository(db)

    # ------------------------------------------------------------------ search
    async def search_jobs(
        self,
        user_id: uuid.UUID,
        query: str,
        location: Optional[str] = None,
        employment_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        salary_min: Optional[int] = None,
        remote_only: bool = False,
        page: int = 1,
        per_page: int = 20,
    ) -> Dict[str, Any]:
        # Expire stale cache rows before deciding whether to hit the external API.
        await self.repo.deactivate_expired()

        # Decide if we need fresh data: check whether we already have fresh cached
        # jobs matching this query. If none, fetch from JSearch and upsert.
        cached_jobs, total = await self.repo.search(
            query=query,
            location=location,
            employment_type=employment_type,
            experience_level=experience_level,
            salary_min=salary_min,
            remote_only=remote_only,
            page=page,
            per_page=per_page,
        )

        if total == 0 and page == 1:
            # The app's employment_type "remote" is a work-arrangement flag, so
            # fold it into remote_only for the JSearch work_from_home filter.
            remote = remote_only or (employment_type == "remote")
            await self._refresh_from_jsearch(
                query=query, location=location, page=page, remote_only=remote
            )
            cached_jobs, total = await self.repo.search(
                query=query,
                location=location,
                employment_type=employment_type,
                experience_level=experience_level,
                salary_min=salary_min,
                remote_only=remote_only,
                page=page,
                per_page=per_page,
            )

        bookmarked_ids = await self.repo.get_bookmarked_job_ids(user_id)

        # Log the search interaction for analytics (best-effort).
        jobs = [self._serialize_job(j, is_bookmarked=j.id in bookmarked_ids) for j in cached_jobs]
        total_pages = (total + per_page - 1) // per_page if per_page else 0

        return {
            "jobs": jobs,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    async def _refresh_from_jsearch(
        self, query: str, page: int, location: Optional[str] = None, remote_only: bool = False
    ) -> None:
        """Fetch jobs from JSearch and upsert them into the cache.
        
        If JSearch is unavailable (rate-limited, auth error, timeout) we fall
        back to seeding the mock dataset so the UI always has something to show.
        """
        raw_jobs: list = []
        try:
            # Region is handled by the `country` param (settings.JSEARCH_COUNTRY),
            # so only append a location when the user actually provided one.
            full_query = f"{query} in {location}" if location else query
            raw_jobs = await self.jsearch.search_jobs(
                query=full_query, page=page, remote_only=remote_only
            )
            logger.info(f"JSearch returned {len(raw_jobs)} jobs for query '{full_query}'")
        except Exception as e:  # noqa: BLE001 - normalize any client error
            logger.warning(f"JSearch fetch failed ({e}); seeding mock data as fallback.")

        # If JSearch returned nothing, fall back to mock data so the cache
        # is never left empty after a failed refresh.
        if not raw_jobs:
            from app.services.impl.jsearch_service_impl import JSearchServiceImpl
            raw_jobs = JSearchServiceImpl._mock_jobs()
            logger.info("Using mock job data as JSearch fallback.")

        for raw in raw_jobs:
            data = self._transform_jsearch(raw)
            if not data:
                continue
            # Upsert each row inside a SAVEPOINT so a single malformed record
            # (e.g. an unexpected value from the external API) rolls back only
            # itself instead of poisoning the whole transaction and 500-ing.
            try:
                async with self.db.begin_nested():
                    await self.repo.upsert_job(data)
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    f"Skipping job '{data.get('external_job_id')}' — upsert failed: {e}"
                )

    def _transform_jsearch(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize a raw JSearch job dict into our internal `jobs` schema."""
        external_id = raw.get("job_id")
        title = raw.get("job_title")
        company = raw.get("employer_name")
        if not external_id or not title or not company:
            return None

        # Location: /search-v2 often leaves city/state/country empty and provides a
        # combined `job_location` string instead — fall back to it.
        location_parts = [
            raw.get("job_city"),
            raw.get("job_state"),
            raw.get("job_country"),
        ]
        location = ", ".join([p for p in location_parts if p]) or raw.get("job_location") or None

        # Employment type: JSearch exposes is_remote + job_employment_type.
        if raw.get("job_is_remote"):
            employment_type = "remote"
        else:
            employment_type = (raw.get("job_employment_type") or "").lower() or None

        posted = raw.get("job_posted_at_datetime_utc")
        posted_date = None
        if posted:
            try:
                posted_date = datetime.fromisoformat(posted.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                posted_date = None
        # /search-v2 may omit the ISO datetime but include an epoch timestamp.
        if posted_date is None and raw.get("job_posted_at_timestamp"):
            try:
                posted_date = datetime.fromtimestamp(
                    int(raw["job_posted_at_timestamp"]), tz=timezone.utc
                )
            except (ValueError, TypeError, OverflowError):
                posted_date = None

        # Skills: JSearch sometimes returns job_required_skills; fall back to highlights.
        skills = raw.get("job_required_skills")
        if not skills:
            highlights = raw.get("job_highlights") or {}
            skills = highlights.get("Qualifications") or []

        now = datetime.now(timezone.utc)
        # Clip strings to their DB column limits and coerce salaries to int:
        # real JSearch payloads can carry very long ids/titles and float salaries
        # that would otherwise raise a DB truncation / type error on insert.
        return {
            "external_job_id": self._clip(str(external_id), 255),
            "title": self._clip(title, 500),
            "company_name": self._clip(company, 255),
            "company_logo_url": self._clip(raw.get("employer_logo"), 500),
            "location": self._clip(location, 255),
            "job_type": self._clip((raw.get("job_employment_type") or "").lower() or None, 100),
            "employment_type": self._clip(employment_type, 100),
            "experience_level": self._clip(self._map_experience_level(raw), 100),
            "salary_min": self._to_int(raw.get("job_min_salary")),
            "salary_max": self._to_int(raw.get("job_max_salary")),
            "salary_currency": self._clip(raw.get("job_salary_currency") or "USD", 10),
            "description": raw.get("job_description"),
            "requirements": self._join_highlights(raw, "Qualifications"),
            "benefits": self._join_highlights(raw, "Benefits"),
            "skills_required": skills if isinstance(skills, list) else [],
            "industry": self._clip(raw.get("employer_company_type"), 255),
            "posted_date": posted_date,
            "application_url": self._clip(raw.get("job_apply_link"), 500),
            "source_platform": self._clip(raw.get("job_publisher"), 100),
            "cached_at": now,
            "expires_at": now + timedelta(hours=CACHE_TTL_HOURS),
            "is_active": True,
        }

    @staticmethod
    def _clip(value: Optional[str], max_len: int) -> Optional[str]:
        """Truncate a string to fit its column, preserving None."""
        if value is None:
            return None
        text = str(value)
        return text[:max_len] if len(text) > max_len else text

    @staticmethod
    def _to_int(value: Any) -> Optional[int]:
        """Coerce JSearch numeric fields (which may be float/str) to int, or None."""
        if value is None:
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _join_highlights(raw: Dict[str, Any], key: str) -> Optional[str]:
        highlights = raw.get("job_highlights") or {}
        items = highlights.get(key) or []
        return "\n".join(items) if items else None

    @staticmethod
    def _map_experience_level(raw: Dict[str, Any]) -> Optional[str]:
        """Map JSearch job requirement flags to entry/mid/senior."""
        reqs = raw.get("job_required_experience") or {}
        months = reqs.get("required_experience_in_months")
        if months is None:
            return None
        years = months / 12.0
        if years <= 2:
            return "entry"
        if years <= 5:
            return "mid"
        return "senior"

    # ------------------------------------------------------------------ details
    async def get_job_details(self, user_id: uuid.UUID, job_id: uuid.UUID) -> Dict[str, Any]:
        job = await self.repo.get_by_id(job_id)
        if not job:
            raise NotFoundError("Không tìm thấy tin tuyển dụng")

        await self.repo.add_interaction(user_id, job_id, "viewed")
        bookmarked_ids = await self.repo.get_bookmarked_job_ids(user_id)
        return self._serialize_job(job, is_bookmarked=job_id in bookmarked_ids, full=True)

    # ------------------------------------------------------------------ bookmark
    async def bookmark_job(self, user_id: uuid.UUID, job_id: uuid.UUID) -> bool:
        job = await self.repo.get_by_id(job_id)
        if not job:
            raise NotFoundError("Không tìm thấy tin tuyển dụng")
        await self.repo.add_interaction(user_id, job_id, "bookmarked")
        return True

    async def unbookmark_job(self, user_id: uuid.UUID, job_id: uuid.UUID) -> bool:
        await self.repo.remove_interaction(user_id, job_id, "bookmarked")
        return False

    async def get_bookmarks(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        rows = await self.repo.get_bookmarks(user_id)
        return [
            {
                "job": self._serialize_job(job, is_bookmarked=True),
                "bookmarked_at": bookmarked_at,
            }
            for job, bookmarked_at in rows
        ]

    # ------------------------------------------------------------ saved searches
    async def create_saved_search(
        self, user_id: uuid.UUID, name: str, criteria: Dict[str, Any], alert_frequency: str
    ) -> Dict[str, Any]:
        saved = SavedSearch(
            user_id=user_id,
            name=name,
            search_criteria=criteria,
            alert_frequency=alert_frequency,
            is_active=True,
        )
        await self.repo.create_saved_search(saved)
        return self._serialize_saved_search(saved)

    async def list_saved_searches(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        rows = await self.repo.list_saved_searches(user_id)
        return [self._serialize_saved_search(s) for s in rows]

    # ------------------------------------------------------------ recommendations
    async def get_recommendations(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Rank active cached jobs by skill overlap with the candidate profile."""
        profile = await self.profile_repo.get_by_user_id(user_id)
        profile_skills = set()
        if profile and profile.technical_skills:
            for s in profile.technical_skills:
                name = s.get("name") if isinstance(s, dict) else s
                if name:
                    profile_skills.add(str(name).lower().strip())

        # Pull a pool of recent active jobs to rank.
        jobs, _ = await self.repo.search(page=1, per_page=100)

        scored: List[tuple] = []
        for job in jobs:
            job_skills = set()
            for s in (job.skills_required or []):
                if s:
                    job_skills.add(str(s).lower().strip())
            if not job_skills or not profile_skills:
                score = 0.0
                reason = "Gợi ý dựa trên các tin tuyển dụng mới nhất"
            else:
                overlap = profile_skills & job_skills
                score = round(len(overlap) / len(job_skills) * 100.0, 2)
                reason = (
                    f"Trùng khớp {len(overlap)}/{len(job_skills)} kỹ năng: "
                    + ", ".join(sorted(overlap)) if overlap
                    else "Chưa trùng kỹ năng nhưng phù hợp lĩnh vực"
                )
            scored.append((job, score, reason))

        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:20]

        # Persist recommendation cache (replace previous set).
        records = [
            JobRecommendation(
                user_id=user_id,
                job_id=job.id,
                recommendation_score=score,
                recommendation_reason=reason,
                algorithm_version=RECOMMENDATION_ALGO_VERSION,
            )
            for job, score, reason in top
        ]
        await self.repo.replace_recommendations(user_id, records)

        return [
            {
                "job": self._serialize_job(job, is_bookmarked=False),
                "recommendation_score": score,
                "recommendation_reason": reason,
            }
            for job, score, reason in top
        ]

    # ------------------------------------------------------------ serialization
    @staticmethod
    def _serialize_job(job: Job, is_bookmarked: bool, full: bool = False) -> Dict[str, Any]:
        salary_range = None
        if job.salary_min or job.salary_max:
            lo = f"{job.salary_min:,}" if job.salary_min else "?"
            hi = f"{job.salary_max:,}" if job.salary_max else "?"
            salary_range = f"{lo} - {hi} {job.salary_currency}"

        base = {
            "id": str(job.id),
            "external_id": job.external_job_id,
            "title": job.title,
            "company": job.company_name,
            "company_logo_url": job.company_logo_url,
            "location": job.location,
            "employment_type": job.employment_type,
            "experience_level": job.experience_level,
            "salary_range": salary_range,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "skills_required": job.skills_required or [],
            "posted_date": job.posted_date,
            "application_url": job.application_url,
            "is_bookmarked": is_bookmarked,
        }
        if full:
            base.update({
                "description": job.description,
                "requirements": job.requirements,
                "benefits": job.benefits,
                "industry": job.industry,
                "source_platform": job.source_platform,
                "job_type": job.job_type,
            })
        return base

    @staticmethod
    def _serialize_saved_search(s: SavedSearch) -> Dict[str, Any]:
        return {
            "id": str(s.id),
            "name": s.name,
            "search_criteria": s.search_criteria,
            "alert_frequency": s.alert_frequency,
            "is_active": s.is_active,
            "created_at": s.created_at,
        }
