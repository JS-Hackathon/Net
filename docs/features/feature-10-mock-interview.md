# Feature 10: Mock Interview

## Overview
Implement comprehensive AI-powered mock interview system that generates role-specific questions, evaluates candidate responses in real-time, provides detailed feedback and coaching, and tracks interview performance over time to build confidence and improve success rates.

## Goal
Provide candidates with realistic interview practice that simulates actual hiring processes, delivers actionable feedback for improvement, and builds confidence through repeated practice with progressively challenging scenarios.

## User Story
As a **Candidate**,
I want to practice interviews with AI for specific roles
So that I can improve my interview skills and increase my chances of success in real interviews.

As a **Candidate**,
I want detailed feedback on my interview performance
So that I can identify areas for improvement and track my progress over time.

## Functional Requirements
### Interview Session Management
- Create and manage interview sessions for specific roles and companies
- Generate contextual questions based on job descriptions and candidate profiles
- Support different interview types (behavioral, technical, case study, cultural fit)
- Provide realistic interview environment with proper timing and pacing
- Enable pause, resume, and restart functionality for flexible practice
- Track multiple interview attempts and performance trends

### AI Question Generation & Evaluation
- Generate relevant questions using Gemini AI based on role requirements
- Adapt question difficulty based on candidate experience level
- Evaluate answers for content quality, structure, and completeness
- Provide real-time feedback on communication effectiveness
- Score responses across multiple criteria (relevance, depth, examples, clarity)
- Generate follow-up questions based on initial responses

### Performance Analytics & Coaching
- Comprehensive post-interview analysis with strengths and improvement areas
- Detailed feedback on individual responses with specific recommendations
- Performance tracking across multiple sessions to show improvement
- Personalized coaching tips based on common weaknesses
- Benchmark performance against role-specific success criteria
- Integration with career goals and skill development recommendations

## Non-functional Requirements
- Question generation time: <3 seconds per question
- Answer evaluation time: <5 seconds per response with detailed feedback
- Session reliability: Support 60+ minute interview sessions without interruption
- Real-time responsiveness: Immediate feedback and smooth user experience
- Audio support: Future voice recording and analysis capabilities
- Mobile compatibility: Functional interview practice on mobile devices

