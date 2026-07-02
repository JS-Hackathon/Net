# Project Context

## Project Overview

MockAI is an AI-powered Career Copilot that helps candidates improve their resumes and prepare for job applications using Large Language Models.

The platform allows users to:

- Upload resumes
- Parse resumes into structured candidate profiles
- Discover relevant jobs
- Compare resumes against job descriptions
- Identify skill gaps
- Recommend career paths
- Generate personalized learning roadmaps
- Conduct AI-powered mock interviews
- Track career progress over time

This project is developed as a Hackathon MVP.

---

# Primary Goal

Build an end-to-end AI recruitment assistant with a modern architecture.

The application should prioritize:

- clean architecture
- modularity
- AI workflow separation
- maintainability
- scalability
- production-ready code quality

---

# Tech Stack

Frontend

- Next.js (App Router)
- TypeScript
- TailwindCSS
- shadcn/ui
- React Hook Form
- TanStack Query
- Zustand

Backend

- FastAPI
- Python
- SQLAlchemy
- PostgreSQL
- Alembic
- JWT Authentication
- Google OAuth

Infrastructure

- Cloudflare
- Cloudflare R2 (resume storage)

External APIs

- Google Gemini API
- JSearch API

---

# Architecture

The system follows a layered architecture.

```
Presentation Layer

↓

Application Layer

↓

Domain Layer

↓

Infrastructure Layer
```

AI logic must never be placed inside controllers.

Controllers only:

- validate request
- call service
- return response

Business logic belongs to Services.

Database logic belongs to Repositories.

External APIs belong to dedicated Clients.

---

# Core Workflow

```
Authentication

↓

Upload Resume

↓

Extract Text

↓

Gemini Resume Parsing

↓

Candidate Profile

↓

Job Discovery

↓

AI Matching

↓

Skill Gap Analysis

↓

Career Recommendation

↓

Learning Roadmap

↓

Mock Interview

↓

Career Snapshot
```

Every AI feature depends on structured Candidate Profile.

---

# User Roles

Guest

- Register
- Login

Candidate

- Upload Resume
- View Analysis
- Search Jobs
- Match Jobs
- Skill Gap
- Roadmap
- Mock Interview
- Career Snapshot

Admin

- Manage Users
- View Statistics
- Monitor AI Usage

---

# Core Modules

Authentication

Resume

Candidate Profile

Analysis

Job Discovery

Matching

Skill Gap

Career Recommendation

Learning Roadmap

Interview

Career Snapshot

Admin

---

# AI Principles

Gemini should always return structured JSON.

Never parse natural language whenever structured output is possible.

Every prompt should have:

- version
- schema
- validation

AI output should be validated before persistence.

Retry Gemini requests when timeout occurs.

---

# Database Principles

Main entities

User

Resume

CandidateProfile

ResumeAnalysis

Job

JobMatch

SkillGap

CareerRecommendation

LearningRoadmap

Interview

CareerSnapshot

Relationships

```
User
 ├── Resume
 ├── CandidateProfile
 └── CareerSnapshot

CareerSnapshot
 ├── Analysis
 ├── Roadmap
 └── Interview
```

Career Snapshot is immutable.

Never update previous snapshots.

Always create a new snapshot.

---

# Backend Guidelines

Use dependency injection.

Use Repository Pattern.

Use Service Layer.

Never access database directly from controllers.

Use DTOs for request/response.

Return consistent API responses.

Use async whenever external APIs are involved.

---

# Frontend Guidelines

Pages should remain thin.

Business logic belongs to hooks.

API calls belong to services.

UI components should remain reusable.

Forms use:

- React Hook Form
- Zod validation

Server state uses TanStack Query.

Client state uses Zustand.

---

# File Upload

Supported

- PDF
- DOCX

Maximum size

5 MB

Store original file in Cloudflare R2.

Resume parsing always works from uploaded file.

---

# AI Features

Resume Parsing

Extract

- skills
- experience
- education
- projects
- certifications

AI Matching

Input

Resume JSON

+

Job JSON

Output

Match Score

Skill Gap

Priority

- Critical
- High
- Medium
- Low

Career Recommendation

Generate

- careers
- confidence
- reasoning

Learning Roadmap

Generate

- week
- topic
- priority
- resources

Mock Interview

Generate

- questions
- evaluation
- feedback
- summary

---

# Non-functional Requirements

Resume analysis

< 15 seconds

Interview evaluation

< 3 seconds

HTTPS only

JWT authentication

Stateless backend

REST APIs

JSON communication

Retry AI failures

Prompt versioning

Hallucination detection

---

# Coding Principles

Prefer composition over inheritance.

Prefer interfaces over concrete implementations.

Keep functions small.

Single Responsibility Principle.

Avoid duplicated logic.

Write self-documenting code.

Strong typing whenever possible.

Never hardcode prompts inside services.

Store prompts separately.

---

# Implementation Priority

Phase 1

Authentication

Phase 2

Resume Upload

Resume Parsing

Candidate Profile

Phase 3

Job Discovery

AI Matching

Phase 4

Skill Gap

Career Recommendation

Learning Roadmap

Phase 5

Mock Interview

Phase 6

Career Snapshot

Analysis History

Phase 7

Admin Dashboard

---

# Expected Coding Style

Every feature should contain:

- API
- Service
- Repository
- DTO
- Validation
- Tests (if applicable)

Every feature should be independently maintainable.

Avoid coupling between AI modules.

Always reuse Candidate Profile instead of re-parsing resumes.

Keep AI providers replaceable through abstraction.

Future AI providers (OpenAI, Claude, DeepSeek, etc.) should be swappable without changing business logic.


