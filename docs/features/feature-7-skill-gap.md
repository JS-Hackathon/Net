# Feature 7: Skill Gap Analysis

## Overview
Implement AI-powered skill gap analysis that compares candidate skills against job market demands, identifies missing competencies, and provides prioritized recommendations for skill development based on career goals and market trends.

## Goal
Provide candidates with clear, actionable insights about their skill gaps relative to target roles, helping them make informed decisions about professional development priorities and career advancement strategies.

## User Story
As a **Candidate**,
I want to understand what skills I'm missing for my target roles
So that I can focus my learning efforts on the most impactful areas for my career growth.

As a **Candidate**,
I want to see which skills are most in-demand in my field
So that I can stay competitive in the job market.

## Functional Requirements
### Skill Gap Detection
- Analyze candidate's current skills against target job requirements
- Identify missing skills with importance and urgency rankings
- Compare skill proficiency levels with job expectations
- Detect transferable skills and alternative competencies
- Track emerging skills trends in candidate's industry
- Provide market demand analysis for specific skills

### Gap Prioritization System
- Rank skill gaps by impact on career advancement (Critical, High, Medium, Low)
- Factor in market demand and salary impact for each skill
- Consider learning difficulty and time investment required
- Account for candidate's career timeline and goals
- Integrate with job matching results for targeted analysis
- Update priorities based on job market changes

### Development Recommendations
- Suggest specific learning paths for each identified gap
- Recommend resources (courses, certifications, projects)
- Estimate time and effort required for skill development
- Track progress on skill development goals
- Provide skill development roadmaps aligned with career objectives

## Non-functional Requirements
- Gap analysis completion time: <10 seconds for comprehensive assessment
- Market data freshness: Updated weekly with latest job market trends
- Analysis accuracy: >85% correlation with actual hiring requirements
- Scalability: Support simultaneous analysis for multiple users
- Data consistency: Reliable skill classification and normalization
- Performance: Handle large skill datasets without degradation

## Backend Tasks
### Database Schema
```sql
-- Skill gap analysis results
CREATE TABLE skill_gap_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    candidate_profile_id UUID REFERENCES candidate_profiles(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) DEFAULT 'comprehensive', -- comprehensive, role_specific, market_trends
    target_role VARCHAR(255), -- Specific role if role_specific analysis
    
    -- Analysis metadata
    total_skills_analyzed INTEGER,
    gaps_identified INTEGER,
    market_data_version VARCHAR(50),
    analysis_confidence DECIMAL(5,2), -- 0-100 AI confidence score
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '30 days')
);

-- Individual skill gaps with detailed analysis
CREATE TABLE skill_gaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES skill_gap_analyses(id) ON DELETE CASCADE,
    skill_name VARCHAR(255) NOT NULL,
    skill_category VARCHAR(100), -- technical, soft, domain, certification
    
    -- Gap assessment
    current_proficiency VARCHAR(50), -- none, beginner, intermediate, advanced, expert
    required_proficiency VARCHAR(50),
    proficiency_gap_score DECIMAL(5,2), -- 0-100 how big the gap is
    
    -- Market analysis
    market_demand VARCHAR(50), -- critical, high, medium, low
    demand_trend VARCHAR(50), -- growing, stable, declining
    salary_impact_percentage DECIMAL(5,2), -- % salary increase potential
    job_postings_mentioning INTEGER, -- Number of jobs requiring this skill
    
    -- Learning assessment
    learning_difficulty VARCHAR(50), -- easy, moderate, challenging, expert_level
    estimated_learning_hours INTEGER,
    priority_ranking VARCHAR(20), -- critical, high, medium, low
    priority_score DECIMAL(5,2), -- Calculated priority 0-100
    
    -- Recommendations
    recommended_resources JSONB, -- Array of learning resources
    skill_alternatives JSONB, -- Alternative/related skills
    certification_paths JSONB, -- Relevant certifications
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Market skill demand data (updated weekly)
CREATE TABLE market_skill_demand (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_name VARCHAR(255) NOT NULL,
    skill_category VARCHAR(100),
    industry VARCHAR(255),
    location VARCHAR(255) DEFAULT 'global',
    
    -- Demand metrics
    job_postings_count INTEGER,
    demand_level VARCHAR(50), -- critical, high, medium, low
    growth_rate DECIMAL(5,2), -- % growth year-over-year
    average_salary_impact DECIMAL(10,2),
    
    -- Time series data
    data_week DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(skill_name, industry, location, data_week)
);

-- Skill development tracking
CREATE TABLE skill_development_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    skill_gap_id UUID REFERENCES skill_gaps(id) ON DELETE CASCADE,
    
    -- Goal definition
    target_proficiency VARCHAR(50),
    target_completion_date DATE,
    learning_plan JSONB, -- Structured learning plan
    
    -- Progress tracking
    current_progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    milestones_completed JSONB, -- Array of completed milestones
    time_invested_hours DECIMAL(8,2) DEFAULT 0.00,
    
    -- Status
    status VARCHAR(50) DEFAULT 'active', -- active, completed, paused, cancelled
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_skill_gap_analyses_user_id ON skill_gap_analyses(user_id);
CREATE INDEX idx_skill_gap_analyses_created_at ON skill_gap_analyses(created_at DESC);
CREATE INDEX idx_skill_gaps_analysis_id ON skill_gaps(analysis_id);
CREATE INDEX idx_skill_gaps_priority ON skill_gaps(priority_score DESC);
CREATE INDEX idx_market_skill_demand_skill ON market_skill_demand(skill_name, data_week DESC);
CREATE INDEX idx_skill_development_goals_user ON skill_development_goals(user_id, status);
```