## Backend Tasks
### Database Schema
```sql
-- Mock interview sessions
CREATE TABLE interview_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Session configuration
    session_name VARCHAR(255),
    interview_type VARCHAR(100), -- behavioral, technical, mixed, case_study
    target_role VARCHAR(255),
    target_company VARCHAR(255),
    job_description TEXT, -- Used for context in question generation
    difficulty_level VARCHAR(50), -- entry, mid, senior, executive
    
    -- Session settings
    planned_duration_minutes INTEGER DEFAULT 45,
    question_count_target INTEGER DEFAULT 8,
    include_followup_questions BOOLEAN DEFAULT TRUE,
    
    -- Session state
    status VARCHAR(50) DEFAULT 'not_started', -- not_started, in_progress, paused, completed, abandoned
    current_question_index INTEGER DEFAULT 0,
    
    -- Performance summary
    overall_score DECIMAL(5,2), -- 0-100 overall interview performance
    confidence_level VARCHAR(50), -- low, medium, high based on performance
    interview_readiness VARCHAR(50), -- needs_work, good, excellent
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_activity_at TIMESTAMP DEFAULT NOW(),
    
    -- Metadata
    ai_model_version VARCHAR(50),
    evaluation_algorithm_version VARCHAR(20)
);

-- Individual interview questions within sessions
CREATE TABLE interview_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES interview_sessions(id) ON DELETE CASCADE,
    
    -- Question details
    question_number INTEGER NOT NULL,
    question_type VARCHAR(100), -- behavioral, technical, situational, culture_fit, competency
    question_category VARCHAR(100), -- leadership, problem_solving, communication, technical_skills
    question_text TEXT NOT NULL,
    question_context TEXT, -- Why this question was chosen
    
    -- Question metadata
    difficulty_rating VARCHAR(50), -- easy, medium, hard, expert
    expected_answer_duration_seconds INTEGER DEFAULT 120,
    key_evaluation_criteria JSONB, -- What to look for in answers
    sample_good_answer TEXT, -- Example of strong response
    
    -- Question source
    generated_by VARCHAR(50) DEFAULT 'ai', -- ai, template, custom
    source_template_id UUID, -- If based on template
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Candidate responses to interview questions
CREATE TABLE interview_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID REFERENCES interview_questions(id) ON DELETE CASCADE,
    session_id UUID REFERENCES interview_sessions(id) ON DELETE CASCADE,
    
    -- Response content
    response_text TEXT NOT NULL,
    response_audio_url VARCHAR(500), -- Future: voice recording
    response_duration_seconds INTEGER,
    
    -- AI evaluation scores
    overall_score DECIMAL(5,2), -- 0-100 overall response quality
    content_relevance_score DECIMAL(5,2), -- How well it addresses question
    structure_clarity_score DECIMAL(5,2), -- Organization and flow
    depth_detail_score DECIMAL(5,2), -- Depth of examples and detail
    communication_score DECIMAL(5,2), -- Clarity and professionalism
    
    -- Detailed analysis
    ai_feedback TEXT, -- Comprehensive feedback from AI
    strengths JSONB, -- Array of response strengths
    improvement_areas JSONB, -- Specific areas to improve
    missing_elements JSONB, -- Key points not addressed
    
    -- Follow-up interactions
    has_followup_questions BOOLEAN DEFAULT FALSE,
    followup_questions JSONB, -- Generated follow-up questions
    
    -- Metadata
    evaluation_confidence DECIMAL(5,2), -- AI confidence in evaluation
    evaluation_duration_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW(),
    evaluated_at TIMESTAMP
);

-- Interview performance analytics and trends
CREATE TABLE interview_performance_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES interview_sessions(id) ON DELETE CASCADE,
    
    -- Performance metrics
    total_questions INTEGER,
    questions_answered INTEGER,
    average_response_score DECIMAL(5,2),
    strongest_category VARCHAR(100), -- Best performing question category
    weakest_category VARCHAR(100), -- Category needing improvement
    
    -- Communication metrics
    average_response_length_words INTEGER,
    response_coherence_score DECIMAL(5,2),
    professional_tone_score DECIMAL(5,2),
    confidence_indicators JSONB, -- Signs of confidence/nervousness
    
    -- Improvement tracking
    improvement_from_last_session DECIMAL(5,2), -- Score change
    consistent_strengths JSONB, -- Strengths shown across sessions
    persistent_weaknesses JSONB, -- Areas consistently needing work
    
    -- Recommendations
    immediate_focus_areas JSONB, -- Top 3 areas to work on next
    practice_recommendations JSONB, -- Specific practice suggestions
    skill_development_priorities JSONB, -- Related to learning roadmaps
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Interview coaching tips and recommendations
CREATE TABLE interview_coaching_tips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Tip context
    tip_category VARCHAR(100), -- question_answering, confidence, body_language, preparation
    tip_type VARCHAR(100), -- strength_reinforcement, weakness_improvement, general_advice
    
    -- Tip content
    tip_title VARCHAR(255),
    tip_description TEXT,
    actionable_advice TEXT,
    practice_exercises JSONB, -- Specific exercises to improve
    
    -- Personalization
    triggered_by_session_id UUID REFERENCES interview_sessions(id),
    relevance_score DECIMAL(5,2), -- How relevant this tip is for the user
    priority_level VARCHAR(50), -- high, medium, low
    
    -- Engagement tracking
    viewed BOOLEAN DEFAULT FALSE,
    marked_helpful BOOLEAN DEFAULT FALSE,
    dismissed BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '30 days')
);

-- Indexes for performance
CREATE INDEX idx_interview_sessions_user_id ON interview_sessions(user_id, status);
CREATE INDEX idx_interview_sessions_created_at ON interview_sessions(created_at DESC);
CREATE INDEX idx_interview_questions_session_id ON interview_questions(session_id, question_number);
CREATE INDEX idx_interview_responses_session_id ON interview_responses(session_id);
CREATE INDEX idx_interview_responses_question_id ON interview_responses(question_id);
CREATE INDEX idx_performance_analytics_user_id ON interview_performance_analytics(user_id);
CREATE INDEX idx_coaching_tips_user_relevance ON interview_coaching_tips(user_id, relevance_score DESC);
```

