# Feature 6: AI Matching

## Overview
Implement AI-powered job matching system that compares candidate profiles against job requirements using Google Gemini, generates match scores with detailed explanations, and provides actionable insights for career development.

## Goal
Create intelligent job-candidate matching that goes beyond keyword matching by analyzing skills compatibility, experience relevance, and career trajectory alignment to provide accurate match scores and meaningful recommendations.

## User Story
As a **Candidate**,
I want to see how well I match with job opportunities
So that I can focus on positions where I have the best chance of success.

As a **Candidate**,
I want to understand why I match or don't match with specific jobs
So that I can identify areas for improvement and make informed career decisions.

## Functional Requirements
### AI-Powered Matching
- Compare candidate profiles against job requirements using Gemini AI
- Generate match scores from 0-100% with confidence indicators
- Analyze skills alignment, experience relevance, and education fit
- Identify missing skills and experience gaps
- Evaluate salary expectations vs. job offerings
- Consider location preferences and remote work compatibility

### Match Analysis & Insights
- Detailed match explanations with strengths and weaknesses
- Skills gap identification with priority rankings
- Experience level compatibility assessment
- Career progression alignment analysis
- Improvement recommendations for better matches
- Market position analysis for similar roles

### Batch Processing & Rankings
- Process multiple job matches simultaneously
- Rank jobs by match score and user preferences
- Compare match quality across different job categories
- Historical match tracking and improvement over time
- Match quality trends and analytics

## Non-functional Requirements
- Match calculation time: <5 seconds per job-candidate pair
- Batch processing: Handle up to 50 jobs simultaneously
- Match accuracy: >80% correlation with user application success
- AI reliability: Retry logic for Gemini API failures
- Scalability: Support concurrent matching for multiple users
- Data consistency: Match results remain stable for same inputs

## Backend Tasks
### Database Schema
```sql
-- Job matching results
CREATE TABLE job_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    candidate_profile_id UUID REFERENCES candidate_profiles(id) ON DELETE CASCADE,
    
    -- Match scoring
    overall_match_score DECIMAL(5,2) NOT NULL, -- 0-100
    skills_match_score DECIMAL(5,2),
    experience_match_score DECIMAL(5,2),
    education_match_score DECIMAL(5,2),
    location_match_score DECIMAL(5,2),
    
    -- AI analysis results
    match_explanation TEXT,
    strengths JSONB, -- Array of matching strengths
    weaknesses JSONB, -- Array of gaps and weaknesses
    missing_skills JSONB, -- Skills required but not possessed
    skill_gaps JSONB, -- Detailed skill gap analysis
    improvement_suggestions JSONB, -- Recommendations for better match
    
    -- Metadata
    gemini_model_version VARCHAR(50),
    matching_algorithm_version VARCHAR(20),
    processing_duration INTEGER, -- Milliseconds
    confidence_score DECIMAL(5,2), -- AI confidence in the analysis
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure one match per user-job pair
    UNIQUE(user_id, job_id)
);

-- Skills matching analysis
CREATE TABLE skills_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_match_id UUID REFERENCES job_matches(id) ON DELETE CASCADE,
    skill_name VARCHAR(255) NOT NULL,
    skill_category VARCHAR(100),
    required_proficiency VARCHAR(50), -- From job requirements
    candidate_proficiency VARCHAR(50), -- From candidate profile
    match_type VARCHAR(50), -- exact, partial, missing, bonus
    match_score DECIMAL(5,2), -- Individual skill match 0-100
    importance_weight DECIMAL(3,2), -- How important this skill is for the job
    created_at TIMESTAMP DEFAULT NOW()
);

-- Match quality metrics for algorithm improvement
CREATE TABLE match_quality_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_match_id UUID REFERENCES job_matches(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50), -- applied, interviewed, hired, rejected
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    feedback_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_job_matches_user_id ON job_matches(user_id);
CREATE INDEX idx_job_matches_job_id ON job_matches(job_id);
CREATE INDEX idx_job_matches_score ON job_matches(overall_match_score DESC);
CREATE INDEX idx_job_matches_created_at ON job_matches(created_at DESC);
CREATE INDEX idx_skills_matches_job_match ON skills_matches(job_match_id);
```

