# Feature 9: Learning Roadmap

## Overview
Implement AI-powered personalized learning roadmap generation that creates structured, time-bound learning plans based on skill gaps, career recommendations, and individual learning preferences with progress tracking and adaptive planning.

## Goal
Provide candidates with actionable, personalized learning roadmaps that efficiently bridge skill gaps and support career advancement through structured learning paths with clear milestones and progress tracking.

## User Story
As a **Candidate**,
I want a personalized learning roadmap for my career goals
So that I can systematically develop the skills needed for my target career path.

As a **Candidate**,
I want to track my learning progress and adjust my plan
So that I can stay motivated and adapt to changing priorities or circumstances.

## Functional Requirements
### Learning Plan Generation
- Create comprehensive learning roadmaps based on skill gap analysis and career goals
- Generate week-by-week learning schedules with specific objectives
- Integrate multiple learning modalities (courses, projects, reading, practice)
- Prioritize learning items based on urgency and impact
- Account for individual learning pace and time availability
- Provide alternative learning paths for different learning styles

### Adaptive Planning & Personalization
- Customize roadmaps based on learning preferences and constraints
- Adjust timelines based on progress and changing priorities
- Integrate feedback to improve future roadmap generation
- Account for existing commitments and available study time
- Provide difficulty progression from beginner to advanced levels
- Support multiple concurrent skill development tracks

### Progress Tracking & Motivation
- Track completion of learning milestones and objectives
- Provide progress visualization and achievement celebrations
- Generate progress reports and skill development analytics
- Identify learning bottlenecks and suggest adjustments
- Gamification elements to maintain engagement and motivation
- Integration with external learning platforms for automatic progress sync

## Non-functional Requirements
- Roadmap generation time: <5 seconds for comprehensive plans
- Progress tracking: Real-time updates with <1 second response time
- Learning resource accuracy: >90% of suggested resources are active and relevant
- Personalization quality: Roadmaps adapt based on user feedback and progress
- Mobile accessibility: Full functionality on mobile devices for on-the-go learning
- Integration capability: Connect with popular learning platforms (Coursera, Udemy, etc.)