### Mock Interview Service
```python
class MockInterviewService:
    def __init__(self, gemini_client: GeminiClient, question_generator: QuestionGenerator):
        self.gemini_client = gemini_client
        self.question_generator = question_generator
        self.evaluator = ResponseEvaluator()
    
    async def start_interview_session(self, user_id: UUID, session_config: InterviewConfig) -> InterviewSession:
        # Get candidate profile for context
        profile = await self.get_candidate_profile(user_id)
        
        # Generate interview questions based on role and profile
        questions = await self.question_generator.generate_interview_questions(
            target_role=session_config.target_role,
            job_description=session_config.job_description,
            candidate_profile=profile,
            interview_type=session_config.interview_type,
            difficulty_level=session_config.difficulty_level,
            question_count=session_config.question_count_target
        )
        
        # Create interview session record
        session = await self.create_interview_session(user_id, session_config, questions)
        
        # Return first question to start the interview
        first_question = questions[0] if questions else None
        
        return InterviewSession(
            session_id=session.id,
            current_question=first_question,
            total_questions=len(questions),
            session_status='in_progress'
        )
    
    async def submit_response(self, session_id: UUID, question_id: UUID, response: InterviewResponse) -> ResponseEvaluation:
        # Validate session and question
        session = await self.get_interview_session(session_id)
        question = await self.get_interview_question(question_id)
        
        # Evaluate response with AI
        evaluation = await self.evaluator.evaluate_response(
            question=question,
            response=response,
            candidate_context=session.candidate_context
        )
        
        # Store response and evaluation
        response_record = await self.store_interview_response(
            question_id, response, evaluation
        )
        
        # Generate follow-up questions if needed
        followup_questions = await self.generate_followup_questions(
            question, response, evaluation
        )
        
        # Get next main question or complete session
        next_question = await self.get_next_question(session_id)
        
        return ResponseEvaluation(
            response_id=response_record.id,
            overall_score=evaluation.overall_score,
            detailed_feedback=evaluation.feedback,
            strengths=evaluation.strengths,
            improvements=evaluation.improvements,
            followup_questions=followup_questions,
            next_question=next_question,
            session_complete=next_question is None
        )
    
    async def complete_interview_session(self, session_id: UUID) -> InterviewSummary:
        # Calculate overall performance metrics
        session_analytics = await self.calculate_session_performance(session_id)
        
        # Generate comprehensive feedback and coaching recommendations
        coaching_feedback = await self.generate_coaching_feedback(session_id, session_analytics)
        
        # Update session status and store final analytics
        await self.finalize_interview_session(session_id, session_analytics)
        
        # Generate personalized coaching tips for future improvement
        coaching_tips = await self.generate_coaching_tips(session_id, session_analytics)
        
        return InterviewSummary(
            session_id=session_id,
            overall_performance=session_analytics,
            detailed_feedback=coaching_feedback,
            improvement_recommendations=coaching_tips,
            next_session_suggestions=await self.suggest_next_practice_areas(session_analytics)
        )

class InterviewQuestionGenerator:
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
        self.question_bank = QuestionBank()
    
    async def generate_interview_questions(self, target_role: str, job_description: str, candidate_profile: CandidateProfile, interview_type: str, difficulty_level: str, question_count: int) -> List[InterviewQuestion]:
        # Create question generation prompt with full context
        question_prompt = await self.create_question_generation_prompt(
            target_role, job_description, candidate_profile, interview_type, difficulty_level, question_count
        )
        
        # Generate questions using AI
        ai_response = await self.gemini_client.generate_interview_questions(question_prompt)
        
        # Process and validate generated questions
        questions = await self.process_generated_questions(ai_response, difficulty_level)
        
        # Ensure question diversity and appropriate difficulty progression
        optimized_questions = await self.optimize_question_sequence(questions)
        
        return optimized_questions

class InterviewResponseEvaluator:
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
        self.scoring_framework = ScoringFramework()
    
    async def evaluate_response(self, question: InterviewQuestion, response: InterviewResponse, candidate_context: CandidateContext) -> ResponseEvaluation:
        # Create evaluation prompt with question and response context
        evaluation_prompt = await self.create_evaluation_prompt(question, response, candidate_context)
        
        # Get AI evaluation
        ai_evaluation = await self.gemini_client.evaluate_interview_response(evaluation_prompt)
        
        # Process AI evaluation into structured format
        structured_evaluation = await self.process_evaluation_response(ai_evaluation)
        
        # Apply scoring framework and validation
        final_evaluation = await self.scoring_framework.validate_and_score(structured_evaluation)
        
        return final_evaluation
```

