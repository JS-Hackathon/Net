# Feature 4: Candidate Profile

## Overview
Implement comprehensive candidate profile management system that allows users to view, edit, and enhance AI-parsed resume data, track profile completeness, and maintain structured career information for all AI-powered features.

## Goal
Provide users with complete control over their professional profile data while maintaining the structured format required for AI features, enabling profile enhancement and ensuring data accuracy through user validation and editing capabilities.

## User Story
As a **Candidate**,
I want to review and edit my AI-generated profile
So that I can ensure accuracy and completeness of my professional information.

As a **Candidate**,
I want to see my profile completeness score
So that I can understand what information to add for better job matching and recommendations.

## Functional Requirements
### Profile Data Management
- Display AI-parsed resume data in structured, editable sections
- Enable manual editing of all profile fields with validation
- Support adding information not captured by AI parsing
- Track profile completeness with scoring and suggestions
- Version control for profile changes with audit trail
- Profile export functionality (PDF, JSON formats)

### Profile Sections
- **Personal Information**: Contact details, location, professional links
- **Professional Summary**: Career objective and summary statement
- **Work Experience**: Detailed job history with achievements and technologies
- **Education**: Academic background with degrees, institutions, honors
- **Skills**: Technical and soft skills with proficiency levels and categories
- **Certifications**: Professional certifications with dates and verification
- **Projects**: Personal and professional projects with descriptions
- **Languages**: Language proficiency levels
- **Achievements**: Awards, publications, volunteer work

### Profile Enhancement Features
- Completeness scoring with section-by-section breakdown
- Suggestions for missing information based on industry standards
- Profile strength indicators for job matching readiness
- Skills gap identification compared to target roles
- Profile optimization tips for better visibility

## Non-functional Requirements
- Profile load time: <2 seconds for complete profile data
- Auto-save functionality: Save changes within 3 seconds of editing
- Data validation: Real-time validation with immediate feedback
- Mobile responsiveness: Full functionality on mobile devices
- Accessibility: WCAG 2.1 AA compliance for all profile interfaces
- Data integrity: Profile changes tracked with complete audit trail

## Backend Tasks
### Database Schema
```sql
-- Comprehensive candidate profiles
CREATE TABLE candidate_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    source_analysis_id UUID REFERENCES resume_analyses(id),
    
    -- Personal Information
    full_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    location VARCHAR(255),
    linkedin_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    github_url VARCHAR(500),
    website_url VARCHAR(500),
    
    -- Professional Summary
    professional_summary TEXT,
    career_objective TEXT,
    years_of_experience INTEGER,
    current_role VARCHAR(255),
    current_company VARCHAR(255),
    salary_expectation_min INTEGER,
    salary_expectation_max INTEGER,
    availability VARCHAR(50), -- immediate, 2_weeks, 1_month, etc.
    
    -- Structured Data (JSONB for flexibility)
    work_experience JSONB, -- Array of work experience objects
    education JSONB, -- Array of education objects
    technical_skills JSONB, -- Array of technical skills with categories
    soft_skills JSONB, -- Array of soft skills
    certifications JSONB, -- Array of certifications
    languages JSONB, -- Array of languages with proficiency
    projects JSONB, -- Array of projects
    achievements JSONB, -- Array of achievements and awards
    
    -- Profile Metadata
    completeness_score DECIMAL(5,2) DEFAULT 0.00, -- 0-100
    last_updated_section VARCHAR(100),
    profile_strength VARCHAR(20) DEFAULT 'basic', -- basic, good, strong, excellent
    is_public BOOLEAN DEFAULT FALSE,
    is_searchable BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_viewed_at TIMESTAMP
);

-- Profile completeness tracking by section
CREATE TABLE profile_completeness (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES candidate_profiles(id) ON DELETE CASCADE,
    section_name VARCHAR(100) NOT NULL,
    completeness_percentage DECIMAL(5,2) NOT NULL,
    missing_fields JSONB, -- Array of missing field names
    suggestions JSONB, -- Array of improvement suggestions
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Profile update history for audit trail
CREATE TABLE profile_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES candidate_profiles(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    section_name VARCHAR(100) NOT NULL,
    field_name VARCHAR(255),
    old_value JSONB,
    new_value JSONB,
    update_source VARCHAR(50) DEFAULT 'manual', -- manual, ai_parsing, import, sync
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_candidate_profiles_user_id ON candidate_profiles(user_id);
CREATE INDEX idx_candidate_profiles_completeness ON candidate_profiles(completeness_score);
CREATE INDEX idx_profile_updates_profile_id ON profile_updates(profile_id);
CREATE INDEX idx_profile_updates_created_at ON profile_updates(created_at);
```