## Backend Tasks
### Database Schema
```sql
-- Learning roadmap master records
CREATE TABLE learning_roadmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Roadmap context
    career_goal VARCHAR(255), -- Target career or role
    skill_gap_analysis_id UUID REFERENCES skill_gap_analyses(id),
    career_recommendation_id UUID REFERENCES career_recommendations(id),
    
    -- Roadmap configuration
    roadmap_name VARCHAR(255) NOT NULL,
    roadmap_description TEXT,
    total_duration_weeks INTEGER,
    weekly_study_hours INTEGER, -- Expected weekly time commitment
    difficulty_level VARCHAR(50), -- beginner, intermediate, advanced, mixed
    learning_style VARCHAR(100), -- visual, auditory, kinesthetic, reading, mixed
    
    -- Progress tracking
    overall_progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    current_week INTEGER DEFAULT 1,
    weeks_completed INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active', -- active, paused, completed, abandoned
    
    -- Metadata
    ai_generation_version VARCHAR(50),
    last_updated_by VARCHAR(50) DEFAULT 'system', -- system, user, adaptive
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    target_completion_date DATE
);

-- Weekly learning plans within roadmaps
CREATE TABLE learning_weeks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    roadmap_id UUID REFERENCES learning_roadmaps(id) ON DELETE CASCADE,
    
    -- Week details
    week_number INTEGER NOT NULL,
    week_theme VARCHAR(255), -- Main focus for the week
    week_description TEXT,
    estimated_hours INTEGER, -- Expected time investment
    
    -- Learning objectives
    primary_objectives JSONB, -- Main learning goals for the week
    secondary_objectives JSONB, -- Optional/bonus objectives
    prerequisite_weeks JSONB, -- Array of week numbers that should be completed first
    
    -- Progress tracking
    completion_percentage DECIMAL(5,2) DEFAULT 0.00,
    status VARCHAR(50) DEFAULT 'not_started', -- not_started, in_progress, completed, skipped
    actual_hours_spent DECIMAL(6,2) DEFAULT 0.00,
    
    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    due_date DATE
);

-- Individual learning items/tasks within weeks
CREATE TABLE learning_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learning_week_id UUID REFERENCES learning_weeks(id) ON DELETE CASCADE,
    
    -- Item details
    item_title VARCHAR(500) NOT NULL,
    item_description TEXT,
    item_type VARCHAR(100), -- course, project, reading, practice, assessment, research
    priority INTEGER DEFAULT 3, -- 1=critical, 2=high, 3=medium, 4=low, 5=optional
    
    -- Learning resource
    resource_url VARCHAR(1000),
    resource_provider VARCHAR(255), -- Coursera, Udemy, YouTube, etc.
    resource_cost DECIMAL(8,2), -- Cost if not free
    estimated_duration_hours DECIMAL(5,2),
    
    -- Skills and outcomes
    target_skills JSONB, -- Skills this item develops
    learning_outcomes JSONB, -- What the learner should achieve
    assessment_criteria JSONB, -- How to verify completion/understanding
    
    -- Progress and completion
    completion_status VARCHAR(50) DEFAULT 'not_started', -- not_started, in_progress, completed, skipped
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    completion_notes TEXT, -- User notes about completion
    quality_rating INTEGER CHECK (quality_rating >= 1 AND quality_rating <= 5),
    
    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Learning milestones and achievements
CREATE TABLE learning_milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    roadmap_id UUID REFERENCES learning_roadmaps(id) ON DELETE CASCADE,
    
    -- Milestone details
    milestone_name VARCHAR(255) NOT NULL,
    milestone_description TEXT,
    milestone_type VARCHAR(100), -- skill_mastery, project_completion, certification, assessment
    target_week INTEGER, -- Expected completion week
    
    -- Achievement criteria
    completion_criteria JSONB, -- What needs to be accomplished
    verification_method VARCHAR(100), -- self_assessment, project_review, test, certification
    points_awarded INTEGER DEFAULT 0, -- Gamification points
    
    -- Status and progress
    status VARCHAR(50) DEFAULT 'pending', -- pending, achieved, missed, deferred
    achievement_date TIMESTAMP,
    evidence_url VARCHAR(1000), -- Link to project, certificate, etc.
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Roadmap adaptations and modifications
CREATE TABLE roadmap_adaptations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    roadmap_id UUID REFERENCES learning_roadmaps(id) ON DELETE CASCADE,
    
    -- Adaptation details
    adaptation_type VARCHAR(100), -- schedule_adjustment, content_change, difficulty_change, pace_adjustment
    adaptation_reason VARCHAR(100), -- user_request, progress_analysis, external_change, skill_gap_update
    
    -- Changes made
    changes_description TEXT,
    affected_weeks JSONB, -- Array of week numbers affected
    old_configuration JSONB, -- Previous state for rollback
    new_configuration JSONB, -- New state after adaptation
    
    -- Impact assessment
    impact_assessment TEXT,
    expected_outcome TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(50) -- user, system, ai_recommendation
);

-- Indexes for performance
CREATE INDEX idx_learning_roadmaps_user_id ON learning_roadmaps(user_id, status);
CREATE INDEX idx_learning_roadmaps_created_at ON learning_roadmaps(created_at DESC);
CREATE INDEX idx_learning_weeks_roadmap_id ON learning_weeks(roadmap_id, week_number);
CREATE INDEX idx_learning_items_week_id ON learning_items(learning_week_id, priority);
CREATE INDEX idx_learning_milestones_roadmap ON learning_milestones(roadmap_id, target_week);
```