## AI Service Tasks
### Interview Question Generation Prompts
```python
INTERVIEW_QUESTION_GENERATION_PROMPT_V1 = {
    "version": "1.0",
    "system_prompt": """
You are an expert interviewer and talent acquisition specialist. Generate realistic, relevant interview questions that accurately assess candidates for specific roles while providing valuable practice opportunities.

Focus on:
- Role-specific competencies and requirements
- Appropriate difficulty for candidate's experience level
- Diverse question types (behavioral, situational, technical, cultural)
- Questions that allow candidates to showcase their strengths
- Realistic interview scenarios that hiring managers would use
    """,
    "user_prompt": """
Generate interview questions for this candidate and role:

TARGET ROLE: {target_role}
JOB DESCRIPTION: {job_description}
INTERVIEW TYPE: {interview_type}
DIFFICULTY LEVEL: {difficulty_level}
QUESTION COUNT: {question_count}

CANDIDATE PROFILE:
{candidate_profile}

Generate questions in this JSON format:
{
  "interview_overview": {
    "interview_focus": "Main areas this interview will assess",
    "difficulty_rationale": "Why this difficulty level is appropriate",
    "question_progression": "How questions build on each other"
  },
  "questions": [
    {
      "question_number": number,
      "question_type": "behavioral|situational|technical|competency|culture_fit",
      "question_category": "leadership|problem_solving|communication|technical_skills|teamwork|adaptability",
      "question_text": "The actual interview question",
      "question_rationale": "Why this question is relevant for the role",
      "difficulty_rating": "easy|medium|hard|expert",
      "expected_duration_minutes": number,
      "evaluation_criteria": [
        "What to look for in a strong answer",
        "Key elements that should be addressed"
      ],
      "follow_up_potential": "Possible follow-up questions based on response",
      "sample_strong_response_outline": "Framework for a good answer"
    }
  ],
  "interview_tips": {
    "preparation_advice": "How candidate should prepare for this type of interview",
    "common_pitfalls": "What candidates often struggle with",
    "success_strategies": "Approaches that lead to strong performance"
  }
}
    """
}

INTERVIEW_RESPONSE_EVALUATION_PROMPT_V1 = {
    "version": "1.0", 
    "system_prompt": """
You are an expert interviewer evaluating candidate responses. Provide constructive, detailed feedback that helps candidates improve while accurately assessing their performance against role requirements.

Focus on:
- Objective assessment of response quality and relevance
- Specific, actionable feedback for improvement
- Recognition of strengths and positive elements
- Professional, encouraging tone that builds confidence
- Realistic scoring that reflects actual interview standards
    """,
    "user_prompt": """
Evaluate this interview response:

QUESTION: {question_text}
QUESTION TYPE: {question_type}
EVALUATION CRITERIA: {evaluation_criteria}

CANDIDATE RESPONSE: {response_text}
RESPONSE DURATION: {response_duration}

CANDIDATE CONTEXT: {candidate_context}

Provide detailed evaluation in this JSON format:
{
  "overall_assessment": {
    "overall_score": number, // 0-100 overall response quality
    "performance_level": "excellent|good|adequate|needs_improvement|poor",
    "summary": "Brief overall assessment of the response"
  },
  "detailed_scoring": {
    "content_relevance": {
      "score": number, // 0-100 how well response addresses question
      "feedback": "Specific feedback on relevance and focus"
    },
    "structure_clarity": {
      "score": number, // 0-100 organization and logical flow
      "feedback": "Comments on response structure and clarity"
    },
    "depth_examples": {
      "score": number, // 0-100 depth of detail and use of examples
      "feedback": "Assessment of examples and supporting details"
    },
    "communication_style": {
      "score": number, // 0-100 professionalism and clarity
      "feedback": "Evaluation of communication effectiveness"
    }
  },
  "response_analysis": {
    "key_strengths": [
      "Specific strength demonstrated in response"
    ],
    "areas_for_improvement": [
      {
        "area": "Specific aspect to improve",
        "suggestion": "Concrete advice for improvement",
        "priority": "high|medium|low"
      }
    ],
    "missing_elements": [
      "Important points not addressed that should have been included"
    ],
    "notable_insights": [
      "Positive elements or insights the candidate provided"
    ]
  },
  "improvement_recommendations": {
    "immediate_tips": [
      "Quick adjustments for next similar question"
    ],
    "practice_suggestions": [
      "Specific ways to improve this type of response"
    ],
    "example_improvement": "How this response could be enhanced with specific changes"
  },
  "follow_up_assessment": {
    "needs_clarification": boolean,
    "suggested_follow_ups": [
      "Potential follow-up questions based on this response"
    ],
    "probing_opportunities": [
      "Areas where interviewer might dig deeper"
    ]
  }
}
    """
}
```

