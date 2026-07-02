# Feature 8: Career Recommendation

## Overview
Implement AI-powered career path recommendation system that analyzes candidate profiles, market trends, and career progression patterns to suggest optimal career paths with confidence scoring and detailed reasoning.

## Goal
Provide personalized, data-driven career guidance that helps candidates discover new opportunities, plan career transitions, and make informed decisions about their professional development based on their skills, experience, and market realities.

## User Story
As a **Candidate**,
I want to receive AI-powered career path recommendations
So that I can explore new opportunities and plan my career growth strategically.

As a **Candidate**,
I want to understand why certain careers are recommended for me
So that I can make informed decisions about my professional future.

## Functional Requirements
### Career Path Analysis
- Analyze candidate profile against multiple career trajectories
- Generate personalized career recommendations with confidence scores
- Consider current skills, experience, education, and career preferences
- Factor in market trends, growth potential, and salary projections
- Identify both traditional and non-traditional career paths
- Account for career transition feasibility and timeline

### Recommendation Intelligence
- Multi-dimensional analysis: skills fit, experience relevance, market demand
- Career progression modeling based on industry patterns
- Transition difficulty assessment with required skill development
- Salary projection and earning potential analysis
- Geographic market analysis for recommended careers
- Industry growth trends and future outlook integration

### Personalization & Filtering
- Filter recommendations by industry preferences and constraints
- Consider work-life balance preferences and remote work options
- Account for relocation willingness and geographic limitations
- Factor in career timeline and advancement goals
- Integrate with existing job matching and skill gap data
- Provide alternative paths for different risk tolerance levels

## Non-functional Requirements
- Recommendation generation time: <8 seconds for comprehensive analysis
- Recommendation accuracy: >80% alignment with user career satisfaction
- Market data integration: Real-time salary and growth projections
- Scalability: Support concurrent recommendation generation
- Data freshness: Weekly updates of market trends and career data
- Personalization quality: Recommendations improve with user feedback

## Backend Tasks
### Database Schema
```sql
-- Career recommendation results
CREATE TABLE career_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    candidate_profile_id UUID REFERENCES candidate_profiles(id) ON DELETE CASCADE,
    
    -- Recommendation metadata
    recommendation_set_id UUID, -- Group related recommendations
    total_careers_analyzed INTEGER,
    recommendation_confidence DECIMAL(5,2), -- Overall AI confidence
    analysis_version VARCHAR(50),
    
    -- Market context
    market_data_version VARCHAR(50),
    geographic_focus VARCHAR(255), -- Location context for recommendations
    industry_focus JSONB, -- Target industries if specified
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '60 days')
);

-- Individual career path recommendations
CREATE TABLE career_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recommendation_id UUID REFERENCES career_recommendations(id) ON DELETE CASCADE,
    
    -- Career details
    career_title VARCHAR(255) NOT NULL,
    career_category VARCHAR(100), -- technology, healthcare, finance, etc.
    industry VARCHAR(255),
    seniority_level VARCHAR(100), -- entry, mid, senior, executive, c_level
    
    -- Scoring and analysis
    overall_fit_score DECIMAL(5,2), -- 0-100 overall recommendation strength
    skills_alignment_score DECIMAL(5,2),
    experience_relevance_score DECIMAL(5,2),
    market_opportunity_score DECIMAL(5,2),
    growth_potential_score DECIMAL(5,2),
    
    -- Market projections
    salary_range_min INTEGER,
    salary_range_max INTEGER,
    salary_currency VARCHAR(10) DEFAULT 'USD',
    job_growth_rate DECIMAL(5,2), -- % annual growth projection
    market_demand VARCHAR(50), -- low, medium, high, critical
    
    -- Transition analysis
    transition_difficulty VARCHAR(50), -- easy, moderate, challenging, significant
    estimated_transition_months INTEGER,
    required_skill_development JSONB, -- Skills needed for transition
    education_requirements JSONB, -- Additional education/certifications
    
    -- AI insights
    recommendation_reasoning TEXT,
    key_strengths JSONB, -- Why candidate fits this career
    potential_challenges JSONB, -- Obstacles and considerations
    success_probability VARCHAR(50), -- high, medium, low
    
    -- Additional context
    typical_career_progression JSONB, -- Common advancement paths
    related_roles JSONB, -- Similar or adjacent career options
    geographic_opportunities JSONB, -- Where these jobs are most available
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Career transition pathways and requirements
CREATE TABLE career_transition_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    career_path_id UUID REFERENCES career_paths(id) ON DELETE CASCADE,
    
    -- Transition details
    pathway_name VARCHAR(255), -- e.g., "Software Engineer to Product Manager"
    transition_type VARCHAR(100), -- lateral, promotion, pivot, complete_change
    
    -- Requirements breakdown
    skill_requirements JSONB, -- Required skills with proficiency levels
    experience_requirements JSONB, -- Necessary experience types
    education_requirements JSONB, -- Degrees, certifications, courses
    networking_requirements JSONB, -- Industry connections needed
    
    -- Timeline and milestones
    milestone_timeline JSONB, -- Month-by-month transition plan
    critical_milestones JSONB, -- Key achievements needed
    success_indicators JSONB, -- How to measure progress
    
    -- Success factors
    success_rate_percentage DECIMAL(5,2), -- Historical success rate
    common_failure_points JSONB, -- Where transitions typically fail
    mitigation_strategies JSONB, -- How to overcome challenges
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- User feedback on career recommendations
CREATE TABLE career_recommendation_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    career_path_id UUID REFERENCES career_paths(id) ON DELETE CASCADE,
    
    -- Feedback details
    interest_level INTEGER CHECK (interest_level >= 1 AND interest_level <= 5),
    feasibility_rating INTEGER CHECK (feasibility_rating >= 1 AND feasibility_rating <= 5),
    accuracy_rating INTEGER CHECK (accuracy_rating >= 1 AND accuracy_rating <= 5),
    
    -- Qualitative feedback
    feedback_notes TEXT,
    reasons_for_interest JSONB, -- What appeals to the user
    concerns_or_barriers JSONB, -- What makes them hesitant
    
    -- Actions taken
    started_pursuing BOOLEAN DEFAULT FALSE,
    requested_more_info BOOLEAN DEFAULT FALSE,
    dismissed_recommendation BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_career_recommendations_user_id ON career_recommendations(user_id);
CREATE INDEX idx_career_recommendations_created_at ON career_recommendations(created_at DESC);
CREATE INDEX idx_career_paths_recommendation_id ON career_paths(recommendation_id);
CREATE INDEX idx_career_paths_fit_score ON career_paths(overall_fit_score DESC);
CREATE INDEX idx_career_paths_category ON career_paths(career_category, industry);
CREATE INDEX idx_career_feedback_user_career ON career_recommendation_feedback(user_id, career_path_id);
```