### Learning Roadmap Service
```python
class LearningRoadmapService:
    def __init__(self, gemini_client: GeminiClient, resource_curator: ResourceCurator):
        self.gemini_client = gemini_client
        self.resource_curator = resource_curator
        self.progress_tracker = ProgressTracker()
    
    async def generate_learning_roadmap(self, user_id: UUID, roadmap_config: RoadmapConfig) -> LearningRoadmapResult:
        # Get skill gaps and career goals context
        skill_gaps = await self.get_user_skill_gaps(user_id, roadmap_config.skill_gap_analysis_id)
        career_goals = await self.get_career_recommendations(user_id, roadmap_config.career_recommendation_id)
        user_preferences = await self.get_user_learning_preferences(user_id)
        
        # Generate AI-powered learning plan
        ai_roadmap = await self.generate_ai_learning_plan(
            skill_gaps, career_goals, user_preferences, roadmap_config
        )
        
        # Curate and validate learning resources
        curated_roadmap = await self.curate_learning_resources(ai_roadmap)
        
        # Create structured weekly plans
        weekly_plans = await self.structure_weekly_learning_plans(curated_roadmap)
        
        # Generate milestones and assessments
        milestones = await self.create_learning_milestones(curated_roadmap, weekly_plans)
        
        # Store roadmap in database
        roadmap_record = await self.store_learning_roadmap(
            user_id, curated_roadmap, weekly_plans, milestones
        )
        
        return LearningRoadmapResult(
            roadmap_id=roadmap_record.id,
            total_weeks=len(weekly_plans),
            estimated_completion_date=roadmap_record.target_completion_date,
            weekly_plans=weekly_plans[:4],  # Return first 4 weeks
            milestones=milestones
        )
    
    async def generate_ai_learning_plan(self, skill_gaps: List[SkillGap], career_goals: List[CareerPath], preferences: UserPreferences, config: RoadmapConfig) -> AILearningPlan:
        # Prepare comprehensive prompt with all context
        learning_prompt = await self.create_learning_roadmap_prompt(
            skill_gaps, career_goals, preferences, config
        )
        
        # Call Gemini for roadmap generation
        ai_response = await self.gemini_client.generate_learning_roadmap(learning_prompt)
        
        # Process and structure AI response
        structured_plan = await self.process_learning_plan_response(ai_response)
        
        # Validate and optimize the plan
        optimized_plan = await self.optimize_learning_sequence(structured_plan, preferences)
        
        return optimized_plan
    
    async def update_progress(self, roadmap_id: UUID, progress_update: ProgressUpdate) -> ProgressResult:
        # Update item/week completion status
        await self.update_learning_item_progress(progress_update.item_id, progress_update)
        
        # Recalculate week and overall progress
        week_progress = await self.calculate_week_progress(progress_update.week_id)
        overall_progress = await self.calculate_overall_progress(roadmap_id)
        
        # Check for milestone achievements
        new_milestones = await self.check_milestone_achievements(roadmap_id, progress_update)
        
        # Assess if roadmap adaptation is needed
        adaptation_needed = await self.assess_adaptation_needs(roadmap_id, overall_progress)
        
        return ProgressResult(
            week_progress=week_progress,
            overall_progress=overall_progress,
            new_milestones=new_milestones,
            adaptation_recommended=adaptation_needed
        )
    
    async def adapt_roadmap(self, roadmap_id: UUID, adaptation_request: AdaptationRequest) -> AdaptationResult:
        # Analyze current progress and bottlenecks
        current_state = await self.analyze_roadmap_state(roadmap_id)
        
        # Generate adaptation recommendations
        adaptations = await self.generate_roadmap_adaptations(current_state, adaptation_request)
        
        # Apply approved adaptations
        if adaptation_request.auto_apply:
            updated_roadmap = await self.apply_adaptations(roadmap_id, adaptations)
            return AdaptationResult(success=True, adaptations_applied=adaptations)
        else:
            return AdaptationResult(success=False, suggested_adaptations=adaptations)
```