### Profile Service Implementation
```python
class CandidateProfileService:
    def __init__(self, db: Database, completeness_calculator: CompletenessCalculator):
        self.db = db
        self.completeness_calculator = completeness_calculator
    
    async def create_profile_from_analysis(self, user_id: UUID, analysis_id: UUID) -> CandidateProfile:
        # Retrieve parsed resume data
        analysis = await self.get_resume_analysis(analysis_id)
        
        # Transform AI data to profile structure
        profile_data = await self.transform_analysis_to_profile(analysis.parsed_data)
        
        # Create profile record
        profile = await self.create_profile(user_id, profile_data, analysis_id)
        
        # Calculate initial completeness score
        await self.update_completeness_score(profile.id)
        
        return profile
    
    async def get_user_profile(self, user_id: UUID) -> CandidateProfile:
        # Retrieve complete profile with all sections
        # Include completeness scores and suggestions
        # Return structured profile data
        
    async def update_profile_section(self, profile_id: UUID, section: str, data: Dict) -> ProfileUpdateResult:
        # Validate section data
        # Update specific profile section
        # Recalculate completeness score
        # Log update in audit trail
        # Return update result with new scores
        
    async def calculate_profile_completeness(self, profile_id: UUID) -> CompletenessResult:
        # Analyze all profile sections
        # Calculate section-specific scores
        # Generate improvement suggestions
        # Return comprehensive completeness data
        
    async def export_profile(self, profile_id: UUID, format: str) -> ExportResult:
        # Generate profile export in requested format
        # Include all sections with proper formatting
        # Return download URL or file data
```

## Frontend Tasks
### Profile Management Components
```tsx
interface ProfileEditorProps {
  profile: CandidateProfile;
  onSave: (section: string, data: any) => Promise<void>;
  onExport: (format: 'pdf' | 'json') => void;
}

const ProfileEditor: React.FC<ProfileEditorProps> = ({ profile, onSave, onExport }) => {
  const [activeSection, setActiveSection] = useState('personal');
  const [unsavedChanges, setUnsavedChanges] = useState<Record<string, any>>({});
  
  // Section navigation
  // Auto-save functionality
  // Unsaved changes warning
  // Export functionality
};
```

### Section-Specific Editors
```tsx
// Personal Information Editor
const PersonalInfoEditor: React.FC<{
  data: PersonalInfo;
  onChange: (data: PersonalInfo) => void;
}> = ({ data, onChange }) => {
  // Form fields for contact information
  // URL validation for professional profiles
  // Location autocomplete
  // Real-time validation feedback
};

// Work Experience Editor
const WorkExperienceEditor: React.FC<{
  experiences: WorkExperience[];
  onChange: (experiences: WorkExperience[]) => void;
}> = ({ experiences, onChange }) => {
  // Dynamic list of work experiences
  // Add/remove/reorder functionality
  // Date pickers with validation
  // Rich text editor for descriptions
  // Technology tags management
};

// Skills Management
const SkillsEditor: React.FC<{
  technicalSkills: TechnicalSkill[];
  softSkills: SoftSkill[];
  onChange: (skills: { technical: TechnicalSkill[]; soft: SoftSkill[] }) => void;
}> = ({ technicalSkills, softSkills, onChange }) => {
  // Skill categories and proficiency levels
  // Auto-complete for common skills
  // Years of experience tracking
  // Skill endorsement system (future)
};
```

### Profile Completeness Components
```tsx
const ProfileCompleteness: React.FC<{
  completeness: CompletenessData;
  onSectionClick: (section: string) => void;
}> = ({ completeness, onSectionClick }) => {
  // Overall completeness score with progress ring
  // Section-by-section breakdown
  // Suggestions for improvement
  // Quick action buttons to complete sections
};

const CompletenessIndicator: React.FC<{
  score: number;
  size?: 'sm' | 'md' | 'lg';
}> = ({ score, size = 'md' }) => {
  // Circular progress indicator
  // Color-coded based on completeness level
  // Animated progress changes
};
```

