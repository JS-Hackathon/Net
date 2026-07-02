# Feature 11: Career Snapshot

## Overview
Implement comprehensive career snapshot system that captures immutable point-in-time records of candidate profiles, analysis results, and career progress to enable historical tracking, progress comparison, and career development insights over time.

## Goal
Provide candidates with the ability to capture and preserve their career state at key moments, enabling progress tracking, goal achievement validation, and data-driven career development insights through historical comparison.

## User Story
As a **Candidate**,
I want to save snapshots of my career analysis and progress
So that I can track my professional development over time and measure my growth.

As a **Candidate**,
I want to compare my current state with previous snapshots
So that I can see how I've improved and identify areas that still need attention.

## Functional Requirements
### Snapshot Creation & Management
- Capture comprehensive career snapshots including profile, skills, analysis results
- Support manual snapshot creation and automatic triggered snapshots
- Preserve complete state data with immutable storage (no updates allowed)
- Include metadata about snapshot context and triggers
- Support snapshot naming and categorization for easy reference
- Provide snapshot scheduling for regular career progress tracking

### Comprehensive Data Capture
- Complete candidate profile data (skills, experience, education)
- All analysis results (skill gaps, career recommendations, learning progress)
- Job matching results and application tracking data
- Interview performance metrics and improvement trends
- Learning roadmap progress and milestone achievements
- Market context and external factors at time of snapshot

### Historical Analysis & Insights
- Compare snapshots to identify growth trends and improvements
- Generate progress reports showing skill development over time
- Track goal achievement and career milestone completion
- Identify patterns in career development and decision making
- Provide insights into successful strategies and approaches
- Export comprehensive career portfolios and progress documentation

## Non-functional Requirements
- Snapshot creation time: <5 seconds for complete data capture
- Data integrity: 100% immutable storage with verification checksums
- Storage efficiency: Optimized data storage to handle years of snapshots
- Query performance: Fast retrieval and comparison of historical data
- Data retention: Long-term storage with backup and recovery capabilities
- Privacy control: User control over snapshot visibility and sharing

