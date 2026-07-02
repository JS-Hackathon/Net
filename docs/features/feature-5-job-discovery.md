# Feature 5: Job Discovery

## Overview
Implement job search and discovery system with JSearch API integration, advanced filtering capabilities, job bookmarking, and comprehensive job data management that provides users access to real-time job market data.

## Goal
Create a powerful job discovery platform that connects users with relevant job opportunities through intelligent search, filtering, and personalization while maintaining performance and data freshness.

## User Story
As a **Candidate**,
I want to search for relevant job opportunities
So that I can find positions that match my skills and career goals.

As a **Candidate**,
I want to filter jobs by location, salary, and company type
So that I can focus on opportunities that meet my specific requirements.

## Functional Requirements
### Job Search System
- Real-time job search using JSearch API integration
- Advanced filtering by location, salary range, experience level, company size
- Keyword search across job titles, descriptions, and company names
- Industry and role category filtering
- Remote work and hybrid job options filtering
- Job posting date and freshness filtering

### Job Management Features
- Job bookmarking and saved searches functionality
- Job application tracking and status management
- Job recommendation system based on user profile
- Job alert notifications for new matching positions
- Recently viewed jobs history
- Job comparison tools for multiple positions

### Job Data Display
- Comprehensive job detail pages with full descriptions
- Company information and culture insights
- Salary range and benefits information
- Required skills and qualifications breakdown
- Job posting source and application instructions
- Similar jobs and company other openings

## Non-functional Requirements
- Job search response time: <3 seconds for typical queries
- JSearch API rate limiting: Respect quotas and implement caching
- Data freshness: Cache job data for 4 hours, then refresh
- Search performance: Support pagination for large result sets
- Concurrent users: Handle multiple simultaneous search requests
- Mobile optimization: Full functionality on mobile devices

## Backend Tasks
### Database Schema
```sql
-- Job data cache from JSearch API
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_job_id VARCHAR(255) UNIQUE NOT NULL, -- JSearch API job ID
    title VARCHAR(500) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_logo_url VARCHAR(500),
    location VARCHAR(255),
    job_type VARCHAR(100), -- full-time, part-time, contract, internship
    employment_type VARCHAR(100), -- remote, hybrid, on-site
    experience_level VARCHAR(100), -- entry, mid, senior, executive
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(10) DEFAULT 'USD',
    description TEXT,
    requirements TEXT,
    benefits TEXT,
    skills_required JSONB, -- Array of required skills
    industry VARCHAR(255),
    posted_date TIMESTAMP,
    application_deadline TIMESTAMP,
    application_url VARCHAR(500),
    source_platform VARCHAR(100), -- Indeed, LinkedIn, etc.
    
    -- Cache metadata
    cached_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '4 hours'),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Search optimization
    search_vector tsvector, -- Full-text search
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User job interactions
CREATE TABLE user_job_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL, -- viewed, bookmarked, applied, rejected
    interaction_data JSONB, -- Additional interaction metadata
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, job_id, interaction_type)
);

-- Saved searches for job alerts
CREATE TABLE saved_searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    search_criteria JSONB NOT NULL, -- Search parameters
    alert_frequency VARCHAR(50) DEFAULT 'daily', -- daily, weekly, immediate
    is_active BOOLEAN DEFAULT TRUE,
    last_run TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Job recommendations cache
CREATE TABLE job_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    recommendation_score DECIMAL(5,2), -- 0-100
    recommendation_reason TEXT,
    algorithm_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_jobs_external_id ON jobs(external_job_id);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_jobs_company ON jobs(company_name);
CREATE INDEX idx_jobs_posted_date ON jobs(posted_date DESC);
CREATE INDEX idx_jobs_salary ON jobs(salary_min, salary_max);
CREATE INDEX idx_jobs_search_vector ON jobs USING gin(search_vector);
CREATE INDEX idx_user_interactions_user_job ON user_job_interactions(user_id, job_id);
CREATE INDEX idx_saved_searches_user_active ON saved_searches(user_id, is_active);
```

