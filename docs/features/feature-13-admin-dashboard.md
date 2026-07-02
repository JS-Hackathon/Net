# Feature 13: Admin Dashboard

## Overview
Implement comprehensive administrative dashboard and management system providing platform oversight, user management, system monitoring, AI usage tracking, and business analytics for MockAI platform operations.

## Goal
Enable effective platform administration through comprehensive user management, system performance monitoring, AI cost tracking, and business intelligence that supports operational decisions and platform growth.

## User Story
As a **Platform Administrator**,
I want a comprehensive admin dashboard
So that I can monitor platform health, manage users, track costs, and make data-driven operational decisions.

As a **Platform Administrator**,
I want to monitor AI usage and costs
So that I can optimize resource allocation and manage platform expenses effectively.

## Functional Requirements
### User Management & Administration
- Comprehensive user account management with role-based permissions
- User activity monitoring and engagement analytics
- Account status management (active, suspended, banned, premium)
- User support ticket management and communication tools
- Bulk user operations and data management
- User data export and privacy compliance tools

### System Monitoring & Performance
- Real-time system health monitoring and alerting
- Database performance metrics and query analysis
- API endpoint performance tracking and optimization alerts
- External service integration monitoring (Gemini, JSearch, R2)
- Error tracking and incident management
- Capacity planning and resource utilization analysis

### AI Usage Analytics & Cost Management
- Comprehensive AI service usage tracking and cost analysis
- Per-user AI consumption monitoring and quota management
- Cost forecasting and budget management tools
- AI model performance analytics and optimization recommendations
- Usage pattern analysis and anomaly detection
- Cost allocation and billing analytics for different user tiers

## Non-functional Requirements
- Dashboard load time: <2 seconds for all administrative interfaces
- Real-time monitoring: Updates within 30 seconds of system changes
- Data accuracy: 99.9% consistency across all administrative reports
- Security: Role-based access with audit logging for all admin actions
- Scalability: Support monitoring thousands of users and high transaction volumes
- Compliance: GDPR, SOC2, and data protection compliance tools