## Backend Tasks
### Database Schema
```sql
-- Career snapshot master records (immutable)
CREATE TABLE career_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Snapshot metadata
    snapshot_name VARCHAR(255) NOT NULL,
    snapshot_description TEXT,
    snapshot_type VARCHAR(100), -- manual, scheduled, milestone_triggered, analysis_triggered
    trigger_context JSONB, -- What triggered this snapshot (goal achievement, etc.)
    
    -- Snapshot scope
    includes_profile BOOLEAN DEFAULT TRUE,
    includes_analysis BOOLEAN DEFAULT TRUE,
    includes_learning_progress BOOLEAN DEFAULT TRUE,
    includes_interview_data BOOLEAN DEFAULT TRUE,
    includes_job_matching BOOLEAN DEFAULT TRUE,
    
    -- Data integrity
    data_checksum VARCHAR(64), -- SHA-256 hash for integrity verification
    snapshot_version VARCHAR(20), -- Data schema version
    compression_used BOOLEAN DEFAULT FALSE,
    
    -- Context and environment
    market_context JSONB, -- Job market state at time of snapshot
    user_goals_at_time JSONB, -- User's goals and priorities when snapshot taken
    external_factors JSONB, -- Economic conditions, industry trends, etc.
    
    -- Timestamps (immutable)
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    
    -- Prevent updates
    CONSTRAINT no_updates CHECK (created_at IS NOT NULL)
);

-- Snapshot data storage (compressed JSON)
CREATE TABLE snapshot_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id UUID REFERENCES career_snapshots(id) ON DELETE CASCADE,
    
    -- Data categories
    data_category VARCHAR(100) NOT NULL, -- profile, skills, analysis, learning, interviews, matching
    data_subcategory VARCHAR(100), -- More specific categorization
    
    -- Snapshot data (immutable JSON)
    snapshot_data JSONB NOT NULL,
    data_size_bytes INTEGER,
    
    -- Data source tracking
    source_table VARCHAR(100), -- Original table name
    source_record_id UUID, -- Original record ID
    source_record_version VARCHAR(50), -- Version of source record at snapshot time
    
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- Snapshot comparison results (cached for performance)
CREATE TABLE snapshot_comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Comparison metadata
    baseline_snapshot_id UUID REFERENCES career_snapshots(id) ON DELETE CASCADE,
    comparison_snapshot_id UUID REFERENCES career_snapshots(id) ON DELETE CASCADE,
    comparison_name VARCHAR(255),
    
    -- Comparison results
    overall_progress_score DECIMAL(5,2), -- 0-100 overall improvement
    skills_improvement_score DECIMAL(5,2),
    experience_growth_score DECIMAL(5,2),
    learning_progress_score DECIMAL(5,2),
    interview_improvement_score DECIMAL(5,2),
    
    -- Detailed analysis
    improvements_summary JSONB, -- Key improvements identified
    regressions_summary JSONB, -- Areas that declined (if any)
    new_achievements JSONB, -- New skills, certifications, etc.
    goal_completions JSONB, -- Goals achieved between snapshots
    
    -- Progress insights
    success_factors JSONB, -- What contributed to positive changes
    growth_patterns JSONB, -- Patterns in development
    recommendations JSONB, -- Suggestions based on comparison
    
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '90 days') -- Cache expiry
);

-- Snapshot sharing and portfolio generation
CREATE TABLE snapshot_portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Portfolio configuration
    portfolio_name VARCHAR(255) NOT NULL,
    portfolio_description TEXT,
    included_snapshots JSONB, -- Array of snapshot IDs
    portfolio_template VARCHAR(100), -- professional, academic, executive
    
    -- Content configuration
    include_sections JSONB, -- Which sections to include
    privacy_settings JSONB, -- What data to show/hide
    branding_options JSONB, -- Colors, logos, styling preferences
    
    -- Generated outputs
    pdf_url VARCHAR(500), -- Generated PDF portfolio
    web_portfolio_url VARCHAR(500), -- Web-viewable version
    last_generated_at TIMESTAMP,
    
    -- Access control
    is_public BOOLEAN DEFAULT FALSE,
    share_token VARCHAR(100) UNIQUE, -- For secure sharing
    access_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Automated snapshot triggers
CREATE TABLE snapshot_triggers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Trigger configuration
    trigger_name VARCHAR(255) NOT NULL,
    trigger_type VARCHAR(100), -- scheduled, goal_achievement, skill_milestone, analysis_update
    trigger_condition JSONB, -- Specific conditions that activate trigger
    
    -- Snapshot configuration for trigger
    snapshot_name_template VARCHAR(255), -- Template for auto-generated names
    include_data_types JSONB, -- What data to include in triggered snapshots
    
    -- Trigger state
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMP,
    next_trigger_date TIMESTAMP, -- For scheduled triggers
    total_snapshots_created INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance and integrity
CREATE INDEX idx_career_snapshots_user_created ON career_snapshots(user_id, created_at DESC);
CREATE INDEX idx_career_snapshots_type ON career_snapshots(snapshot_type, created_at DESC);
CREATE INDEX idx_snapshot_data_snapshot_id ON snapshot_data(snapshot_id, data_category);
CREATE INDEX idx_snapshot_comparisons_user ON snapshot_comparisons(user_id, created_at DESC);
CREATE INDEX idx_snapshot_portfolios_user ON snapshot_portfolios(user_id, updated_at DESC);
CREATE INDEX idx_snapshot_triggers_user_active ON snapshot_triggers(user_id, is_active);

-- Immutability constraints
ALTER TABLE career_snapshots ADD CONSTRAINT immutable_snapshot 
    CHECK (created_at = created_at); -- Prevents updates
ALTER TABLE snapshot_data ADD CONSTRAINT immutable_data 
    CHECK (created_at = created_at); -- Prevents updates
```

