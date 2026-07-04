"""add job discovery and matching tables (Phase 3)

Revision ID: a1b2c3d4e5f6
Revises: 2293bfea655b
Create Date: 2026-07-03 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '2293bfea655b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # --- jobs -----------------------------------------------------------------
    op.create_table(
        'jobs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('external_job_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('company_logo_url', sa.String(length=500), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('job_type', sa.String(length=100), nullable=True),
        sa.Column('employment_type', sa.String(length=100), nullable=True),
        sa.Column('experience_level', sa.String(length=100), nullable=True),
        sa.Column('salary_min', sa.Integer(), nullable=True),
        sa.Column('salary_max', sa.Integer(), nullable=True),
        sa.Column('salary_currency', sa.String(length=10), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('benefits', sa.Text(), nullable=True),
        sa.Column('skills_required', sa.JSON(), nullable=True),
        sa.Column('industry', sa.String(length=255), nullable=True),
        sa.Column('posted_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('application_deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('application_url', sa.String(length=500), nullable=True),
        sa.Column('source_platform', sa.String(length=100), nullable=True),
        sa.Column('cached_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_job_id', name='uq_jobs_external_job_id'),
    )
    op.create_index('idx_jobs_external_id', 'jobs', ['external_job_id'], unique=False)
    op.create_index('idx_jobs_location', 'jobs', ['location'], unique=False)
    op.create_index('idx_jobs_company', 'jobs', ['company_name'], unique=False)
    op.create_index('idx_jobs_posted_date', 'jobs', [sa.text('posted_date DESC')], unique=False)
    op.create_index('idx_jobs_salary', 'jobs', ['salary_min', 'salary_max'], unique=False)
    op.create_index('idx_jobs_expires_at', 'jobs', ['expires_at'], unique=False)

    # Full-text search: tsvector column, GIN index and an auto-update trigger.
    op.execute("ALTER TABLE jobs ADD COLUMN search_vector tsvector")
    op.execute(
        """
        UPDATE jobs SET search_vector =
            setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
            setweight(to_tsvector('english', coalesce(company_name, '')), 'B') ||
            setweight(to_tsvector('english', coalesce(description, '')), 'C')
        """
    )
    op.execute("CREATE INDEX idx_jobs_search_vector ON jobs USING gin(search_vector)")
    op.execute(
        """
        CREATE OR REPLACE FUNCTION jobs_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(NEW.company_name, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(NEW.description, '')), 'C');
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_jobs_search_vector
        BEFORE INSERT OR UPDATE OF title, company_name, description ON jobs
        FOR EACH ROW EXECUTE FUNCTION jobs_search_vector_update();
        """
    )

    # --- user_job_interactions ------------------------------------------------
    op.create_table(
        'user_job_interactions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('job_id', sa.Uuid(), nullable=False),
        sa.Column('interaction_type', sa.String(length=50), nullable=False),
        sa.Column('interaction_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'job_id', 'interaction_type', name='uq_user_job_interaction'),
    )
    op.create_index('ix_user_job_interactions_user_id', 'user_job_interactions', ['user_id'], unique=False)
    op.create_index('ix_user_job_interactions_job_id', 'user_job_interactions', ['job_id'], unique=False)
    op.create_index('idx_user_interactions_user_job', 'user_job_interactions', ['user_id', 'job_id'], unique=False)

    # --- saved_searches -------------------------------------------------------
    op.create_table(
        'saved_searches',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('search_criteria', sa.JSON(), nullable=False),
        sa.Column('alert_frequency', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_run', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_saved_searches_user_id', 'saved_searches', ['user_id'], unique=False)
    op.create_index('idx_saved_searches_user_active', 'saved_searches', ['user_id', 'is_active'], unique=False)

    # --- job_recommendations --------------------------------------------------
    op.create_table(
        'job_recommendations',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('job_id', sa.Uuid(), nullable=False),
        sa.Column('recommendation_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('recommendation_reason', sa.Text(), nullable=True),
        sa.Column('algorithm_version', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_job_recommendations_user_id', 'job_recommendations', ['user_id'], unique=False)
    op.create_index('ix_job_recommendations_job_id', 'job_recommendations', ['job_id'], unique=False)

    # --- job_matches ----------------------------------------------------------
    op.create_table(
        'job_matches',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('job_id', sa.Uuid(), nullable=False),
        sa.Column('candidate_profile_id', sa.Uuid(), nullable=True),
        sa.Column('overall_match_score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('skills_match_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('experience_match_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('education_match_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('location_match_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('match_explanation', sa.Text(), nullable=True),
        sa.Column('strengths', sa.JSON(), nullable=True),
        sa.Column('weaknesses', sa.JSON(), nullable=True),
        sa.Column('missing_skills', sa.JSON(), nullable=True),
        sa.Column('skill_gaps', sa.JSON(), nullable=True),
        sa.Column('improvement_suggestions', sa.JSON(), nullable=True),
        sa.Column('recommendation', sa.JSON(), nullable=True),
        sa.Column('gemini_model_version', sa.String(length=50), nullable=True),
        sa.Column('matching_algorithm_version', sa.String(length=20), nullable=True),
        sa.Column('processing_duration', sa.Integer(), nullable=True),
        sa.Column('confidence_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('needs_review', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['candidate_profile_id'], ['candidate_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'job_id', name='uq_job_match_user_job'),
    )
    op.create_index('idx_job_matches_user_id', 'job_matches', ['user_id'], unique=False)
    op.create_index('idx_job_matches_job_id', 'job_matches', ['job_id'], unique=False)
    op.create_index('idx_job_matches_score', 'job_matches', [sa.text('overall_match_score DESC')], unique=False)
    op.create_index('idx_job_matches_created_at', 'job_matches', [sa.text('created_at DESC')], unique=False)

    # --- skills_matches -------------------------------------------------------
    op.create_table(
        'skills_matches',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('job_match_id', sa.Uuid(), nullable=False),
        sa.Column('skill_name', sa.String(length=255), nullable=False),
        sa.Column('skill_category', sa.String(length=100), nullable=True),
        sa.Column('required_proficiency', sa.String(length=50), nullable=True),
        sa.Column('candidate_proficiency', sa.String(length=50), nullable=True),
        sa.Column('match_type', sa.String(length=50), nullable=True),
        sa.Column('match_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('importance_weight', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['job_match_id'], ['job_matches.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_skills_matches_job_match', 'skills_matches', ['job_match_id'], unique=False)

    # --- match_quality_feedback ----------------------------------------------
    op.create_table(
        'match_quality_feedback',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('job_match_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('feedback_type', sa.String(length=50), nullable=True),
        sa.Column('user_rating', sa.Integer(), nullable=True),
        sa.Column('feedback_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('user_rating >= 1 AND user_rating <= 5', name='ck_match_feedback_rating'),
        sa.ForeignKeyConstraint(['job_match_id'], ['job_matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_match_quality_feedback_job_match_id', 'match_quality_feedback', ['job_match_id'], unique=False)
    op.create_index('ix_match_quality_feedback_user_id', 'match_quality_feedback', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_match_quality_feedback_user_id', table_name='match_quality_feedback')
    op.drop_index('ix_match_quality_feedback_job_match_id', table_name='match_quality_feedback')
    op.drop_table('match_quality_feedback')

    op.drop_index('idx_skills_matches_job_match', table_name='skills_matches')
    op.drop_table('skills_matches')

    op.drop_index('idx_job_matches_created_at', table_name='job_matches')
    op.drop_index('idx_job_matches_score', table_name='job_matches')
    op.drop_index('idx_job_matches_job_id', table_name='job_matches')
    op.drop_index('idx_job_matches_user_id', table_name='job_matches')
    op.drop_table('job_matches')

    op.drop_index('ix_job_recommendations_job_id', table_name='job_recommendations')
    op.drop_index('ix_job_recommendations_user_id', table_name='job_recommendations')
    op.drop_table('job_recommendations')

    op.drop_index('idx_saved_searches_user_active', table_name='saved_searches')
    op.drop_index('ix_saved_searches_user_id', table_name='saved_searches')
    op.drop_table('saved_searches')

    op.drop_index('idx_user_interactions_user_job', table_name='user_job_interactions')
    op.drop_index('ix_user_job_interactions_job_id', table_name='user_job_interactions')
    op.drop_index('ix_user_job_interactions_user_id', table_name='user_job_interactions')
    op.drop_table('user_job_interactions')

    op.execute("DROP TRIGGER IF EXISTS trg_jobs_search_vector ON jobs")
    op.execute("DROP FUNCTION IF EXISTS jobs_search_vector_update()")
    op.drop_index('idx_jobs_search_vector', table_name='jobs')
    op.drop_index('idx_jobs_expires_at', table_name='jobs')
    op.drop_index('idx_jobs_salary', table_name='jobs')
    op.drop_index('idx_jobs_posted_date', table_name='jobs')
    op.drop_index('idx_jobs_company', table_name='jobs')
    op.drop_index('idx_jobs_location', table_name='jobs')
    op.drop_index('idx_jobs_external_id', table_name='jobs')
    op.drop_table('jobs')