### Career Recommendation Service
```python
class CareerRecommendationService:
    def __init__(self, gemini_client: GeminiClient, market_data_service: MarketDataService):
        self.gemini_client = gemini_client
        self.market_data_service = market_data_service
        self.career_database = CareerDatabase()
    
    async def generate_career_recommendations(self, user_id: UUID, preferences: CareerPreferences = None) -> CareerRecommendationResult:
        # Get comprehensive candidate profile
        profile = await self.get_candidate_profile(user_id)
        
        # Get market data and career trends
        market_context = await self.market_data_service.get_career_market_data(
            industries=preferences.target_industries if preferences else None,
            locations=preferences.target_locations if preferences else None
        )
        
        # Get similar career progression patterns
        career_patterns = await self.career_database.get_similar_career_patterns(profile)
        
        # Generate AI recommendations
        ai_recommendations = await self.generate_ai_career_analysis(
            profile, market_context, career_patterns, preferences
        )
        
        # Enrich with market data and projections
        enriched_recommendations = await self.enrich_recommendations_with_market_data(
            ai_recommendations, market_context
        )
        
        # Calculate transition pathways
        transition_paths = await self.analyze_transition_pathways(
            profile, enriched_recommendations
        )
        
        # Store recommendations
        recommendation_record = await self.store_recommendations(
            user_id, profile.id, enriched_recommendations, transition_paths
        )
        
        return CareerRecommendationResult(
            recommendation_id=recommendation_record.id,
            total_careers=len(enriched_recommendations),
            top_recommendations=enriched_recommendations[:5],
            transition_analysis=transition_paths,
            market_insights=market_context.insights
        )
    
    async def generate_ai_career_analysis(self, profile: CandidateProfile, market_context: MarketContext, career_patterns: List[CareerPattern], preferences: CareerPreferences) -> List[CareerRecommendation]:
        # Prepare comprehensive AI prompt with all context
        ai_prompt = await self.create_career_recommendation_prompt(
            profile, market_context, career_patterns, preferences
        )
        
        # Call Gemini for career analysis
        ai_response = await self.gemini_client.analyze_career_paths(ai_prompt)
        
        # Process and validate AI recommendations
        recommendations = await self.process_career_recommendations(ai_response)
        
        # Score and rank recommendations
        scored_recommendations = await self.score_recommendations(
            recommendations, profile, market_context
        )
        
        return sorted(scored_recommendations, key=lambda x: x.overall_fit_score, reverse=True)
    
    async def analyze_transition_pathways(self, profile: CandidateProfile, recommendations: List[CareerRecommendation]) -> List[TransitionPath]:
        transition_paths = []
        
        for recommendation in recommendations:
            # Analyze skill gaps for transition
            skill_gaps = await self.analyze_career_skill_gaps(profile, recommendation)
            
            # Calculate transition timeline
            timeline = await self.calculate_transition_timeline(skill_gaps, recommendation)
            
            # Identify success factors and risks
            success_factors = await self.identify_success_factors(recommendation)
            
            transition_path = TransitionPath(
                career_path=recommendation,
                skill_gaps=skill_gaps,
                estimated_timeline=timeline,
                success_factors=success_factors,
                difficulty_rating=self.calculate_transition_difficulty(skill_gaps, timeline)
            )
            
            transition_paths.append(transition_path)
        
        return transition_paths
```