### Career Snapshot Service
```python
class CareerSnapshotService:
    def __init__(self, data_aggregator: DataAggregator, comparison_engine: ComparisonEngine):
        self.data_aggregator = data_aggregator
        self.comparison_engine = comparison_engine
        self.portfolio_generator = PortfolioGenerator()
    
    async def create_career_snapshot(self, user_id: UUID, snapshot_config: SnapshotConfig) -> CareerSnapshot:
        # Gather all relevant user data
        snapshot_data = await self.data_aggregator.gather_complete_user_data(
            user_id=user_id,
            include_profile=snapshot_config.includes_profile,
            include_analysis=snapshot_config.includes_analysis,
            include_learning=snapshot_config.includes_learning_progress,
            include_interviews=snapshot_config.includes_interview_data,
            include_matching=snapshot_config.includes_job_matching
        )
        
        # Capture market context and external factors
        market_context = await self.capture_market_context(user_id)
        user_goals = await self.capture_user_goals_state(user_id)
        
        # Calculate data integrity checksum
        data_checksum = await self.calculate_data_checksum(snapshot_data)
        
        # Store immutable snapshot
        snapshot_record = await self.store_snapshot(
            user_id=user_id,
            config=snapshot_config,
            data=snapshot_data,
            market_context=market_context,
            user_goals=user_goals,
            checksum=data_checksum
        )
        
        return CareerSnapshot(
            snapshot_id=snapshot_record.id,
            created_at=snapshot_record.created_at,
            data_summary=await self.generate_snapshot_summary(snapshot_data),
            integrity_verified=True
        )
    
    async def compare_snapshots(self, user_id: UUID, baseline_id: UUID, comparison_id: UUID) -> SnapshotComparison:
        # Verify user owns both snapshots
        await self.verify_snapshot_ownership(user_id, [baseline_id, comparison_id])
        
        # Retrieve snapshot data
        baseline_data = await self.get_snapshot_data(baseline_id)
        comparison_data = await self.get_snapshot_data(comparison_id)
        
        # Perform comprehensive comparison analysis
        comparison_result = await self.comparison_engine.compare_career_states(
            baseline=baseline_data,
            comparison=comparison_data
        )
        
        # Generate insights and recommendations
        insights = await self.generate_comparison_insights(comparison_result)
        
        # Cache comparison results
        comparison_record = await self.store_comparison_results(
            user_id, baseline_id, comparison_id, comparison_result, insights
        )
        
        return SnapshotComparison(
            comparison_id=comparison_record.id,
            overall_progress=comparison_result.overall_progress_score,
            detailed_changes=comparison_result.detailed_analysis,
            insights=insights,
            recommendations=comparison_result.recommendations
        )
    
    async def generate_career_portfolio(self, user_id: UUID, portfolio_config: PortfolioConfig) -> CareerPortfolio:
        # Retrieve selected snapshots
        snapshots = await self.get_user_snapshots(user_id, portfolio_config.included_snapshots)
        
        # Generate portfolio content based on template
        portfolio_content = await self.portfolio_generator.generate_portfolio(
            snapshots=snapshots,
            template=portfolio_config.portfolio_template,
            privacy_settings=portfolio_config.privacy_settings,
            branding_options=portfolio_config.branding_options
        )
        
        # Generate PDF and web versions
        pdf_url = await self.portfolio_generator.generate_pdf(portfolio_content)
        web_url = await self.portfolio_generator.generate_web_version(portfolio_content)
        
        # Store portfolio record
        portfolio_record = await self.store_portfolio(
            user_id, portfolio_config, pdf_url, web_url
        )
        
        return CareerPortfolio(
            portfolio_id=portfolio_record.id,
            pdf_url=pdf_url,
            web_url=web_url,
            share_token=portfolio_record.share_token
        )
```