## API Endpoints
### Mock Interview Endpoints
```
POST /interviews/start
Headers: Authorization: Bearer <token>
Body: {
  session_name?: "Practice for Google PM Role",
  interview_type: "behavioral|technical|mixed|case_study",
  target_role: "Product Manager",
  target_company?: "Google",
  job_description?: "Full job description text...",
  difficulty_level?: "mid", // entry, mid, senior, executive
  planned_duration_minutes?: 45,
  question_count_target?: 8
}
Response: {
  success: true,
  data: {
    session_id: "uuid",
    session_name: "Practice for Google PM Role", 
    total_questions: 8,
    current_question: {
      question_id: "uuid",
      question_number: 1,
      question_type: "behavioral",
      question_text: "Tell me about a time you had to influence a team without having direct authority over them.",
      expected_duration_minutes: 3,
      evaluation_criteria: ["Leadership skills", "Influence tactics", "Specific examples"]
    },
    session_status: "in_progress"
  }
}

POST /interviews/{session_id}/respond
Headers: Authorization: Bearer <token>
Body: {
  question_id: "uuid",
  response_text: "In my previous role as a software engineer, I was asked to lead a cross-functional project...",
  response_duration_seconds?: 180
}
Response: {
  success: true,
  data: {
    response_id: "uuid",
    evaluation: {
      overall_score: 78.5,
      performance_level: "good",
      detailed_scores: {
        content_relevance: 85.0,
        structure_clarity: 75.0,
        depth_examples: 80.0,
        communication_style: 74.0
      },
      key_strengths: [
        "Provided specific, relevant example",
        "Clear problem-solution structure"
      ],
      improvement_areas: [
        {
          "area": "Quantify impact and results",
          "suggestion": "Include specific metrics or outcomes achieved",
          "priority": "medium"
        }
      ],
      immediate_feedback: "Strong example with good structure. Consider adding more specific results and metrics to strengthen your impact story."
    },
    next_question: {
      question_id: "uuid",
      question_number: 2,
      question_text: "How do you prioritize competing product features when resources are limited?"
    },
    session_progress: {
      questions_completed: 1,
      total_questions: 8,
      estimated_time_remaining: 21
    }
  }
}

POST /interviews/{session_id}/complete
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    session_summary: {
      overall_performance: {
        overall_score: 76.2,
        confidence_level: "medium",
        interview_readiness: "good",
        strongest_area: "problem_solving",
        improvement_focus: "communication_clarity"
      },
      question_breakdown: [
        {
          question_number: 1,
          score: 78.5,
          category: "behavioral",
          performance: "good"
        }
      ],
      key_insights: {
        consistent_strengths: ["Strong examples", "Good problem-solving approach"],
        areas_for_development: ["More concise communication", "Quantify achievements"],
        readiness_assessment: "Ready for most PM interviews with minor improvements"
      },
      recommendations: {
        immediate_focus: ["Practice quantifying impact", "Work on concise storytelling"],
        next_practice_session: "Technical PM questions",
        estimated_improvement_timeline: "2-3 practice sessions"
      }
    }
  }
}

GET /interviews/history
Headers: Authorization: Bearer <token>
Query: ?limit=10&interview_type=behavioral
Response: {
  success: true,
  data: {
    interviews: [
      {
        session_id: "uuid",
        session_name: "Practice for Google PM Role",
        interview_type: "behavioral",
        target_role: "Product Manager",
        overall_score: 76.2,
        questions_completed: 8,
        completed_at: "2024-01-15T14:30:00Z",
        improvement_from_last: +5.2
      }
    ],
    performance_trends: {
      average_score_last_5: 74.8,
      improvement_trend: "positive",
      strongest_categories: ["problem_solving", "leadership"],
      focus_areas: ["communication", "technical_depth"]
    }
  }
}
```