## AI Service Tasks
### Learning Roadmap Generation Prompts
```python
LEARNING_ROADMAP_PROMPT_V1 = {
    "version": "1.0",
    "system_prompt": """
You are an expert learning designer and career coach specializing in creating personalized, effective learning roadmaps. Design comprehensive, week-by-week learning plans that efficiently bridge skill gaps and support career advancement.

Focus on:
- Progressive skill building with proper sequencing
- Realistic time commitments and pacing
- Diverse learning modalities (theory, practice, projects)
- Clear milestones and assessment points
- Motivation and engagement throughout the journey
- Practical application and portfolio building
    """,
    "user_prompt": """
Create a personalized learning roadmap based on this analysis:

SKILL GAPS TO ADDRESS:
{skill_gaps}

CAREER GOALS:
{career_goals}

LEARNING PREFERENCES:
{user_preferences}

ROADMAP CONFIGURATION:
{roadmap_config}

Generate a comprehensive learning roadmap in this JSON format:
{
  "roadmap_overview": {
    "roadmap_title": "Descriptive title for the learning journey",
    "total_duration_weeks": number,
    "weekly_time_commitment": number, // hours per week
    "difficulty_progression": "How difficulty increases over time",
    "key_outcomes": ["Primary skill/knowledge outcomes"],
    "success_metrics": ["How to measure success"]
  },
  
  "learning_phases": [
    {
      "phase_name": "Phase title (e.g., 'Foundations', 'Applied Practice')",
      "phase_description": "What this phase accomplishes",
      "weeks": "1-4", // Week range for this phase
      "phase_objectives": ["Main objectives for this phase"]
    }
  ],
  
  "weekly_plans": [
    {
      "week_number": number,
      "week_theme": "Main focus for the week",
      "week_description": "Overview of what will be learned",
      "estimated_hours": number,
      "primary_objectives": [
        "Specific, measurable learning objective"
      ],
      "learning_items": [
        {
          "title": "Specific learning task or activity",
          "type": "course|project|reading|practice|assessment|research",
          "description": "Detailed description of the activity",
          "estimated_hours": number,
          "priority": "critical|high|medium|low|optional",
          "skills_developed": ["skill1", "skill2"],
          "learning_outcomes": ["What learner will be able to do"],
          "resource_suggestions": [
            {
              "type": "course|video|article|book|tutorial|practice_platform",
              "title": "Resource name",
              "provider": "Provider name (if known)",
              "url": "URL if specific resource known",
              "cost": "free|paid|subscription",
              "difficulty": "beginner|intermediate|advanced"
            }
          ],
          "completion_criteria": "How to know this item is completed",
          "assessment_method": "How to verify learning"
        }
      ],
      "milestone_check": "What should be achieved by end of week",
      "next_week_preparation": "How to prepare for the following week"
    }
  ],
  
  "major_milestones": [
    {
      "milestone_name": "Significant achievement marker",
      "target_week": number,
      "description": "What this milestone represents",
      "achievement_criteria": ["Specific criteria to meet milestone"],
      "verification_method": "How to verify milestone completion",
      "celebration_suggestion": "How to acknowledge this achievement"
    }
  ],
  
  "project_portfolio": [
    {
      "project_name": "Portfolio project title",
      "project_description": "What the project involves",
      "skills_demonstrated": ["Skills this project showcases"],
      "target_weeks": "When to work on this project",
      "complexity_level": "beginner|intermediate|advanced",
      "time_investment": "Estimated hours needed",
      "deliverables": ["What should be produced"],
      "career_relevance": "How this project supports career goals"
    }
  ],
  
  "adaptation_guidelines": {
    "faster_pace_options": "How to accelerate if progressing quickly",
    "slower_pace_accommodations": "How to adjust if needing more time", 
    "alternative_paths": "Different approaches for different learning styles",
    "difficulty_adjustments": "How to make content easier or harder",
    "time_constraint_modifications": "Adjustments for limited time availability"
  },
  
  "success_strategies": {
    "motivation_techniques": ["How to stay motivated throughout"],
    "common_challenges": ["Typical obstacles and how to overcome them"],
    "progress_tracking": "How to monitor and measure progress",
    "community_resources": "Where to find support and accountability",
    "troubleshooting": "What to do when stuck or struggling"
  }
}
    """
}
```

## API Endpoints
### Learning Roadmap Endpoints
```
POST /learning-roadmaps/generate
Headers: Authorization: Bearer <token>
Body: {
  roadmap_name: "Frontend Development Mastery",
  career_goal?: "Senior Frontend Developer",
  skill_gap_analysis_id?: "uuid",
  career_recommendation_id?: "uuid",
  configuration: {
    duration_weeks?: 12,
    weekly_hours?: 10,
    difficulty_level?: "intermediate",
    learning_style?: "mixed",
    start_date?: "2024-01-15"
  },
  preferences?: {
    focus_areas: ["React", "TypeScript", "Testing"],
    budget_constraint?: "free_only|under_100|no_limit",
    time_availability?: "evenings|weekends|flexible"
  }
}
Response: {
  success: true,
  data: {
    roadmap_id: "uuid",
    roadmap_name: "Frontend Development Mastery",
    total_weeks: 12,
    weekly_hours: 10,
    estimated_completion_date: "2024-04-15",
    first_week_preview: {
      week_theme: "JavaScript Fundamentals Review",
      primary_objectives: ["Master ES6+ features", "Understand async programming"],
      learning_items_count: 5
    },
    milestones_count: 4
  }
}

GET /learning-roadmaps/{roadmap_id}
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    id: "uuid",
    roadmap_name: "Frontend Development Mastery",
    status: "active",
    overall_progress: 34.5,
    current_week: 4,
    weeks_completed: 3,
    total_weeks: 12,
    weekly_plans: [
      {
        week_number: 4,
        week_theme: "React Component Patterns",
        completion_percentage: 60.0,
        learning_items: [
          {
            title: "Advanced React Patterns Course",
            type: "course",
            priority: "high",
            completion_status: "completed",
            estimated_hours: 6,
            actual_hours: 5.5,
            resource_url: "https://...",
            skills_developed: ["React", "Component Architecture"]
          }
        ]
      }
    ],
    upcoming_milestones: [
      {
        milestone_name: "Build First React Application",
        target_week: 5,
        achievement_criteria: ["Complete todo app with CRUD operations"]
      }
    ]
  }
}

PUT /learning-roadmaps/{roadmap_id}/progress
Headers: Authorization: Bearer <token>
Body: {
  item_id?: "uuid",
  week_id?: "uuid", 
  completion_status?: "completed|in_progress|skipped",
  progress_percentage?: 75.0,
  hours_spent?: 3.5,
  quality_rating?: 4,
  notes?: "Great course, learned component composition patterns"
}
Response: {
  success: true,
  data: {
    updated_item_progress: 100.0,
    updated_week_progress: 80.0,
    updated_overall_progress: 36.2,
    milestones_achieved: [
      {
        milestone_name: "JavaScript Mastery",
        points_awarded: 100,
        achievement_date: "2024-01-28T10:30:00Z"
      }
    ],
    next_recommendations: [
      "Start Week 5: React Component Patterns",
      "Review Week 3 material before moving forward"
    ]
  }
}
```