## API Endpoints
### Career Snapshot Endpoints
```
POST /career-snapshots/create
Headers: Authorization: Bearer <token>
Body: {
  snapshot_name: "Q1 2024 Career Progress",
  snapshot_description?: "Quarterly review after completing React certification",
  snapshot_type?: "manual", // manual, scheduled, milestone_triggered
  includes: {
    profile: true,
    analysis: true,
    learning_progress: true,
    interview_data: true,
    job_matching: true
  },
  trigger_context?: {
    "milestone": "Completed React Certification",
    "goal_achieved": "Frontend Developer Readiness"
  }
}
Response: {
  success: true,
  data: {
    snapshot_id: "uuid",
    snapshot_name: "Q1 2024 Career Progress",
    created_at: "2024-03-31T23:59:59Z",
    data_summary: {
      profile_completeness: 92.5,
      skills_count: 28,
      analysis_results_included: 5,
      learning_milestones: 12,
      interview_sessions: 3,
      job_matches: 45
    },
    integrity_checksum: "sha256hash...",
    storage_size_mb: 2.3
  }
}

GET /career-snapshots
Headers: Authorization: Bearer <token>
Query: ?limit=20&type=manual&sort=created_at_desc
Response: {
  success: true,
  data: {
    snapshots: [
      {
        snapshot_id: "uuid",
        snapshot_name: "Q1 2024 Career Progress",
        snapshot_type: "manual",
        created_at: "2024-03-31T23:59:59Z",
        data_summary: {
          profile_completeness: 92.5,
          skills_count: 28,
          total_data_points: 156
        },
        can_compare: true
      }
    ],
    pagination: {
      total: 8,
      page: 1,
      has_more: false
    }
  }
}

GET /career-snapshots/{snapshot_id}
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    snapshot_id: "uuid",
    snapshot_name: "Q1 2024 Career Progress",
    created_at: "2024-03-31T23:59:59Z",
    snapshot_data: {
      profile: {
        completeness_score: 92.5,
        skills: [
          {
            name: "React",
            proficiency: "Advanced",
            snapshot_date: "2024-03-31"
          }
        ],
        experience_summary: "3.2 years total experience"
      },
      analysis_results: {
        skill_gaps_count: 5,
        career_recommendations_count: 3,
        learning_roadmaps_active: 2
      },
      learning_progress: {
        total_learning_hours: 145.5,
        milestones_achieved: 12,
        current_roadmaps: 2
      },
      interview_performance: {
        sessions_completed: 3,
        average_score: 78.2,
        improvement_trend: "positive"
      }
    },
    market_context: {
      job_market_state: "strong",
      skill_demand_trends: "React demand increasing 15% YoY",
      salary_ranges_updated: "2024-03-30"
    }
  }
}

POST /career-snapshots/compare
Headers: Authorization: Bearer <token>
Body: {
  baseline_snapshot_id: "uuid_old",
  comparison_snapshot_id: "uuid_new",
  comparison_name?: "Q4 2023 vs Q1 2024 Progress"
}
Response: {
  success: true,
  data: {
    comparison_id: "uuid",
    time_period: {
      start_date: "2023-12-31T23:59:59Z",
      end_date: "2024-03-31T23:59:59Z",
      duration_days: 91
    },
    overall_progress: {
      overall_score: 87.3,
      improvement_summary: "Strong growth in technical skills and interview performance"
    },
    detailed_changes: {
      skills_progress: {
        new_skills_added: 5,
        skills_improved: 8,
        proficiency_increases: [
          {
            skill: "React",
            from: "Intermediate",
            to: "Advanced",
            improvement_factor: 2.1
          }
        ]
      },
      learning_achievements: {
        milestones_completed: 12,
        learning_hours_invested: 75.5,
        certifications_earned: ["React Developer Certification"]
      },
      interview_improvement: {
        score_improvement: 15.3,
        consistency_improvement: "Much more consistent performance",
        new_strengths: ["Technical communication", "Problem-solving clarity"]
      }
    },
    insights: {
      success_factors: [
        "Consistent daily learning schedule",
        "Regular interview practice",
        "Focus on hands-on projects"
      ],
      growth_patterns: [
        "Accelerated learning in frontend technologies",
        "Steady improvement in communication skills"
      ],
      recommendations: [
        "Continue current learning pace",
        "Consider advanced React patterns",
        "Add backend skills for full-stack capability"
      ]
    }
  }
}

POST /career-snapshots/portfolio
Headers: Authorization: Bearer <token>
Body: {
  portfolio_name: "Professional Development Portfolio 2024",
  included_snapshots: ["uuid1", "uuid2", "uuid3"],
  portfolio_template: "professional", // professional, academic, executive
  privacy_settings: {
    include_salary_data: false,
    include_personal_info: true,
    include_contact_details: true
  },
  branding_options: {
    primary_color: "#2563eb",
    include_photo: true,
    style: "modern"
  }
}
Response: {
  success: true,
  data: {
    portfolio_id: "uuid",
    portfolio_name: "Professional Development Portfolio 2024",
    pdf_url: "https://signed-url-to-portfolio.pdf",
    web_portfolio_url: "https://portfolio.mockai.com/shared/uuid",
    share_token: "secure_token_123",
    expires_at: "2025-03-31T23:59:59Z",
    generation_summary: {
      pages_generated: 8,
      sections_included: ["Profile Summary", "Skills Growth", "Learning Journey", "Achievements"],
      snapshots_analyzed: 3,
      time_period_covered: "6 months"
    }
  }
}
```

