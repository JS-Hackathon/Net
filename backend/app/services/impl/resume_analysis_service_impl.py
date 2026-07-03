import uuid
import logging
import time
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.base import ValidationError, NotFoundError
from app.models.resume_analysis import ResumeAnalysis, ParsingMetric
from app.models.candidate_profile import CandidateProfile
from app.repositories.resume_repository import ResumeRepository
from app.repositories.resume_analysis_repository import ResumeAnalysisRepository
from app.repositories.candidate_profile_repository import CandidateProfileRepository
from app.services.interfaces.resume_analysis_service import IResumeAnalysisService
from app.services.interfaces.storage_service import StorageService
from app.services.interfaces.ai_provider import AIProvider
from app.services.text_extractor import TextExtractor

logger = logging.getLogger(__name__)

class ResumeAnalysisServiceImpl(IResumeAnalysisService):
    def __init__(
        self, 
        db: AsyncSession, 
        storage_service: StorageService, 
        ai_provider: AIProvider,
        profile_service: Any = None  # Will inject profile service if needed, or query directly
    ):
        self.db = db
        self.repo = ResumeAnalysisRepository(db)
        self.resume_repo = ResumeRepository(db)
        self.profile_repo = CandidateProfileRepository(db)
        self.storage = storage_service
        self.ai = ai_provider

    async def parse_resume_background(
        self, 
        user_id: uuid.UUID, 
        resume_id: uuid.UUID
    ) -> ResumeAnalysis:
        # Verify resume exists and belongs to user
        resume = await self.resume_repo.get_by_id(resume_id)
        if not resume or resume.user_id != user_id:
            raise NotFoundError("Không tìm thấy CV yêu cầu")

        # Create new analysis entry
        analysis = ResumeAnalysis(
            resume_id=resume_id,
            user_id=user_id,
            status="pending",
            retry_count=0,
            max_retries=3
        )
        await self.repo.create(analysis)

        # Update resume status
        resume.upload_status = "processing"
        resume.text_extraction_status = "processing"
        await self.db.flush()

        return analysis

    async def run_extraction_and_parsing_sync(self, analysis_id: uuid.UUID) -> None:
        from app.core.database import async_session_factory
        
        async with async_session_factory() as session:
            repo = ResumeAnalysisRepository(session)
            resume_repo = ResumeRepository(session)
            
            analysis = await repo.get_by_id(analysis_id)
            if not analysis:
                logger.error(f"Analysis {analysis_id} not found")
                return

            analysis.status = "processing"
            await session.commit()

            start_time = time.time()

            try:
                resume = await resume_repo.get_by_id(analysis.resume_id)
                if not resume:
                    raise ValueError("Không tìm thấy CV tương ứng với phân tích")

                # 1. Download file
                file_bytes = await self.storage.download_file(resume.filename)

                # 2. Extract Text
                raw_text = TextExtractor.extract_text(file_bytes, resume.file_type)
                analysis.raw_text = raw_text
                resume.text_extraction_status = "completed"
                await session.flush()

                # 3. Call AI parsing
                parsed_json = await self.ai.parse_resume(raw_text)
                
                if "error" in parsed_json:
                    raise ValueError(parsed_json.get("details", "AI Parsing failed"))

                # Normalize parsed data to handle potential schema variations
                parsed_data = self._normalize_parsed_data(parsed_json)
                analysis.parsed_data = parsed_data

                # 4. Calculate confidence scores
                field_scores, overall_score = self._calculate_confidence(parsed_data)
                analysis.confidence_score = overall_score

                # Save metrics
                for field, score in field_scores.items():
                    metric = ParsingMetric(
                        analysis_id=analysis_id,
                        field_name=field,
                        confidence_score=score,
                        extraction_method="ai_primary",
                        validation_status="valid" if score >= 70 else "needs_review"
                    )
                    await repo.create_metric(metric)

                # 5. Set status based on confidence score threshold (70%)
                if overall_score >= 70.0:
                    analysis.status = "completed"
                    # Automatically sync to Candidate Profile
                    await self._sync_to_profile(analysis.user_id, parsed_data, analysis_id, session)
                else:
                    analysis.status = "reviewing"  # User needs to review low confidence fields

                # Finalize analysis metadata
                analysis.parsing_duration = int((time.time() - start_time) * 1000)
                analysis.completed_at = datetime.now(timezone.utc)
                resume.upload_status = "completed"
                
                await session.commit()
                logger.info(f"Analysis {analysis_id} completed successfully in {analysis.parsing_duration}ms")

            except Exception as e:
                logger.error(f"Error processing analysis {analysis_id}: {e}", exc_info=True)
                await session.rollback()
                
                # Update status on failure
                analysis = await repo.get_by_id(analysis_id)
                if analysis:
                    analysis.status = "failed"
                    analysis.error_message = str(e)
                    analysis.completed_at = datetime.now(timezone.utc)
                
                resume = await resume_repo.get_by_id(analysis.resume_id)
                if resume:
                    resume.upload_status = "failed"
                    resume.text_extraction_status = "failed"
                
                await session.commit()

    async def get_analysis(self, user_id: uuid.UUID, analysis_id: uuid.UUID) -> ResumeAnalysis:
        analysis = await self.repo.get_by_id(analysis_id)
        if not analysis or analysis.user_id != user_id:
            raise NotFoundError("Không tìm thấy kết quả phân tích yêu cầu")
        return analysis

    async def get_parsing_status(self, user_id: uuid.UUID, analysis_id: uuid.UUID) -> Dict[str, Any]:
        analysis = await self.repo.get_by_id(analysis_id)
        if not analysis or analysis.user_id != user_id:
            raise NotFoundError("Không tìm thấy thông tin phân tích yêu cầu")

        status_mapping = {
            "pending": (15, "Đang chuẩn bị file và trích xuất văn bản..."),
            "processing": (50, "AI đang phân tích và chuẩn hóa nội dung..."),
            "reviewing": (100, "Phân tích hoàn tất. Yêu cầu xem lại thông tin tin cậy thấp."),
            "completed": (100, "Hoàn thành phân tích CV!"),
            "failed": (100, f"Thất bại: {analysis.error_message or 'Lỗi không xác định'}")
        }

        progress, step = status_mapping.get(analysis.status, (0, "Bắt đầu..."))
        
        return {
            "status": analysis.status,
            "progress_percentage": progress,
            "estimated_completion": None,
            "current_step": step
        }

    async def submit_review(
        self, 
        user_id: uuid.UUID, 
        analysis_id: uuid.UUID, 
        corrections: Dict[str, Any], 
        approved: bool
    ) -> ResumeAnalysis:
        analysis = await self.repo.get_by_id(analysis_id)
        if not analysis or analysis.user_id != user_id:
            raise NotFoundError("Không tìm thấy kết quả phân tích yêu cầu")

        if analysis.status not in ("reviewing", "completed"):
            raise ValidationError("Chỉ có thể phê duyệt phân tích ở trạng thái hoàn thành hoặc chờ duyệt")

        # Apply corrections to parsed_data
        updated_data = dict(analysis.parsed_data or {})
        for path, value in corrections.items():
            self._set_nested_value(updated_data, path, value)

        analysis.parsed_data = updated_data
        analysis.status = "completed"
        analysis.reviewed_at = datetime.now(timezone.utc)
        analysis.reviewed_by = user_id
        
        # Save metrics for manual modifications
        for path in corrections.keys():
            metric = ParsingMetric(
                analysis_id=analysis_id,
                field_name=path.split(".")[-1],
                confidence_score=100.0,
                extraction_method="manual",
                validation_status="valid"
            )
            await self.repo.create_metric(metric)

        # Sync to profile
        await self._sync_to_profile(user_id, updated_data, analysis_id, self.db)
        await self.db.flush()

        return analysis

    async def retry_parsing(self, user_id: uuid.UUID, analysis_id: uuid.UUID) -> ResumeAnalysis:
        analysis = await self.repo.get_by_id(analysis_id)
        if not analysis or analysis.user_id != user_id:
            raise NotFoundError("Không tìm thấy thông tin phân tích yêu cầu")

        if analysis.status != "failed":
            raise ValidationError("Chỉ có thể thử lại các phân tích đã bị thất bại")

        analysis.status = "pending"
        analysis.retry_count += 1
        analysis.error_message = None
        
        # Update resume status
        resume = await self.resume_repo.get_by_id(analysis.resume_id)
        if resume:
            resume.upload_status = "processing"
            resume.text_extraction_status = "processing"

        await self.db.flush()
        return analysis

    def _normalize_parsed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Maps varying schemas returned by AI to standard Candidate Profile JSON schema."""
        normalized = {}
        
        # 1. Personal Info mapping
        p_info = data.get("personal_info", {})
        if not p_info:
            # Handle fallback if AI returned flat root personal keys
            p_info = {
                "full_name": data.get("full_name") or data.get("name"),
                "email": data.get("email"),
                "phone": data.get("phone") or data.get("mobile"),
                "location": data.get("location") or data.get("address"),
                "linkedin_url": data.get("linkedin"),
                "portfolio_url": data.get("portfolio"),
                "github_url": data.get("github"),
                "website_url": data.get("website")
            }
        else:
            p_info = {
                "full_name": p_info.get("full_name") or p_info.get("name"),
                "email": p_info.get("email"),
                "phone": p_info.get("phone") or p_info.get("mobile"),
                "location": p_info.get("location") or p_info.get("address"),
                "linkedin_url": p_info.get("linkedin_url") or p_info.get("linkedin"),
                "portfolio_url": p_info.get("portfolio_url") or p_info.get("portfolio"),
                "github_url": p_info.get("github_url") or p_info.get("github"),
                "website_url": p_info.get("website_url") or p_info.get("website")
            }
        normalized["personal_info"] = p_info

        # 2. Professional Summary
        normalized["professional_summary"] = data.get("professional_summary") or data.get("summary")
        normalized["career_objective"] = data.get("career_objective") or data.get("objective")
        normalized["years_of_experience"] = data.get("years_of_experience") or data.get("experience_years")
        normalized["current_role"] = data.get("current_role")
        normalized["current_company"] = data.get("current_company")

        # 3. Work Experience mapping
        work = data.get("work_experience") or data.get("experience") or []
        normalized_work = []
        for w in work:
            if isinstance(w, str):
                continue
            normalized_work.append({
                "title": w.get("title") or w.get("role") or "Unknown Role",
                "company": w.get("company") or "Unknown Company",
                "location": w.get("location"),
                "start_date": str(w.get("start_date") or w.get("duration", "").split("-")[0] or "2020"),
                "end_date": str(w.get("end_date") or (w.get("duration", "").split("-")[1] if "-" in w.get("duration", "") else None)),
                "is_current": w.get("is_current") or ("present" in str(w.get("duration", "")).lower() or "hiện tại" in str(w.get("duration", "")).lower()),
                "description": w.get("description") or "\n".join(w.get("responsibilities", [])),
                "key_achievements": w.get("key_achievements") or [],
                "technologies_used": w.get("technologies_used") or w.get("technologies") or []
            })
        normalized["work_experience"] = normalized_work

        # 4. Education mapping
        edu = data.get("education") or []
        normalized_edu = []
        for e in edu:
            if isinstance(e, str):
                continue
            normalized_edu.append({
                "degree": e.get("degree") or "Bằng cấp",
                "field_of_study": e.get("field_of_study") or e.get("major"),
                "institution": e.get("institution") or e.get("school") or "Trường học",
                "location": e.get("location"),
                "graduation_date": str(e.get("graduation_date") or e.get("graduation_year") or ""),
                "gpa": e.get("gpa"),
                "honors": e.get("honors") or []
            })
        normalized["education"] = normalized_edu

        # 5. Technical Skills mapping
        tech_skills = data.get("technical_skills") or []
        if not tech_skills and data.get("skills"):
            # Handle if AI returned skills as list of strings
            tech_skills = [{"name": s, "category": "General", "proficiency": "Intermediate", "years_experience": None} for s in data.get("skills")]
        normalized_tech = []
        for s in tech_skills:
            if isinstance(s, str):
                normalized_tech.append({"name": s, "category": "General", "proficiency": "Intermediate", "years_experience": None})
            else:
                normalized_tech.append({
                    "name": s.get("name") or "Skill",
                    "category": s.get("category") or "General",
                    "proficiency": s.get("proficiency") or "Intermediate",
                    "years_experience": s.get("years_experience")
                })
        normalized["technical_skills"] = normalized_tech

        # 6. Soft Skills mapping
        soft_skills = data.get("soft_skills") or []
        normalized_soft = []
        for s in soft_skills:
            if isinstance(s, str):
                normalized_soft.append({"name": s, "description": None})
            else:
                normalized_soft.append({
                    "name": s.get("name") or "Soft Skill",
                    "description": s.get("description")
                })
        normalized["soft_skills"] = normalized_soft

        # 7. Other sections
        normalized["certifications"] = data.get("certifications") or []
        # Ensure list of dicts for certifications
        certs = normalized["certifications"]
        normalized_certs = []
        for c in certs:
            if isinstance(c, str):
                normalized_certs.append({
                    "name": c,
                    "issuer": "Unknown",
                    "issue_date": None,
                    "expiry_date": None,
                    "credential_id": None,
                    "verification_url": None
                })
            else:
                normalized_certs.append({
                    "name": c.get("name") or "Certificate",
                    "issuer": c.get("issuer") or "Unknown",
                    "issue_date": c.get("issue_date"),
                    "expiry_date": c.get("expiry_date"),
                    "credential_id": c.get("credential_id"),
                    "verification_url": c.get("verification_url")
                })
        normalized["certifications"] = normalized_certs

        normalized["languages"] = data.get("languages") or []
        normalized["projects"] = data.get("projects") or []
        normalized["achievements"] = data.get("achievements") or []

        return normalized

    def _calculate_confidence(self, data: Dict[str, Any]) -> Tuple[Dict[str, float], float]:
        """Calculates confidence scores based on completeness and formatting of parsed fields."""
        scores = {}
        
        # 1. Personal Info check
        p_info = data.get("personal_info", {})
        p_score = 100.0
        if not p_info.get("full_name"):
            p_score -= 30
        if not p_info.get("email") or not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", p_info.get("email", "")):
            p_score -= 30
        if not p_info.get("phone"):
            p_score -= 20
        scores["personal_info"] = max(0.0, p_score)

        # 2. Work Experience check
        work = data.get("work_experience", [])
        if not work:
            scores["work_experience"] = 50.0  # missing work experience
        else:
            w_score = 100.0
            for w in work:
                if not w.get("title") or not w.get("company"):
                    w_score -= 15
                if not w.get("description") or len(w.get("description", "")) < 20:
                    w_score -= 10
            scores["work_experience"] = max(0.0, w_score)

        # 3. Education check
        edu = data.get("education", [])
        if not edu:
            scores["education"] = 50.0
        else:
            e_score = 100.0
            for e in edu:
                if not e.get("degree") or not e.get("institution"):
                    e_score -= 15
            scores["education"] = max(0.0, e_score)

        # 4. Technical Skills check
        tech = data.get("technical_skills", [])
        if not tech:
            scores["technical_skills"] = 50.0
        else:
            scores["technical_skills"] = 90.0 if any(not s.get("proficiency") for s in tech) else 100.0

        # 5. Soft Skills check
        scores["soft_skills"] = 100.0 if data.get("soft_skills") else 75.0

        # Calculate overall score as weighted average
        weights = {
            "personal_info": 0.15,
            "work_experience": 0.35,
            "education": 0.20,
            "technical_skills": 0.25,
            "soft_skills": 0.05
        }
        
        overall = sum(scores.get(k, 100.0) * w for k, w in weights.items())
        return scores, float(round(overall, 2))

    async def _sync_to_profile(self, user_id: uuid.UUID, parsed_data: Dict[str, Any], analysis_id: uuid.UUID, session: AsyncSession) -> None:
        """Helper to create or update Candidate Profile with parsed data."""
        profile_repo = CandidateProfileRepository(session)
        profile = await profile_repo.get_by_user_id(user_id)
        p_info = parsed_data.get("personal_info", {})
        
        if not profile:
            profile = CandidateProfile(
                user_id=user_id,
                source_analysis_id=analysis_id,
                full_name=p_info.get("full_name"),
                email=p_info.get("email"),
                phone=p_info.get("phone"),
                location=p_info.get("location"),
                linkedin_url=p_info.get("linkedin_url"),
                portfolio_url=p_info.get("portfolio_url"),
                github_url=p_info.get("github_url"),
                website_url=p_info.get("website_url"),
                professional_summary=parsed_data.get("professional_summary"),
                career_objective=parsed_data.get("career_objective"),
                years_of_experience=parsed_data.get("years_of_experience"),
                current_role=parsed_data.get("current_role"),
                current_company=parsed_data.get("current_company"),
                work_experience=parsed_data.get("work_experience"),
                education=parsed_data.get("education"),
                technical_skills=parsed_data.get("technical_skills"),
                soft_skills=parsed_data.get("soft_skills"),
                certifications=parsed_data.get("certifications"),
                languages=parsed_data.get("languages"),
                projects=parsed_data.get("projects"),
                achievements=parsed_data.get("achievements")
            )
            await profile_repo.create(profile)
        else:
            profile.source_analysis_id = analysis_id
            profile.full_name = p_info.get("full_name") or profile.full_name
            profile.email = p_info.get("email") or profile.email
            profile.phone = p_info.get("phone") or profile.phone
            profile.location = p_info.get("location") or profile.location
            profile.linkedin_url = p_info.get("linkedin_url") or profile.linkedin_url
            profile.portfolio_url = p_info.get("portfolio_url") or profile.portfolio_url
            profile.github_url = p_info.get("github_url") or profile.github_url
            profile.website_url = p_info.get("website_url") or profile.website_url
            profile.professional_summary = parsed_data.get("professional_summary") or profile.professional_summary
            profile.career_objective = parsed_data.get("career_objective") or profile.career_objective
            profile.years_of_experience = parsed_data.get("years_of_experience") or profile.years_of_experience
            profile.current_role = parsed_data.get("current_role") or profile.current_role
            profile.current_company = parsed_data.get("current_company") or profile.current_company
            profile.work_experience = parsed_data.get("work_experience")
            profile.education = parsed_data.get("education")
            profile.technical_skills = parsed_data.get("technical_skills")
            profile.soft_skills = parsed_data.get("soft_skills")
            profile.certifications = parsed_data.get("certifications")
            profile.languages = parsed_data.get("languages")
            profile.projects = parsed_data.get("projects")
            profile.achievements = parsed_data.get("achievements")

    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """Sets a value in a nested dict structure using dot-notation (e.g., 'work_experience.0.title')."""
        parts = path.split(".")
        curr = data
        for i, part in enumerate(parts[:-1]):
            # If part is numeric, it is an index in a list
            if part.isdigit():
                idx = int(part)
                curr = curr[idx]
            else:
                curr = curr[part]
        
        # Set final key/index
        last = parts[-1]
        if last.isdigit():
            curr[int(last)] = value
        else:
            curr[last] = value