## Frontend Tasks
### Roadmap Visualization Components
```tsx
const LearningRoadmapDashboard: React.FC<{
  roadmap: LearningRoadmap;
  onUpdateProgress: (update: ProgressUpdate) => void;
}> = ({ roadmap, onUpdateProgress }) => {
  // Overall progress visualization with completion percentage
  // Current week highlight with upcoming objectives
  // Milestone timeline with achievements and upcoming goals
  // Quick actions for common tasks
};

const WeeklyPlanCard: React.FC<{
  week: LearningWeek;
  onItemComplete: (itemId: string) => void;
  onViewDetails: () => void;
}> = ({ week, onItemComplete, onViewDetails }) => {
  // Week theme and objectives display
  // Progress bar for week completion
  // Learning items list with checkboxes
  // Time tracking and estimated vs actual hours
};

const LearningItemTracker: React.FC<{
  item: LearningItem;
  onProgressUpdate: (progress: number, notes?: string) => void;
}> = ({ item, onProgressUpdate }) => {
  // Item details with resource links
  // Progress slider or status toggle
  // Time tracking input
  // Quality rating and notes
  // Completion verification
};

const MilestoneProgress: React.FC<{
  milestones: Milestone[];
  currentWeek: number;
}> = ({ milestones, currentWeek }) => {
  // Timeline visualization of milestones
  // Achievement badges for completed milestones
  // Progress indicators for upcoming milestones
  // Celebration animations for new achievements
};
```

## Business Rules & Acceptance Criteria
### Roadmap Generation Standards
- Weekly plans must have realistic time estimates (5-20 hours per week maximum)
- Learning progression follows logical skill dependencies
- At least 30% hands-on practice and projects included
- Milestones spaced evenly throughout roadmap (every 2-4 weeks)
- Resource recommendations 80% free or low-cost options

### Progress Tracking Requirements
- [ ] Real-time progress updates with <1 second response time
- [ ] Milestone achievement detection and celebration
- [ ] Adaptive recommendations based on progress patterns
- [ ] Weekly and overall progress visualization accuracy >95%
- [ ] Mobile-friendly progress tracking interface

## Dependencies
### Depends On
- **Feature 7**: Skill Gap Analysis (identifies learning priorities)
- **Feature 8**: Career Recommendation (provides career context and goals)
- **Feature 4**: Candidate Profile (learning preferences and constraints)

### Used By
- **Feature 11**: Career Snapshot (preserves learning progress over time)
- External learning platforms (potential API integrations)

### Produces
- Structured learning roadmaps with weekly plans and milestones
- Progress tracking data and learning analytics
- Personalized learning resource recommendations
- Adaptive learning path optimization based on user progress

## Notes
### Development Priorities
1. Core roadmap generation with AI integration
2. Progress tracking and milestone system  
3. Resource curation and recommendation engine
4. Adaptive planning based on progress analysis
5. Learning analytics and insights dashboard
6. Integration with external learning platforms