## AI Service Tasks
### Career Recommendation Prompts
```python
CAREER_RECOMMENDATION_PROMPT_V1 = {
    "version": "1.0",
    "system_prompt": """
You are an expert career counselor with deep knowledge of career progression patterns, market trends, and professional development pathways. Analyze the candidate's profile and provide personalized, realistic career recommendations that align with their skills, experience, and market opportunities.

Focus on:
- Realistic career progression based on current skills and experience
- Market demand and growth potential for recommended careers
- Skill transferability and development requirements
- Geographic and industry considerations
- Risk assessment for career transitions
    """,
    "user_prompt": """
Analyze this candidate's profile and recommend optimal career paths:

CANDIDATE PROFILE:
{candidate_profile}

MARKET CONTEXT:
{market_data}

SIMILAR CAREER PATTERNS:
{career_patterns}

USER PREFERENCES:
{career_preferences}

Provide detailed career recommendations in this JSON format:
{
  "career_analysis": {
    "profile_summary": "Brief analysis of candidate's current position and strengths",
    "career_readiness_score": number, // 0-100 how ready for career advancement
    "market_positioning": "How candidate compares in current market"
  },
  "recommended_careers": [
    {
      "career_title": "Specific job title/career path",
      "career_category": "Industry/field category", 
      "seniority_level": "entry|mid|senior|executive|c_level",
      "overall_fit_score": number, // 0-100 overall recommendation strength
      
      "fit_analysis": {
        "skills_alignment": {
          "score": number, // 0-100
          "matching_skills": ["skill1", "skill2"],
          "transferable_skills": ["skill1", "skill2"], 
          "skill_gaps": ["missing_skill1", "missing_skill2"]
        },
        "experience_relevance": {
          "score": number, // 0-100
          "relevant_experience": "How current experience applies",
          "experience_gaps": "What experience is missing"
        },
        "market_opportunity": {
          "score": number, // 0-100
          "demand_level": "low|medium|high|critical",
          "growth_projection": "Industry growth outlook",
          "geographic_availability": "Where jobs are available"
        }
      },
      
      "career_projections": {
        "salary_range": {
          "min": number,
          "max": number,
          "currency": "USD"
        },
        "job_growth_rate": number, // Annual % growth
        "career_progression": "Typical advancement path",
        "long_term_outlook": "5-10 year career prospects"
      },
      
      "transition_analysis": {
        "difficulty_level": "easy|moderate|challenging|significant",
        "estimated_timeline_months": number,
        "critical_requirements": [
          "Most important requirement for success"
        ],
        "skill_development_needed": [
          {
            "skill": "skill name",
            "current_level": "none|beginner|intermediate|advanced",
            "target_level": "beginner|intermediate|advanced|expert",
            "learning_priority": "critical|high|medium|low"
          }
        ],
        "education_certifications": [
          "Additional education or certifications recommended"
        ]
      },
      
      "recommendation_reasoning": {
        "why_good_fit": "Detailed explanation of fit rationale",
        "key_strengths": ["Strength 1", "Strength 2"],
        "potential_challenges": ["Challenge 1", "Challenge 2"],
        "success_probability": "high|medium|low",
        "risk_factors": ["Risk 1", "Risk 2"]
      },
      
      "next_steps": {
        "immediate_actions": ["Action 1", "Action 2"],
        "short_term_goals": ["3-6 month objectives"],
        "long_term_preparation": ["6+ month objectives"],
        "networking_strategy": "How to build relevant connections"
      }
    }
  ],
  
  "alternative_considerations": {
    "lateral_moves": "Careers at similar level with different focus",
    "entrepreneurial_paths": "Business/startup opportunities",
    "consulting_freelance": "Independent work possibilities",
    "geographic_relocations": "Opportunities requiring relocation"
  },
  
  "market_insights": {
    "trending_careers": ["Career 1", "Career 2"],
    "declining_opportunities": ["Declining area 1"],
    "emerging_fields": ["New opportunity 1"],
    "skill_market_trends": "What skills are becoming more/less valuable"
  }
}
    """
}
```

