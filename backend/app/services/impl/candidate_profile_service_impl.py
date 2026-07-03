import uuid
import logging
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.base import ValidationError, NotFoundError
from app.models.candidate_profile import CandidateProfile, ProfileCompleteness, ProfileUpdate
from app.repositories.candidate_profile_repository import CandidateProfileRepository
from app.services.interfaces.candidate_profile_service import ICandidateProfileService

logger = logging.getLogger(__name__)

class CandidateProfileServiceImpl(ICandidateProfileService):
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CandidateProfileRepository(db)

    async def get_profile(self, user_id: uuid.UUID) -> CandidateProfile:
        profile = await self.repo.get_by_user_id(user_id)
        if not profile:
            # Create default empty profile
            profile = CandidateProfile(
                user_id=user_id,
                completeness_score=0.00,
                profile_strength="basic",
                is_public=False,
                is_searchable=True,
                work_experience=[],
                education=[],
                technical_skills=[],
                soft_skills=[],
                certifications=[],
                languages=[],
                projects=[],
                achievements=[]
            )
            await self.repo.create(profile)
            await self.db.flush()
            # Calculate initial completeness
            await self._update_profile_completeness(profile)
        return profile

    async def update_profile_section(
        self, 
        user_id: uuid.UUID, 
        section: str, 
        data: Dict[str, Any]
    ) -> CandidateProfile:
        profile = await self.repo.get_by_user_id(user_id)
        if not profile:
            raise NotFoundError("Không tìm thấy hồ sơ ứng viên")

        old_val = None
        new_val = data

        # Update specific section
        if section == "personal_info":
            old_val = {
                "full_name": profile.full_name,
                "email": profile.email,
                "phone": profile.phone,
                "location": profile.location,
                "linkedin_url": profile.linkedin_url,
                "portfolio_url": profile.portfolio_url,
                "github_url": profile.github_url,
                "website_url": profile.website_url
            }
            profile.full_name = data.get("full_name", profile.full_name)
            profile.email = data.get("email", profile.email)
            profile.phone = data.get("phone", profile.phone)
            profile.location = data.get("location", profile.location)
            profile.linkedin_url = data.get("linkedin_url", profile.linkedin_url)
            profile.portfolio_url = data.get("portfolio_url", profile.portfolio_url)
            profile.github_url = data.get("github_url", profile.github_url)
            profile.website_url = data.get("website_url", profile.website_url)

        elif section == "professional_summary":
            old_val = {
                "professional_summary": profile.professional_summary,
                "career_objective": profile.career_objective,
                "years_of_experience": profile.years_of_experience,
                "current_role": profile.current_role,
                "current_company": profile.current_company,
                "salary_expectation_min": profile.salary_expectation_min,
                "salary_expectation_max": profile.salary_expectation_max,
                "availability": profile.availability
            }
            profile.professional_summary = data.get("professional_summary", profile.professional_summary)
            profile.career_objective = data.get("career_objective", profile.career_objective)
            profile.years_of_experience = data.get("years_of_experience", profile.years_of_experience)
            profile.current_role = data.get("current_role", profile.current_role)
            profile.current_company = data.get("current_company", profile.current_company)
            profile.salary_expectation_min = data.get("salary_expectation_min", profile.salary_expectation_min)
            profile.salary_expectation_max = data.get("salary_expectation_max", profile.salary_expectation_max)
            profile.availability = data.get("availability", profile.availability)

        elif section == "work_experience":
            old_val = profile.work_experience
            profile.work_experience = data.get("work_experience", [])

        elif section == "education":
            old_val = profile.education
            profile.education = data.get("education", [])

        elif section == "technical_skills":
            old_val = profile.technical_skills
            profile.technical_skills = data.get("technical_skills", [])

        elif section == "soft_skills":
            old_val = profile.soft_skills
            profile.soft_skills = data.get("soft_skills", [])

        elif section == "certifications":
            old_val = profile.certifications
            profile.certifications = data.get("certifications", [])

        elif section == "languages":
            old_val = profile.languages
            profile.languages = data.get("languages", [])

        elif section == "projects":
            old_val = profile.projects
            profile.projects = data.get("projects", [])

        elif section == "achievements":
            old_val = profile.achievements
            profile.achievements = data.get("achievements", [])

        else:
            raise ValidationError(f"Phần hồ sơ không hợp lệ: {section}")

        profile.last_updated_section = section
        
        # Log update details in audit trail
        update_log = ProfileUpdate(
            profile_id=profile.id,
            user_id=user_id,
            section_name=section,
            old_value=old_val,
            new_value=new_val,
            update_source="manual"
        )
        await self.repo.create_update_log(update_log)

        # Recalculate completeness
        await self._update_profile_completeness(profile)
        await self.db.flush()

        return profile

    async def get_completeness(self, user_id: uuid.UUID) -> Dict[str, Any]:
        # Tự động tạo hồ sơ trống nếu chưa tồn tại
        profile = await self.get_profile(user_id)

        # Get detailed breakdown records
        records = await self.repo.get_completeness_by_profile_id(profile.id)
        
        section_scores = {}
        missing_fields = {}
        suggestions = []

        for r in records:
            section_scores[r.section_name] = float(r.completeness_percentage)
            missing_fields[r.section_name] = r.missing_fields or []
            
            # Map suggestion lists
            sug_list = r.suggestions or []
            for s in sug_list:
                suggestions.append({
                    "section": r.section_name,
                    "message": s,
                    "priority": "high" if float(r.completeness_percentage) < 50.0 else "medium"
                })

        return {
            "overall_score": float(profile.completeness_score),
            "section_scores": section_scores,
            "suggestions": suggestions,
            "missing_fields": missing_fields
        }

    async def export_profile(self, user_id: uuid.UUID, format: str) -> Dict[str, Any]:
        # Tự động tạo hồ sơ trống nếu chưa tồn tại
        profile = await self.get_profile(user_id)

        import os
        export_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            "static", 
            "exports"
        )
        os.makedirs(export_dir, exist_ok=True)

        filename = f"profile_{user_id}_{uuid.uuid4().hex[:8]}.{format}"
        file_path = os.path.join(export_dir, filename)

        profile_data = {
            "full_name": profile.full_name,
            "email": profile.email,
            "phone": profile.phone,
            "location": profile.location,
            "linkedin_url": profile.linkedin_url,
            "portfolio_url": profile.portfolio_url,
            "github_url": profile.github_url,
            "website_url": profile.website_url,
            "professional_summary": profile.professional_summary,
            "career_objective": profile.career_objective,
            "years_of_experience": profile.years_of_experience,
            "current_role": profile.current_role,
            "current_company": profile.current_company,
            "work_experience": profile.work_experience,
            "education": profile.education,
            "technical_skills": profile.technical_skills,
            "soft_skills": profile.soft_skills,
            "certifications": profile.certifications,
            "languages": profile.languages,
            "projects": profile.projects,
            "achievements": profile.achievements
        }

        if format == "json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
        else:
            # Simple formatted text/pdf mock
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"MOCKAI CANDIDATE PROFILE EXPORT - {profile.full_name or 'N/A'}\n")
                f.write("="*60 + "\n\n")
                f.write(f"Email: {profile.email or 'N/A'}\n")
                f.write(f"Phone: {profile.phone or 'N/A'}\n")
                f.write(f"Location: {profile.location or 'N/A'}\n\n")
                f.write(f"Summary: {profile.professional_summary or 'N/A'}\n\n")
                f.write(f"Skills: {', '.join([s.get('name', '') for s in (profile.technical_skills or [])])}\n\n")
                f.write("Work Experience:\n")
                for w in (profile.work_experience or []):
                    f.write(f"- {w.get('title')} at {w.get('company')} ({w.get('start_date')} - {w.get('end_date') or 'Present'})\n")
                    f.write(f"  Description: {w.get('description')}\n")
            # Rename output format suffix to pdf for mock download compatibility
            if format == "pdf":
                pdf_path = file_path.replace(".pdf", ".pdf")
                # In real scenario we'd use reportlab, here we just save text file named .pdf
                pass

        return {
            "download_url": f"/static/exports/{filename}",
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
            "file_name": filename
        }

    async def _update_profile_completeness(self, profile: CandidateProfile) -> None:
        """Private helper to calculate and save section completeness + suggestions."""
        # Clean current records first to avoid duplicates
        await self.repo.delete_completeness_records(profile.id)

        # 1. Personal Info (25%)
        p_fields = ["full_name", "email", "phone", "location"]
        p_missing = []
        p_sugs = []
        for f in p_fields:
            val = getattr(profile, f, None)
            if not val:
                p_missing.append(f)
                p_sugs.append(f"Vui lòng bổ sung {self._field_label(f)}")
        p_score = ((len(p_fields) - len(p_missing)) / len(p_fields)) * 25.0
        
        await self.repo.create_or_update_completeness(ProfileCompleteness(
            profile_id=profile.id,
            section_name="personal_info",
            completeness_percentage=p_score,
            missing_fields=p_missing,
            suggestions=p_sugs
        ))

        # 2. Work Experience (35%)
        work_list = profile.work_experience or []
        w_score = 35.0
        w_missing = []
        w_sugs = []
        if not work_list:
            w_score = 0.0
            w_missing.append("work_experience")
            w_sugs.append("Vui lòng thêm ít nhất một kinh nghiệm làm việc")
        else:
            # Check length/completeness of entries
            invalid_entries = 0
            for w in work_list:
                if not w.get("title") or not w.get("company") or not w.get("description"):
                    invalid_entries += 1
            if invalid_entries > 0:
                w_score -= 10.0
                w_sugs.append("Một số kinh nghiệm làm việc của bạn thiếu mô tả chi tiết hoặc thông tin chức danh")
        
        await self.repo.create_or_update_completeness(ProfileCompleteness(
            profile_id=profile.id,
            section_name="work_experience",
            completeness_percentage=w_score,
            missing_fields=w_missing,
            suggestions=w_sugs
        ))

        # 3. Education (15%)
        edu_list = profile.education or []
        e_score = 15.0
        e_missing = []
        e_sugs = []
        if not edu_list:
            e_score = 0.0
            e_missing.append("education")
            e_sugs.append("Vui lòng thêm thông tin học vấn học tập")
        
        await self.repo.create_or_update_completeness(ProfileCompleteness(
            profile_id=profile.id,
            section_name="education",
            completeness_percentage=e_score,
            missing_fields=e_missing,
            suggestions=e_sugs
        ))

        # 4. Technical & Soft Skills (20%)
        tech = profile.technical_skills or []
        s_score = 0.0
        s_missing = []
        s_sugs = []
        if len(tech) >= 5:
            s_score = 20.0
        else:
            s_score = (len(tech) / 5.0) * 20.0
            s_missing.append("technical_skills")
            s_sugs.append("Nên bổ sung tối thiểu 5 kỹ năng chuyên môn khác nhau")
        
        await self.repo.create_or_update_completeness(ProfileCompleteness(
            profile_id=profile.id,
            section_name="skills",
            completeness_percentage=s_score,
            missing_fields=s_missing,
            suggestions=s_sugs
        ))

        # 5. Others (5% bonus cap)
        others_score = 0.0
        others_sugs = []
        if profile.certifications:
            others_score += 1.25
        else:
            others_sugs.append("Bổ sung chứng chỉ chuyên môn (nếu có)")
        if profile.projects:
            others_score += 1.25
        else:
            others_sugs.append("Thêm các dự án thực tế để tăng tính cạnh tranh")
        if profile.languages:
            others_score += 1.25
        else:
            others_sugs.append("Thêm các chứng chỉ ngoại ngữ và mức độ thành thạo")
        if profile.achievements:
            others_score += 1.25
        else:
            others_sugs.append("Thêm giải thưởng, hoạt động ngoại khóa")
        
        await self.repo.create_or_update_completeness(ProfileCompleteness(
            profile_id=profile.id,
            section_name="others",
            completeness_percentage=others_score,
            missing_fields=[],
            suggestions=others_sugs
        ))

        # Recalculate total score
        total_score = p_score + w_score + e_score + s_score + others_score
        profile.completeness_score = min(100.0, total_score)
        
        # Calculate strength level
        if total_score <= 40:
            profile.profile_strength = "basic"
        elif total_score <= 70:
            profile.profile_strength = "good"
        elif total_score <= 90:
            profile.profile_strength = "strong"
        else:
            profile.profile_strength = "excellent"

    def _field_label(self, field: str) -> str:
        mapping = {
            "full_name": "Họ và tên",
            "email": "Email liên hệ",
            "phone": "Số điện thoại",
            "location": "Địa chỉ sinh sống"
        }
        return mapping.get(field, field)