### Skill Gap Analysis Service
```python
class SkillGapAnalysisService:
    def __init__(self, gemini_client: GeminiClient, market_data_service: MarketDataService):
        self.gemini_client = gemini_client
        self.market_data_service = market_data_service
        self.skill_classifier = SkillClassifier()
    
    async def analyze_skill_gaps(self, user_id: UUID, target_roles: List[str] = None) -> SkillGapAnalysis:
        # Get candidate profile and skills
        profile = await self.get_candidate_profile(user_id)
        
        # Get market demand data for relevant skills
        market_data = await self.market_data_service.get_skill_demand_data(
            industries=profile.target_industries,
            locations=profile.target_locations
        )
        
        # Analyze gaps using AI
        if target_roles:
            gap_analysis = await self.analyze_role_specific_gaps(profile, target_roles, market_data)
        else:
            gap_analysis = await self.analyze_comprehensive_gaps(profile, market_data)
        
        # Calculate priorities and recommendations
        prioritized_gaps = await self.prioritize_skill_gaps(gap_analysis, market_data)
        
        # Store analysis results
        analysis_record = await self.store_gap_analysis(user_id, profile.id, prioritized_gaps)
        
        return SkillGapAnalysis(
            analysis_id=analysis_record.id,
            total_gaps=len(prioritized_gaps),
            critical_gaps=len([g for g in prioritized_gaps if g.priority == 'critical']),
            gaps=prioritized_gaps,
            market_insights=market_data.insights
        )
    
    async def analyze_role_specific_gaps(self, profile: CandidateProfile, target_roles: List[str], market_data: MarketData) -> List[SkillGap]:
        # Get job requirements for target roles
        role_requirements = await self.get_role_skill_requirements(target_roles)
        
        # Use AI to compare profile skills with role requirements
        ai_prompt = await self.create_role_gap_prompt(profile, role_requirements, market_data)
        ai_response = await self.gemini_client.analyze_skill_gaps(ai_prompt)
        
        # Process AI response into structured gap data
        return await self.process_gap_analysis_response(ai_response, market_data)
    
    async def prioritize_skill_gaps(self, gaps: List[SkillGap], market_data: MarketData) -> List[SkillGap]:
        for gap in gaps:
            # Calculate priority score based on multiple factors
            market_demand_score = self.calculate_market_demand_score(gap.skill_name, market_data)
            proficiency_gap_score = gap.proficiency_gap_score
            learning_difficulty_score = self.calculate_learning_difficulty_score(gap)
            salary_impact_score = gap.salary_impact_percentage
            
            # Weighted priority calculation
            gap.priority_score = (
                market_demand_score * 0.3 +
                proficiency_gap_score * 0.25 +
                salary_impact_score * 0.25 +
                (100 - learning_difficulty_score) * 0.2  # Easier to learn = higher priority
            )
            
            # Assign priority category
            if gap.priority_score >= 80:
                gap.priority_ranking = 'critical'
            elif gap.priority_score >= 65:
                gap.priority_ranking = 'high'
            elif gap.priority_score >= 40:
                gap.priority_ranking = 'medium'
            else:
                gap.priority_ranking = 'low'
        
        return sorted(gaps, key=lambda x: x.priority_score, reverse=True)
```