## Frontend Tasks & Business Rules
### Snapshot Visualization Components
```tsx
const SnapshotDashboard: React.FC<{
  snapshots: CareerSnapshot[];
  onCreateSnapshot: () => void;
  onCompareSnapshots: (id1: string, id2: string) => void;
}> = ({ snapshots, onCreateSnapshot, onCompareSnapshots }) => {
  // Timeline view of all snapshots
  // Quick comparison interface
  // Snapshot creation button
  // Performance trends visualization
};

const SnapshotComparison: React.FC<{
  comparison: SnapshotComparisonResult;
}> = ({ comparison }) => {
  // Side-by-side comparison visualization
  // Progress indicators and improvements
  // Skills growth charts
  // Achievement timeline
  // Insights and recommendations
};
```

### Business Rules & Quality Standards
- Snapshots are completely immutable once created (no updates allowed)
- Minimum 24-hour interval between automatic snapshots to prevent spam
- Data integrity verified with checksums on creation and retrieval
- Portfolio sharing expires after 1 year unless renewed
- Comparison analysis cached for 90 days for performance

### Performance Requirements & Acceptance Criteria
- [ ] Snapshot creation completes within 5 seconds for comprehensive data
- [ ] Snapshot comparisons complete within 3 seconds using cached results
- [ ] Portfolio generation completes within 10 seconds for standard templates
- [ ] Historical data retrieval maintains <2 second response times
- [ ] Data integrity verification passes 100% of checksum validations

## Dependencies
### Depends On
- **Feature 4**: Candidate Profile (profile data for snapshots)
- **Feature 7**: Skill Gap Analysis (analysis results to preserve)
- **Feature 8**: Career Recommendations (recommendation data)
- **Feature 9**: Learning Roadmap (learning progress data)
- **Feature 10**: Mock Interview (interview performance data)

### Used By
- **Feature 12**: Analysis History (uses snapshots for historical analysis)
- External portfolio sharing (web portfolios and PDF exports)

### Produces
- Immutable career progress records and historical data
- Career development analytics and trend identification
- Professional portfolio generation and sharing capabilities
- Long-term career development insights and pattern recognition

## Notes
### Development Priorities
1. Core snapshot creation and immutable data storage
2. Comprehensive data comparison and analysis engine
3. Timeline visualization and progress tracking interface
4. Portfolio generation with professional templates
5. Advanced analytics and insight generation
6. Automated snapshot triggers and scheduling system