## API Endpoints
### Profile Management Endpoints
```
GET /profile
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    id: "uuid",
    personal_info: { /* personal information */ },
    work_experience: [ /* work experience array */ ],
    education: [ /* education array */ ],
    technical_skills: [ /* skills array */ ],
    completeness_score: 85.5,
    profile_strength: "strong",
    last_updated: "2024-01-01T00:00:00Z"
  }
}

PUT /profile
Headers: Authorization: Bearer <token>
Body: {
  section: "work_experience",
  data: {
    // Section-specific data structure
  }
}
Response: {
  success: true,
  data: {
    updated_section: "work_experience",
    new_completeness_score: 87.2,
    suggestions: ["Add more technical skills", "Include project descriptions"]
  }
}

GET /profile/completeness
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    overall_score: 85.5,
    section_scores: {
      "personal_info": 95.0,
      "work_experience": 80.0,
      "education": 90.0,
      "technical_skills": 75.0,
      "certifications": 60.0
    },
    suggestions: [
      {
        section: "technical_skills",
        message: "Add proficiency levels to your skills",
        priority: "high"
      }
    ],
    missing_fields: {
      "personal_info": ["portfolio_url"],
      "certifications": ["verification_url"]
    }
  }
}

POST /profile/export
Headers: Authorization: Bearer <token>
Body: {
  format: "pdf", // or "json"
  sections?: ["personal_info", "work_experience"] // optional
}
Response: {
  success: true,
  data: {
    download_url: "https://signed-url...",
    expires_at: "2024-01-01T01:00:00Z",
    file_name: "candidate_profile_2024.pdf"
  }
}
```

## Business Rules
### Profile Data Management
- Users can only access and edit their own profiles
- All profile sections are optional but affect completeness scoring
- Work experience entries must have start dates; end dates optional for current roles
- Education entries require degree and institution; graduation date optional
- Skills must have names; proficiency and experience years are optional
- Profile changes are immediately saved with optimistic UI updates

### Completeness Scoring Rules
- Personal information (25%): Name, email, phone, location required for full score
- Work experience (35%): At least one complete entry with description
- Education (15%): At least one degree with institution
- Skills (20%): Minimum 5 technical skills with proficiency levels
- Additional sections (5%): Certifications, projects, languages bonus points

### Profile Quality Standards
- Minimum 70% completeness recommended for job matching
- Profile strength levels: Basic (0-40%), Good (41-70%), Strong (71-90%), Excellent (91-100%)
- Profiles below 50% completeness receive enhancement suggestions
- Public profiles require 80% minimum completeness

## Acceptance Criteria
### Profile Management
- [ ] Users can view complete profile data from AI parsing
- [ ] All profile sections are editable with proper validation
- [ ] Auto-save functionality works within 3 seconds of changes
- [ ] Profile completeness score updates automatically after edits
- [ ] Export functionality generates proper PDF and JSON formats

### User Experience
- [ ] Profile loads within 2 seconds
- [ ] Mobile interface fully functional and responsive
- [ ] Accessibility standards met (WCAG 2.1 AA)
- [ ] Unsaved changes warning prevents data loss
- [ ] Real-time validation provides immediate feedback

### Data Quality
- [ ] Profile completeness scoring accurately reflects content quality
- [ ] Improvement suggestions are helpful and actionable
- [ ] Audit trail tracks all profile changes
- [ ] Data validation prevents invalid information storage

## Dependencies
### Depends On
- **Feature 3**: Resume Parsing (provides initial profile data)
- **Feature 1**: Authentication (user context and access control)
- **Feature 0.2**: Design System (profile editing components)

### Used By
- **Feature 6**: AI Matching (uses profile data for job comparisons)
- **Feature 7**: Skill Gap Analysis (analyzes profile skills)
- **Feature 8**: Career Recommendations (bases recommendations on profile)
- **Feature 11**: Career Snapshot (captures profile state)

### Produces
- Structured candidate profile data for all AI features
- Profile completeness metrics for quality assessment
- User-validated career information
- Profile audit trail for compliance and analysis

## Notes
### Development Priorities
1. Core profile display and editing functionality
2. Auto-save and real-time validation
3. Completeness scoring and suggestions
4. Export functionality
5. Mobile responsiveness and accessibility
6. Performance optimization for large profiles