### JSearch API Service
```python
class JSearchService:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = aiohttp.ClientSession()
        self.rate_limiter = RateLimiter(requests_per_minute=60)
    
    async def search_jobs(self, search_params: JobSearchParams) -> JobSearchResponse:
        await self.rate_limiter.acquire()
        
        # Build JSearch API request
        request_params = {
            'query': search_params.query,
            'page': search_params.page,
            'num_pages': search_params.per_page,
            'date_posted': search_params.date_posted,
            'remote_jobs_only': search_params.remote_only,
            'employment_types': search_params.employment_types,
            'job_requirements': search_params.experience_level,
            'company_types': search_params.company_types
        }
        
        try:
            response = await self.session.get(
                f"{self.base_url}/search",
                headers={'X-RapidAPI-Key': self.api_key},
                params=request_params,
                timeout=10
            )
            
            data = await response.json()
            return self.transform_jsearch_response(data)
            
        except Exception as e:
            raise JSearchAPIException(f"JSearch API error: {str(e)}")
    
    def transform_jsearch_response(self, jsearch_data: Dict) -> JobSearchResponse:
        # Transform JSearch response to internal format
        # Normalize salary information
        # Extract and categorize skills
        # Format location data
        # Return standardized job objects
```

### Job Discovery Service
```python
class JobDiscoveryService:
    def __init__(self, jsearch_client: JSearchService, cache_service: CacheService):
        self.jsearch_client = jsearch_client
        self.cache_service = cache_service
        self.db = Database()
    
    async def search_jobs(self, user_id: UUID, search_params: JobSearchParams) -> JobSearchResult:
        # Check cache for recent identical searches
        cached_results = await self.get_cached_search(search_params)
        if cached_results and not self.is_cache_expired(cached_results):
            return cached_results
        
        # Fetch from JSearch API
        jsearch_results = await self.jsearch_client.search_jobs(search_params)
        
        # Store/update job data in database
        jobs = await self.upsert_jobs(jsearch_results.jobs)
        
        # Log user search for analytics
        await self.log_user_search(user_id, search_params)
        
        # Cache results for performance
        await self.cache_search_results(search_params, jobs)
        
        return JobSearchResult(jobs=jobs, total=jsearch_results.total, page=search_params.page)
    
    async def get_job_details(self, job_id: UUID, user_id: UUID) -> JobDetail:
        # Retrieve job from cache/database
        # Log job view interaction
        # Fetch additional details if needed
        # Return comprehensive job information
        
    async def bookmark_job(self, user_id: UUID, job_id: UUID) -> bool:
        # Create bookmark interaction
        # Update user preferences based on bookmark
        # Return success status
        
    async def get_user_bookmarks(self, user_id: UUID) -> List[Job]:
        # Retrieve user's bookmarked jobs
        # Include job details and current status
        # Sort by bookmark date
```

## API Endpoints
### Job Search Endpoints
```
GET /jobs/search
Headers: Authorization: Bearer <token>
Query: ?q=software engineer&location=San Francisco&salary_min=80000&remote=true&page=1
Response: {
  success: true,
  data: {
    jobs: [
      {
        id: "uuid",
        external_id: "jsearch_12345",
        title: "Senior Software Engineer",
        company: "Tech Corp",
        location: "San Francisco, CA",
        employment_type: "remote",
        salary_range: "$100K - $150K",
        posted_date: "2024-01-01T00:00:00Z",
        skills_required: ["Python", "React", "AWS"],
        is_bookmarked: false
      }
    ],
    pagination: {
      page: 1,
      per_page: 20,
      total: 150,
      total_pages: 8
    }
  }
}

GET /jobs/{job_id}
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    id: "uuid",
    title: "Senior Software Engineer",
    company: {
      name: "Tech Corp",
      logo_url: "https://...",
      size: "1000-5000",
      industry: "Technology"
    },
    description: "Full job description...",
    requirements: "Required qualifications...",
    benefits: "Benefits and perks...",
    salary_range: "$100K - $150K",
    location: "San Francisco, CA",
    employment_type: "remote",
    application_url: "https://...",
    posted_date: "2024-01-01T00:00:00Z",
    skills_required: ["Python", "React", "AWS"],
    is_bookmarked: true,
    view_count: 1
  }
}

POST /jobs/{job_id}/bookmark
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    message: "Job bookmarked successfully",
    is_bookmarked: true
  }
}

DELETE /jobs/{job_id}/bookmark
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    message: "Bookmark removed successfully",
    is_bookmarked: false
  }
}

GET /jobs/bookmarks
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    bookmarks: [
      {
        job: { /* job details */ },
        bookmarked_at: "2024-01-01T00:00:00Z"
      }
    ],
    total: 5
  }
}
```