## Backend Tasks
### Database Schema
```sql
-- Admin user roles and permissions
CREATE TABLE admin_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_name VARCHAR(100) UNIQUE NOT NULL,
    role_description TEXT,
    permissions JSONB NOT NULL, -- Array of permission strings
    is_system_role BOOLEAN DEFAULT FALSE, -- Cannot be deleted
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Admin user assignments
CREATE TABLE admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    admin_role_id UUID REFERENCES admin_roles(id) ON DELETE RESTRICT,
    granted_by UUID REFERENCES users(id), -- Who granted admin access
    granted_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    last_access TIMESTAMP
);

-- System health metrics
CREATE TABLE system_health_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_timestamp TIMESTAMP DEFAULT NOW(),
    
    -- Database metrics
    database_connections_active INTEGER,
    database_connections_max INTEGER,
    database_query_avg_duration_ms DECIMAL(8,2),
    database_slow_queries_count INTEGER,
    
    -- API metrics
    api_requests_per_minute INTEGER,
    api_error_rate DECIMAL(5,2),
    api_avg_response_time_ms INTEGER,
    api_rate_limit_hits INTEGER,
    
    -- External service metrics
    gemini_api_status VARCHAR(50),
    gemini_response_time_ms INTEGER,
    jsearch_api_status VARCHAR(50),
    jsearch_response_time_ms INTEGER,
    r2_storage_status VARCHAR(50),
    
    -- Server metrics
    cpu_usage_percentage DECIMAL(5,2),
    memory_usage_percentage DECIMAL(5,2),
    disk_usage_percentage DECIMAL(5,2),
    
    -- Application metrics
    active_users_count INTEGER,
    sessions_active INTEGER,
    background_jobs_pending INTEGER
);

-- AI usage tracking and cost management
CREATE TABLE ai_usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Usage context
    feature_used VARCHAR(100), -- resume_parsing, job_matching, skill_analysis, etc.
    ai_model VARCHAR(100), -- gemini-pro, gemini-pro-vision, etc.
    
    -- Usage metrics
    tokens_input INTEGER,
    tokens_output INTEGER,
    tokens_total INTEGER,
    processing_duration_ms INTEGER,
    
    -- Cost calculation
    cost_per_token DECIMAL(10,8), -- Cost in USD per token
    total_cost DECIMAL(10,4), -- Total cost for this request
    billing_tier VARCHAR(50), -- free, basic, premium, enterprise
    
    -- Request context
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    cache_hit BOOLEAN DEFAULT FALSE,
    retry_count INTEGER DEFAULT 0,
    
    -- Timestamps
    request_timestamp TIMESTAMP DEFAULT NOW(),
    completion_timestamp TIMESTAMP
);

-- User activity and engagement analytics
CREATE TABLE user_engagement_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    analysis_date DATE DEFAULT CURRENT_DATE,
    
    -- Activity metrics
    login_count INTEGER DEFAULT 0,
    session_duration_minutes INTEGER DEFAULT 0,
    features_used JSONB, -- Array of features accessed
    actions_completed INTEGER DEFAULT 0,
    
    -- Engagement scores
    engagement_score DECIMAL(5,2), -- 0-100 calculated engagement
    activity_level VARCHAR(50), -- inactive, low, medium, high, very_high
    retention_risk_score DECIMAL(5,2), -- 0-100 likelihood of churn
    
    -- Feature usage
    resumes_uploaded INTEGER DEFAULT 0,
    analyses_requested INTEGER DEFAULT 0,
    jobs_searched INTEGER DEFAULT 0,
    interviews_practiced INTEGER DEFAULT 0,
    learning_hours DECIMAL(6,2) DEFAULT 0.00,
    
    -- Value metrics
    profile_completeness DECIMAL(5,2),
    goals_achieved INTEGER DEFAULT 0,
    milestones_reached INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Platform incidents and alerts
CREATE TABLE platform_incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Incident details
    incident_title VARCHAR(255) NOT NULL,
    incident_description TEXT,
    severity_level VARCHAR(50), -- critical, high, medium, low
    incident_type VARCHAR(100), -- outage, performance, security, data
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'open', -- open, investigating, resolved, closed
    impact_assessment TEXT,
    affected_components JSONB, -- Array of affected system components
    affected_users_count INTEGER DEFAULT 0,
    
    -- Timeline
    detected_at TIMESTAMP DEFAULT NOW(),
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    
    -- Response tracking
    assigned_to UUID REFERENCES users(id),
    resolution_summary TEXT,
    lessons_learned TEXT,
    
    -- Monitoring integration
    alert_source VARCHAR(100), -- monitoring_system, user_report, automated
    alert_data JSONB -- Original alert data
);

-- Business analytics and KPIs
CREATE TABLE business_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analytics_date DATE DEFAULT CURRENT_DATE,
    
    -- User metrics
    total_users INTEGER,
    active_users_daily INTEGER,
    active_users_weekly INTEGER,
    active_users_monthly INTEGER,
    new_registrations INTEGER,
    user_churn_rate DECIMAL(5,2),
    
    -- Feature adoption
    resume_uploads_count INTEGER,
    ai_analyses_count INTEGER,
    job_searches_count INTEGER,
    interview_sessions_count INTEGER,
    
    -- AI usage metrics
    total_ai_requests INTEGER,
    ai_cost_total DECIMAL(10,2),
    ai_cost_per_user DECIMAL(8,2),
    ai_success_rate DECIMAL(5,2),
    
    -- Performance metrics
    platform_uptime_percentage DECIMAL(5,2),
    average_response_time_ms INTEGER,
    error_rate DECIMAL(5,2),
    
    -- Business metrics
    conversion_rate DECIMAL(5,2), -- Free to paid conversion
    customer_satisfaction DECIMAL(5,2), -- Survey results
    support_tickets_count INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_system_health_timestamp ON system_health_metrics(metric_timestamp DESC);
CREATE INDEX idx_ai_usage_user_date ON ai_usage_tracking(user_id, request_timestamp DESC);
CREATE INDEX idx_ai_usage_cost_tracking ON ai_usage_tracking(request_timestamp DESC, total_cost DESC);
CREATE INDEX idx_user_engagement_date ON user_engagement_analytics(analysis_date DESC, engagement_score DESC);
CREATE INDEX idx_platform_incidents_status ON platform_incidents(status, severity_level, detected_at DESC);
CREATE INDEX idx_business_analytics_date ON business_analytics(analytics_date DESC);
```