## AI Service Tasks
### Skill Gap Analysis Prompts
```python
SKILL_GAP_ANALYSIS_PROMPT_V1 = {
    "version": "1.0",
    "system_prompt": """
You are an expert career advisor analyzing skill gaps for professional development.
Compare the candidate's current skills with market requirements and target role needs.
Provide detailed, actionable insights for skill development prioritization.
Focus on practical recommendations that align with career goals and market demand.
    """,
    "user_prompt": """
Analyze skill gaps for this candidate profile against market requirements:

CANDIDATE CURRENT SKILLS:
{candidate_skills}

TARGET ROLE REQUIREMENTS:
{role_requirements}

MARKET DEMAND DATA:
{market_data}

Provide detailed analysis in this JSON format:
{
  "skill_gaps_analysis": {
    "critical_gaps": [
      {
        "skill": "skill name",
        "current_level": "none|beginner|intermediate|advanced|expert",
        "required_level": "beginner|intermediate|advanced|expert", 
        "gap_severity": "minor|moderate|significant|critical",
        "market_demand": "low|medium|high|critical",
        "learning_difficulty": "easy|moderate|challenging|expert_level",
        "estimated_learning_time_hours": number,
        "salary_impact_percentage": number,
        "why_important": "Explanation of why this skill is crucial",
        "learning_path": [
          "Step 1: Specific learning recommendation",
          "Step 2: Next step"
        ],
        "recommended_resources": [
          {"type": "course|certification|project|book", "name": "resource name", "url": "optional"}
        ]
      }
    ],
    "transferable_skills": [
      {
        "current_skill": "skill you have",
        "transferable_to": "related skill needed",
        "transfer_difficulty": "easy|moderate|challenging",
        "additional_learning_needed": "what else to learn"
      }
    ],
    "skill_strengths": [
      {
        "skill": "skill name", 
        "competitive_advantage": "how this skill gives you an edge",
        "market_value": "high|medium|low"
      }
    ],
    "development_recommendations": {
      "immediate_priorities": ["skill1", "skill2"],
      "short_term_goals": ["3-6 month objectives"],
      "long_term_development": ["6+ month objectives"],
      "alternative_paths": ["Alternative career paths to consider"]
    }
  }
}
    """
}
```

## API Endpoints
### Skill Gap Analysis Endpoints
```
POST /skill-gaps/analyze
Headers: Authorization: Bearer <token>
Body: {
  target_roles?: ["Software Engineer", "Data Scientist"],
  analysis_type: "comprehensive" | "role_specific" | "market_trends"
}
Response: {
  success: true,
  data: {
    analysis_id: "uuid",
    total_gaps_identified: 12,
    critical_gaps: 3,
    high_priority_gaps: 5,
    analysis_confidence: 87.5,
    processing_time: 8500,
    expires_at: "2024-02-01T00:00:00Z"
  }
}

GET /skill-gaps/{analysis_id}
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    id: "uuid",
    analysis_type: "comprehensive",
    created_at: "2024-01-01T00:00:00Z",
    gaps: [
      {
        skill_name: "React",
        skill_category: "technical",
        current_proficiency: "beginner", 
        required_proficiency: "advanced",
        priority_ranking: "critical",
        priority_score: 92.5,
        market_demand: "high",
        salary_impact_percentage: 15.0,
        learning_difficulty: "moderate",
        estimated_learning_hours: 80,
        recommended_resources: [
          {
            "type": "course",
            "name": "React Complete Guide",
            "provider": "Udemy",
            "estimated_hours": 40
          }
        ],
        learning_path: [
          "Complete React fundamentals course",
          "Build 2-3 personal projects",
          "Learn React ecosystem (Redux, Router)"
        ]
      }
    ],
    market_insights: {
      "trending_skills": ["AI/ML", "Cloud Computing"],
      "declining_skills": ["jQuery", "Flash"],
      "emerging_opportunities": ["Web3 Development"]
    },
    development_recommendations: {
      "immediate_priorities": ["React", "Node.js"],
      "timeline": "Focus on React for next 2-3 months"
    }
  }
}

GET /skill-gaps/summary
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    latest_analysis: {
      "analysis_id": "uuid",
      "created_at": "2024-01-01T00:00:00Z",
      "total_gaps": 12,
      "critical_count": 3
    },
    gap_trends: {
      "improving_areas": ["Frontend Development"],
      "areas_needing_attention": ["Cloud Platforms", "DevOps"]
    },
    active_development_goals": [
      {
        "skill": "React",
        "progress": 35.0,
        "target_date": "2024-03-01"
      }
    ]
  }
}
```