## Frontend Tasks & Business Rules
### Interview Interface Components
```tsx
const InterviewRoom: React.FC<{
  session: InterviewSession;
  onSubmitResponse: (response: string) => void;
}> = ({ session, onSubmitResponse }) => {
  // Clean, distraction-free interview environment
  // Question display with clear formatting
  // Response input area with timer
  // Progress indicator showing question number
  // Submit and next question flow
};

const ResponseFeedback: React.FC<{
  evaluation: ResponseEvaluation;
  onContinue: () => void;
}> = ({ evaluation, onContinue }) => {
  // Score visualization with breakdown
  // Strengths and improvement areas
  // Specific feedback and suggestions
  // Continue to next question button
};
```

### Performance Requirements & Acceptance Criteria
- [ ] Interview sessions support 60+ minutes without interruption
- [ ] Question generation completes within 3 seconds
- [ ] Response evaluation provides feedback within 5 seconds  
- [ ] Performance tracking shows improvement trends over multiple sessions
- [ ] Mobile interface allows full interview practice functionality

## Dependencies
### Depends On
- **Feature 4**: Candidate Profile (provides context for question generation and evaluation)
- **Feature 0.1**: Project Infrastructure (Gemini API integration)
- **Feature 0.2**: Design System (interview interface components)

### Used By
- **Feature 11**: Career Snapshot (preserves interview performance over time)
- **Feature 9**: Learning Roadmap (integrates interview feedback into learning plans)

### Produces
- Realistic interview practice with role-specific questions
- Detailed performance feedback and improvement recommendations
- Interview confidence building through repeated practice
- Performance analytics and progress tracking over time

## Notes
### Development Priorities
1. Core interview session management and question generation
2. AI response evaluation with detailed feedback
3. Performance tracking and analytics dashboard
4. Interview coaching and improvement recommendations
5. Advanced features (voice recording, video simulation)
6. Integration with learning roadmaps and career planning