### Admin Dashboard Service
```python
class AdminDashboardService:
    def __init__(self, monitoring_service: MonitoringService, analytics_service: AnalyticsService):
        self.monitoring_service = monitoring_service
        self.analytics_service = analytics_service
        self.user_manager = UserManager()
        
    async def get_dashboard_overview(self, admin_user_id: UUID) -> DashboardOverview:
        # Verify admin permissions
        await self.verify_admin_permissions(admin_user_id, 'dashboard_view')
        
        # Gather real-time system metrics
        system_health = await self.monitoring_service.get_current_system_health()
        
        # Get user and engagement metrics
        user_metrics = await self.analytics_service.get_user_metrics_summary()
        
        # Get AI usage and cost metrics
        ai_metrics = await self.analytics_service.get_ai_usage_summary()
        
        # Get recent incidents and alerts
        recent_incidents = await self.get_recent_incidents(limit=5)
        
        # Calculate key performance indicators
        kpis = await self.calculate_platform_kpis()
        
        return DashboardOverview(
            system_health=system_health,
            user_metrics=user_metrics,
            ai_metrics=ai_metrics,
            recent_incidents=recent_incidents,
            kpis=kpis,
            last_updated=datetime.utcnow()
        )
    
    async def manage_user_account(self, admin_user_id: UUID, target_user_id: UUID, action: UserAction) -> UserActionResult:
        # Verify admin permissions for user management
        await self.verify_admin_permissions(admin_user_id, 'user_management')
        
        # Log admin action for audit trail
        await self.log_admin_action(admin_user_id, 'user_management', action)
        
        # Execute user management action
        result = await self.user_manager.execute_user_action(target_user_id, action)
        
        # Send notifications if required
        if action.requires_notification:
            await self.send_user_notification(target_user_id, action)
        
        return result
    
    async def get_ai_usage_analytics(self, admin_user_id: UUID, date_range: DateRange) -> AIUsageAnalytics:
        await self.verify_admin_permissions(admin_user_id, 'ai_analytics_view')
        
        # Aggregate AI usage data for the period
        usage_data = await self.analytics_service.get_ai_usage_analytics(date_range)
        
        # Calculate cost breakdowns and trends
        cost_analysis = await self.analytics_service.calculate_ai_cost_trends(usage_data)
        
        # Identify usage patterns and anomalies
        usage_patterns = await self.analytics_service.analyze_usage_patterns(usage_data)
        
        return AIUsageAnalytics(
            usage_summary=usage_data,
            cost_breakdown=cost_analysis,
            usage_patterns=usage_patterns,
            optimization_recommendations=await self.generate_cost_optimization_recommendations(cost_analysis)
        )
```