### AI Matching Service
```python
class JobMatchingService:
    def __init__(self, gemini_client: GeminiClient, profile_service: ProfileService):
        self.gemini_client = gemini_client
        self.profile_service = profile_service
        self.prompt_manager = PromptManager()
    
    async def calculate_job_match(self, user_id: UUID, job_id: UUID) -> JobMatchResult:
        # Get candidate profile and job details
        profile = await self.profile_service.get_user_profile(user_id)
        job = await self.get_job_details(job_id)
        
        # Prepare matching prompt with structured data
        matching_prompt = await self.prepare_matching_prompt(profile, job)
        
        # Call Gemini for AI analysis
        ai_response = await self.gemini_client.analyze_job_match(matching_prompt)
        
        # Process and validate AI response
        match_analysis = await self.process_match_response(ai_response)
        
        # Calculate composite scores
        overall_score = await self.calculate_composite_score(match_analysis)
        
        # Store match results
        match_record = await self.store_match_results(
            user_id, job_id, profile.id, match_analysis, overall_score
        )
        
        return JobMatchResult(
            match_id=match_record.id,
            overall_score=overall_score,
            analysis=match_analysis,
            processing_time=ai_response.processing_time
        )
    
    async def batch_match_jobs(self, user_id: UUID, job_ids: List[UUID]) -> List[JobMatchResult]:
        # Process multiple jobs concurrently with rate limiting
        semaphore = asyncio.Semaphore(5)  # Limit concurrent API calls
        
        async def match_single_job(job_id: UUID):
            async with semaphore:
                return await self.calculate_job_match(user_id, job_id)
        
        tasks = [match_single_job(job_id) for job_id in job_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out failed matches and log errors
        successful_matches = [r for r in results if isinstance(r, JobMatchResult)]
        return successful_matches
    
    async def get_user_matches(self, user_id: UUID, filters: MatchFilters) -> List[JobMatch]:
        # Retrieve stored matches with filtering and sorting
        # Apply score thresholds and date ranges
        # Include job details and match explanations
        
    async def update_match_feedback(self, match_id: UUID, feedback: MatchFeedback) -> bool:
        # Store user feedback for match quality improvement
        # Update algorithm performance metrics
        # Use feedback for future matching improvements
```

### Gemini Matching Client
```python
class GeminiMatchingClient:
    def __init__(self, api_key: str):
        self.client = genai.GenerativeModel('gemini-pro')
        self.matching_prompts = MatchingPrompts()
    
    async def analyze_job_match(self, matching_data: MatchingPromptData) -> MatchResponse:
        # Format prompt with candidate and job data
        prompt = self.matching_prompts.format_matching_prompt(matching_data)
        
        generation_config = {
            'temperature': 0.2,  # Low temperature for consistent analysis
            'top_p': 0.8,
            'max_output_tokens': 2000
        }
        
        try:
            response = await self.client.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            # Parse structured JSON response
            analysis = json.loads(response.text)
            
            return MatchResponse(
                analysis=analysis,
                model_version='gemini-pro-1.0',
                processing_time=response.usage_metadata.total_token_count,
                confidence=self.calculate_response_confidence(analysis)
            )
            
        except Exception as e:
            raise AIMatchingException(f"Gemini matching failed: {str(e)}")
```

## AI Service Tasks
### Job Matching Prompts
```python
JOB_MATCHING_PROMPT_V1 = {
    "version": "1.0",
    "system_prompt": """
You are an expert career counselor and recruiter analyzing job-candidate compatibility.
Analyze the candidate profile against job requirements and provide detailed matching insights.
Return structured JSON with scores, explanations, and actionable recommendations.
Be thorough but concise in your analysis.
    """,
    "user_prompt": """
Analyze this candidate's fit for the job position and provide a detailed matching assessment:

CANDIDATE PROFILE:
{candidate_data}

JOB REQUIREMENTS:
{job_data}

Provide analysis in this exact JSON format:
{
  "overall_assessment": {
    "match_score": number, // 0-100 overall compatibility
    "confidence": number, // 0-100 confidence in this assessment
    "summary": "Brief overall assessment"
  },
  "skills_analysis": {
    "matching_skills": [
      {"skill": "name", "candidate_level": "level", "required_level": "level", "match_quality": "excellent|good|fair"}
    ],
    "missing_skills": [
      {"skill": "name", "required_level": "level", "importance": "critical|high|medium", "learning_effort": "low|medium|high"}
    ],
    "bonus_skills": [
      {"skill": "name", "value": "How this extra skill adds value"}
    ],
    "skills_score": number // 0-100
  },
  "experience_analysis": {
    "relevant_experience": "Assessment of relevant work experience",
    "experience_gaps": ["Gap 1", "Gap 2"],
    "experience_score": number, // 0-100
    "career_progression_fit": "How well candidate's trajectory fits the role"
  },
  "education_analysis": {
    "education_fit": "Assessment of educational background",
    "education_score": number, // 0-100
    "additional_education_needs": ["Need 1", "Need 2"]
  },
  "location_compatibility": {
    "location_score": number, // 0-100
    "remote_work_fit": "Assessment for remote/hybrid roles",
    "relocation_considerations": "Any relocation factors"
  },
  "strengths": [
    "Key strength that makes candidate attractive",
    "Another strength"
  ],
  "areas_for_improvement": [
    {
      "area": "What needs improvement",
      "priority": "high|medium|low",
      "suggestion": "Specific recommendation"
    }
  ],
  "recommendation": {
    "should_apply": boolean,
    "likelihood_of_success": "high|medium|low",
    "key_selling_points": ["Point 1", "Point 2"],
    "preparation_advice": "How to prepare for application/interview"
  }
}
    """,
    "validation_schema": {
        # Complete JSON schema for response validation
    }
}
```