## API Endpoints
### Career Recommendation Endpoints
```
POST /career-recommendations/generate
Headers: Authorization: Bearer <token>
Body: {
  preferences?: {
    target_industries?: ["Technology", "Healthcare"],
    target_locations?: ["San Francisco", "Remote"],
    career_timeline?: "immediate|short_term|long_term",
    risk_tolerance?: "conservative|moderate|aggressive",
    work_life_balance?: "flexible|standard|intensive"
  },
  focus_areas?: ["skill_alignment", "salary_growth", "market_demand"]
}
Response: {
  success: true,
  data: {
    recommendation_id: "uuid",
    total_careers_analyzed: 25,
    recommendations_generated: 8,
    analysis_confidence: 89.2,
    processing_time: 7800,
    expires_at: "2024-03-01T00:00:00Z"
  }
}

GET /career-recommendations/{recommendation_id}
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    id: "uuid",
    created_at: "2024-01-01T00:00:00Z",
    total_careers: 8,
    career_paths: [
      {
        career_title: "Senior Product Manager",
        career_category: "Product Management",
        overall_fit_score: 92.5,
        skills_alignment_score: 88.0,
        market_opportunity_score: 95.0,
        salary_range: {
          "min": 120000,
          "max": 180000,
          "currency": "USD"
        },
        transition_difficulty: "moderate",
        estimated_timeline_months: 6,
        recommendation_reasoning: "Strong technical background combined with leadership experience makes you an excellent candidate for product management roles. Your understanding of software development processes and user experience principles align well with product management requirements.",
        key_strengths: [
          "Technical expertise enables effective engineering collaboration",
          "Project management experience translates well to product ownership"
        ],
        required_skill_development: [
          {
            "skill": "Product Strategy",
            "current_level": "beginner", 
            "target_level": "intermediate",
            "learning_priority": "high"
          }
        ],
        next_steps: {
          "immediate_actions": [
            "Complete product management fundamentals course",
            "Start following product management thought leaders"
          ],
          "short_term_goals": [
            "Lead a product feature from conception to launch",
            "Build relationships with product teams in your organization"
          ]
        }
      }
    ],
    market_insights: {
      "trending_careers": ["AI Product Manager", "Data Product Manager"],
      "skill_market_trends": "Product management roles increasingly require technical backgrounds"
    }
  }
}
```

## Business Rules & Acceptance Criteria
### Recommendation Quality Standards
- Minimum 75% overall fit score for top recommendations
- Market data must be less than 30 days old
- Transition timelines realistic based on skill gap analysis  
- Salary projections within 10% of market research data
- Geographic recommendations match user location preferences

### Performance Requirements
- [ ] Recommendation generation completes within 8 seconds
- [ ] Analysis accuracy >80% validated against user career outcomes
- [ ] Market data integration provides current salary and growth data
- [ ] Recommendations improve with user feedback over time
- [ ] System supports concurrent recommendation generation

## Dependencies
### Depends On
- **Feature 4**: Candidate Profile (comprehensive profile data)
- **Feature 7**: Skill Gap Analysis (skill gap insights and market data)
- **Feature 6**: AI Matching (job market analysis and requirements)

### Used By  
- **Feature 9**: Learning Roadmap (creates learning plans for recommended careers)
- **Feature 11**: Career Snapshot (preserves career recommendations over time)

### Produces
- Personalized career path recommendations with confidence scoring
- Career transition analysis and timeline planning
- Market-driven career insights and projections
- Skill development priorities aligned with career goals

## Notes
### Development Priorities
1. Core AI recommendation engine with market data integration
2. Career transition pathway analysis and timeline calculation
3. User preference integration and personalization
4. Recommendation feedback system for continuous improvement
5. Advanced market trend analysis and emerging career identification