## API Endpoints
### Admin Dashboard Endpoints
```
GET /admin/dashboard
Headers: Authorization: Bearer <admin_token>
Response: {
  success: true,
  data: {
    system_health: {
      overall_status: "healthy",
      database: {
        status: "healthy",
        connections: 45,
        avg_query_time: 23.5,
        slow_queries: 2
      },
      apis: {
        status: "healthy",
        requests_per_minute: 1250,
        error_rate: 0.12,
        avg_response_time: 145
      },
      external_services: {
        gemini_api: "healthy",
        jsearch_api: "healthy", 
        cloudflare_r2: "healthy"
      }
    },
    user_metrics: {
      total_users: 15847,
      daily_active: 2341,
      weekly_active: 8925,
      monthly_active: 12456,
      new_registrations_today: 45,
      churn_rate: 2.3
    },
    ai_usage: {
      total_requests_today: 8934,
      total_cost_today: 245.67,
      average_cost_per_user: 0.105,
      most_used_feature: "resume_parsing",
      cost_trend: "stable"
    },
    recent_incidents: [
      {
        id: "uuid",
        title: "Temporary Gemini API slowdown",
        severity: "medium",
        status: "resolved",
        detected_at: "2024-01-15T09:30:00Z",
        resolved_at: "2024-01-15T09:45:00Z"
      }
    ],
    kpis: {
      platform_uptime: 99.97,
      user_satisfaction: 4.7,
      feature_adoption_rate: 78.5,
      support_response_time: 2.3 // hours
    }
  }
}

GET /admin/users
Headers: Authorization: Bearer <admin_token>
Query: ?page=1&limit=50&status=active&sort=created_at_desc&search=john@example.com
Response: {
  success: true,
  data: {
    users: [
      {
        user_id: "uuid",
        email: "john@example.com",
        full_name: "John Smith",
        status: "active",
        role: "candidate",
        created_at: "2024-01-15T10:30:00Z",
        last_login: "2024-01-20T14:22:00Z",
        engagement_level: "high",
        total_ai_usage_cost: 15.67,
        profile_completeness: 87.5,
        subscription_tier: "free"
      }
    ],
    pagination: {
      total: 15847,
      page: 1,
      per_page: 50,
      total_pages: 317
    },
    summary_stats: {
      active_users: 14532,
      premium_users: 1205,
      high_engagement: 8934,
      support_tickets_open: 23
    }
  }
}

POST /admin/users/{user_id}/actions
Headers: Authorization: Bearer <admin_token>
Body: {
  action: "suspend|activate|upgrade|downgrade|reset_password|export_data",
  reason: "Violation of terms of service",
  duration_days?: 30,
  notify_user: true,
  additional_notes?: "User reported for spam behavior"
}
Response: {
  success: true,
  data: {
    action_id: "uuid",
    user_id: "uuid",
    action_taken: "suspend",
    effective_immediately: true,
    notification_sent: true,
    admin_notes: "Account suspended for 30 days due to ToS violation"
  }
}

GET /admin/ai-analytics
Headers: Authorization: Bearer <admin_token>
Query: ?start_date=2024-01-01&end_date=2024-01-31&group_by=feature&include_costs=true
Response: {
  success: true,
  data: {
    period_summary: {
      total_requests: 234567,
      total_cost: 5432.10,
      average_cost_per_request: 0.0232,
      unique_users: 12456,
      cost_per_user: 0.436
    },
    feature_breakdown: [
      {
        feature: "resume_parsing",
        requests: 89234,
        cost: 2156.78,
        success_rate: 97.8,
        avg_response_time: 4.2,
        cost_trend: "decreasing"
      },
      {
        feature: "job_matching",
        requests: 67890,
        cost: 1543.21,
        success_rate: 95.4,
        avg_response_time: 3.8,
        cost_trend: "stable"
      }
    ],
    usage_patterns: {
      peak_hours: ["09:00", "13:00", "19:00"],
      peak_days: ["Monday", "Tuesday", "Wednesday"],
      seasonal_trends: "20% increase during Q1 job search season"
    },
    cost_optimization: {
      potential_savings: 456.78,
      recommendations: [
        "Implement more aggressive caching for job matching",
        "Optimize resume parsing prompts to reduce token usage",
        "Consider batch processing for bulk operations"
      ]
    }
  }
}

GET /admin/incidents
Headers: Authorization: Bearer <admin_token>
Query: ?status=open&severity=high&limit=20
Response: {
  success: true,
  data: {
    incidents: [
      {
        incident_id: "uuid",
        title: "High AI API error rate",
        severity: "high",
        status: "investigating",
        detected_at: "2024-01-20T08:15:00Z",
        affected_users: 234,
        impact_assessment: "Resume parsing failing for 15% of users",
        assigned_to: "ops-team@company.com",
        updates_count: 3,
        estimated_resolution: "2024-01-20T12:00:00Z"
      }
    ],
    incident_stats: {
      total_open: 3,
      critical_count: 1,
      average_resolution_time: 2.4, // hours
      incidents_this_month: 12,
      uptime_impact: 0.03 // percentage
    }
  }
}

POST /admin/system/alerts
Headers: Authorization: Bearer <admin_token>
Body: {
  alert_type: "performance|security|cost|user_activity",
  threshold_config: {
    metric: "ai_cost_per_hour",
    threshold_value: 100.00,
    comparison: "greater_than",
    duration_minutes: 15
  },
  notification_channels: ["email", "slack"],
  is_active: true
}
Response: {
  success: true,
  data: {
    alert_id: "uuid",
    alert_name: "High AI Cost Alert",
    status: "active",
    next_check: "2024-01-20T09:30:00Z",
    created_by: "admin@company.com"
  }
}
```