## Frontend Tasks
### Job Search Interface
```tsx
interface JobSearchProps {
  onJobSelect: (job: Job) => void;
  initialFilters?: JobSearchFilters;
}

const JobSearchPage: React.FC<JobSearchProps> = ({ onJobSelect, initialFilters }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<JobSearchFilters>(initialFilters || {});
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Search functionality with debouncing
  // Filter management and persistence
  // Pagination handling
  // Loading and error states
};

const JobSearchFilters: React.FC<{
  filters: JobSearchFilters;
  onChange: (filters: JobSearchFilters) => void;
}> = ({ filters, onChange }) => {
  // Location filter with autocomplete
  // Salary range sliders
  // Experience level selection
  // Employment type checkboxes
  // Company size and industry filters
  // Remote/hybrid/on-site options
};

const JobCard: React.FC<{
  job: Job;
  onBookmark: (jobId: string) => void;
  onClick: (job: Job) => void;
}> = ({ job, onBookmark, onClick }) => {
  // Job title and company display
  // Location and salary information
  // Skills tags display
  // Bookmark button with state
  // Posted date and freshness indicator
};
```

### Job Management Components
```tsx
const JobDetail: React.FC<{
  job: JobDetail;
  onBookmark: () => void;
  onApply: () => void;
}> = ({ job, onBookmark, onApply }) => {
  // Full job description and requirements
  // Company information section
  // Skills matching indicator
  // Apply and bookmark actions
  // Similar jobs recommendations
};

const BookmarkedJobs: React.FC = () => {
  // List of user's bookmarked jobs
  // Sorting and filtering options
  // Bulk actions (remove, apply)
  // Job status tracking
};
```

## Business Rules
### Job Data Management
- Job data cached for 4 hours before refresh from JSearch API
- Expired job postings automatically marked inactive
- User interactions logged for recommendation improvements
- Duplicate jobs from different sources merged intelligently
- Job skills extracted and normalized for matching algorithms

### Search and Filtering Rules
- Search results limited to 1000 jobs per query for performance
- Location searches support city, state, country, and "remote" keywords
- Salary filters work with annual, hourly, and contract rates
- Experience level mapping: Entry (0-2 years), Mid (3-5 years), Senior (6+ years)
- Only active job postings shown in search results

## Acceptance Criteria
### Job Search Functionality
- [ ] Job search returns relevant results within 3 seconds
- [ ] Advanced filtering works across all job attributes
- [ ] Search results properly paginated with smooth navigation
- [ ] Job bookmarking persists across sessions
- [ ] Mobile interface fully functional for job browsing

### Data Quality and Performance
- [ ] Job data stays fresh with 4-hour cache refresh
- [ ] JSearch API rate limits respected with proper error handling
- [ ] Duplicate job detection and merging works accurately
- [ ] Search performance remains fast with large datasets
- [ ] Error states handled gracefully with user-friendly messages

## Dependencies
### Depends On
- **Feature 1**: Authentication (user context for bookmarks and preferences)
- **Feature 0.1**: Project Infrastructure (JSearch API client setup)
- **Feature 0.2**: Design System (search and filter components)

### Used By
- **Feature 6**: AI Matching (uses job data for matching algorithms)
- **Feature 7**: Skill Gap Analysis (compares user skills with job requirements)
- **Feature 8**: Career Recommendations (analyzes job market trends)

### Produces
- Real-time job market data for matching and analysis
- User job interaction data for recommendations
- Job search and filtering capabilities
- Job bookmarking and tracking system

## Notes
### Development Priorities
1. Core job search with JSearch API integration
2. Advanced filtering and search interface
3. Job bookmarking and user interactions
4. Performance optimization with caching
5. Mobile responsiveness and accessibility
6. Job recommendation system (future enhancement)