## Frontend Tasks
### Skill Gap Display Components
```tsx
const SkillGapDashboard: React.FC<{
  analysis: SkillGapAnalysis;
  onStartLearning: (skillGap: SkillGap) => void;
}> = ({ analysis, onStartLearning }) => {
  // Overview metrics (total gaps, priorities breakdown)
  // Gap categories with filtering and sorting
  // Priority-based visualization
  // Quick action buttons for top priorities
};

const SkillGapCard: React.FC<{
  gap: SkillGap;
  onViewDetails: () => void;
  onStartLearning: () => void;
}> = ({ gap, onViewDetails, onStartLearning }) => {
  // Skill name and category
  // Priority indicator with color coding
  // Current vs required proficiency levels
  // Market demand and salary impact
  // Learning time estimate
  // Action buttons (learn, details)
};

const SkillGapDetail: React.FC<{
  gap: SkillGap;
  onCreateGoal: (learningPlan: LearningPlan) => void;
}> = ({ gap, onCreateGoal }) => {
  // Detailed gap analysis and explanation
  // Learning path recommendations
  // Resource suggestions with links
  // Progress tracking setup
  // Goal creation form
};

const PriorityIndicator: React.FC<{
  priority: 'critical' | 'high' | 'medium' | 'low';
  score?: number;
}> = ({ priority, score }) => {
  // Color-coded priority badge
  // Score visualization if provided
  // Tooltip with priority explanation
};
```

### Gap Analysis Visualization
```tsx
const SkillGapMatrix: React.FC<{
  gaps: SkillGap[];
  onSkillSelect: (skill: string) => void;
}> = ({ gaps, onSkillSelect }) => {
  // 2D visualization: Market Demand vs Learning Difficulty
  // Bubble size represents salary impact
  // Interactive skill selection
  // Quadrant-based recommendations
};

const GapTrendsChart: React.FC<{
  trendData: GapTrendData[];
}> = ({ trendData }) => {
  // Timeline showing gap progress over time
  // Skills being learned and completed
  // Market trend indicators
  // Progress predictions
};
```

## Business Rules
### Gap Analysis Rules
- Skill gaps recalculated when profile or market data changes significantly
- Priority scoring considers market demand, salary impact, and learning difficulty
- Critical gaps require immediate attention (next 1-3 months)
- High priority gaps recommended for short-term focus (3-6 months)
- Analysis expires after 30 days to ensure freshness

### Learning Recommendations
- Resources recommended based on candidate's learning style preferences
- Time estimates adjusted for candidate's experience level and availability
- Certification paths prioritized for skills with formal validation needs
- Alternative skills suggested when primary skills have high learning barriers
- Progress tracking integrated with goal-setting and milestone achievements

### Market Data Integration
- Skill demand data updated weekly from job market analysis
- Trending skills identified through growth rate analysis
- Geographic considerations factored into demand calculations
- Industry-specific skill requirements incorporated when available
- Salary impact data based on regional compensation surveys

## Acceptance Criteria
### Analysis Accuracy
- [ ] Gap identification accuracy >85% compared to manual expert analysis
- [ ] Priority rankings correlate with actual career advancement impact
- [ ] Market demand data reflects current job posting trends
- [ ] Learning time estimates within 20% of actual completion times
- [ ] Resource recommendations relevant and up-to-date

### Performance Requirements  
- [ ] Gap analysis completes within 10 seconds for typical profiles
- [ ] Dashboard loads and displays results within 3 seconds
- [ ] Market data updates don't impact analysis performance
- [ ] Batch analysis supports multiple users simultaneously
- [ ] Mobile interface fully functional for gap review

### User Experience
- [ ] Gap priorities clearly explained and actionable
- [ ] Learning recommendations specific and achievable
- [ ] Progress tracking motivates continued development
- [ ] Visual indicators help users understand urgency and impact
- [ ] Integration with job matching provides relevant context

## Dependencies
### Depends On
- **Feature 4**: Candidate Profile (current skills and proficiency data)
- **Feature 6**: AI Matching (job requirements and market insights)
- **Feature 5**: Job Discovery (market skill demand analysis)

### Used By
- **Feature 8**: Career Recommendations (skill gaps inform career paths)
- **Feature 9**: Learning Roadmap (creates learning plans for identified gaps)
- **Feature 11**: Career Snapshot (preserves gap analysis over time)

### Produces
- Prioritized skill gap identification and analysis
- Market-driven skill development recommendations
- Learning resource suggestions and pathways
- Progress tracking framework for skill development

## Notes
### Development Priorities
1. Core gap analysis with AI integration
2. Priority calculation and ranking system
3. Market data integration and trending analysis
4. User interface for gap visualization and planning
5. Learning resource recommendation engine
6. Progress tracking and goal management features