## Frontend Tasks & Business Rules
### Admin Interface Components
```tsx
const AdminDashboard: React.FC = () => {
  // System health overview with status indicators
  // Key metrics cards with trend indicators
  // Real-time alerts and notifications panel
  // Quick action buttons for common admin tasks
};

const UserManagementTable: React.FC<{
  users: User[];
  onUserAction: (userId: string, action: UserAction) => void;
}> = ({ users, onUserAction }) => {
  // Sortable, filterable user table
  // Bulk action capabilities
  // User detail modals with full history
  // Action confirmation dialogs
};

const AIUsageAnalytics: React.FC<{
  analytics: AIAnalytics;
}> = ({ analytics }) => {
  // Cost breakdown charts and trends
  // Feature usage comparison graphs
  // Optimization recommendations
  // Budget tracking and forecasting
};
```

### Security & Access Control Rules
- Admin access requires multi-factor authentication
- All admin actions logged with full audit trail
- Role-based permissions with principle of least privilege
- Admin sessions expire after 4 hours of inactivity
- Sensitive operations require additional confirmation

### Performance & Monitoring Standards
- Dashboard must load within 2 seconds for admin interfaces
- Real-time metrics updated every 30 seconds
- Alert notifications delivered within 60 seconds of threshold breach
- Admin action confirmations processed within 3 seconds
- System health checks run every 60 seconds with 99.9% accuracy

### Acceptance Criteria
- [ ] Comprehensive user management with role-based permissions
- [ ] Real-time system monitoring with proactive alerting
- [ ] AI cost tracking with optimization recommendations
- [ ] Incident management with resolution tracking
- [ ] Business analytics with trend analysis and forecasting
- [ ] Audit logging for all administrative actions
- [ ] Export capabilities for compliance and reporting

## Dependencies
### Depends On
- **All Previous Features**: Admin dashboard monitors and manages all platform functionality
- **Feature 1**: Authentication (admin role management and permissions)
- **Feature 0.1**: Project Infrastructure (system monitoring and logging)

### Produces
- Platform operational oversight and management capabilities
- User lifecycle management and support tools
- AI cost optimization and resource management
- Business intelligence and growth analytics
- Incident response and system reliability tools

## Notes
### Development Priorities
1. Core admin dashboard with system health monitoring
2. User management interface with comprehensive controls
3. AI usage analytics and cost tracking system
4. Incident management and alerting system
5. Business analytics and reporting capabilities
6. Advanced automation and optimization tools

### Security Considerations
- Implement comprehensive audit logging for all admin actions
- Use secure authentication with MFA requirements
- Apply principle of least privilege for admin permissions
- Regular security reviews and penetration testing
- Encrypt sensitive administrative data and communications

### Scalability Planning
- Design monitoring systems to handle high-volume platforms
- Implement efficient data aggregation for large user bases
- Plan for distributed admin capabilities across time zones
- Consider automated incident response and self-healing systems