## API Endpoints
### Job Matching Endpoints
```
POST /jobs/{job_id}/match
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    match_id: "uuid",
    overall_score: 87.5,
    skills_score: 85.0,
    experience_score: 90.0,
    education_score: 88.0,
    location_score: 95.0,
    processing_time: 4200,
    created_at: "2024-01-01T00:00:00Z"
  }
}

GET /matches/{match_id}
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    id: "uuid",
    job: { /* job details */ },
    overall_score: 87.5,
    analysis: {
      skills_analysis: { /* detailed skills breakdown */ },
      experience_analysis: { /* experience assessment */ },
      strengths: ["Strong technical background", "Relevant project experience"],
      areas_for_improvement: [
        {
          "area": "Cloud platform experience",
          "priority": "high",
          "suggestion": "Consider AWS certification"
        }
      ],
      recommendation: {
        "should_apply": true,
        "likelihood_of_success": "high",
        "preparation_advice": "Emphasize your Python experience and recent projects"
      }
    },
    created_at: "2024-01-01T00:00:00Z"
  }
}

POST /jobs/batch-match
Headers: Authorization: Bearer <token>
Body: {
  job_ids: ["uuid1", "uuid2", "uuid3"]
}
Response: {
  success: true,
  data: {
    matches: [
      {
        job_id: "uuid1",
        match_id: "match_uuid1",
        overall_score: 87.5,
        status: "completed"
      }
    ],
    processing_summary: {
      total_jobs: 3,
      successful: 3,
      failed: 0,
      average_processing_time: 4500
    }
  }
}

GET /matches
Headers: Authorization: Bearer <token>
Query: ?min_score=70&sort=score&order=desc&limit=20
Response: {
  success: true,
  data: {
    matches: [
      {
        match_id: "uuid",
        job: { /* job summary */ },
        overall_score: 92.0,
        match_summary: "Excellent fit with strong technical skills alignment",
        created_at: "2024-01-01T00:00:00Z"
      }
    ],
    pagination: {
      total: 45,
      page: 1,
      per_page: 20
    }
  }
}
```

## Frontend Tasks
### Match Display Components
```tsx
const JobMatchCard: React.FC<{
  match: JobMatch;
  onViewDetails: () => void;
}> = ({ match, onViewDetails }) => {
  // Match score visualization with color coding
  // Job title and company information
  // Key strengths and gaps summary
  // Action buttons (view details, apply)
};

const MatchAnalysisDetail: React.FC<{
  analysis: MatchAnalysis;
}> = ({ analysis }) => {
  // Overall score with breakdown by category
  // Skills matching matrix
  // Experience compatibility assessment
  // Improvement recommendations
  // Application preparation advice
};

const MatchScoreIndicator: React.FC<{
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}> = ({ score, size = 'md', showLabel = true }) => {
  // Circular progress indicator for match score
  // Color coding: <60 red, 60-80 yellow, >80 green
  // Animation for score changes
};
```

## Business Rules
### Matching Algorithm Rules
- Overall score calculated as weighted average: Skills (40%), Experience (35%), Education (15%), Location (10%)
- Skills matching considers both exact matches and transferable skills
- Experience relevance weighted by recency and role similarity
- Location score factors in remote work preferences and relocation willingness
- Minimum 60% match score recommended for application consideration

### Quality Assurance Rules
- Match results cached for 7 days or until profile/job updates
- AI confidence below 80% triggers manual review flag
- Batch matching limited to 50 jobs per request to prevent timeouts
- Failed matches automatically retry once before flagging as failed
- User feedback incorporated into algorithm improvement metrics

## Acceptance Criteria
### Matching Accuracy
- [ ] Match scores correlate >80% with user application success rates
- [ ] Skills analysis correctly identifies missing and bonus skills
- [ ] Experience assessment accounts for role progression and relevance
- [ ] Location compatibility factors in remote work and relocation preferences
- [ ] Improvement suggestions are specific and actionable

### Performance Requirements
- [ ] Individual match calculation completes within 5 seconds
- [ ] Batch matching handles 50 jobs within 30 seconds
- [ ] Match results remain consistent for identical inputs
- [ ] API endpoints respond within performance thresholds
- [ ] Error handling graceful for AI service failures

## Dependencies
### Depends On
- **Feature 4**: Candidate Profile (structured profile data for matching)
- **Feature 5**: Job Discovery (job data and requirements)
- **Feature 0.1**: Project Infrastructure (Gemini API integration)

### Used By
- **Feature 7**: Skill Gap Analysis (uses match results for gap identification)
- **Feature 8**: Career Recommendations (incorporates matching insights)
- **Feature 11**: Career Snapshot (preserves match history)

### Produces
- Job-candidate compatibility scores and analysis
- Skills gap identification for career development
- Match quality data for algorithm improvement
- User job matching preferences and patterns

## Notes
### Development Priorities
1. Core AI matching with Gemini integration
2. Match scoring and analysis display
3. Batch processing for multiple jobs
4. Match history and comparison features
5. User feedback collection for improvements
6. Performance optimization and caching