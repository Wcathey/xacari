-- Xacari Database Schema for Supabase
-- Run this SQL in your Supabase SQL Editor
-- NOTE: RLS is auto-enabled by your Supabase project trigger

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- USERS TABLE (extends auth.users)
-- =====================================================
CREATE TABLE public.profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- User preferences
    preferred_language TEXT DEFAULT 'en',
    units_system TEXT DEFAULT 'metric', -- metric or imperial
    voice_enabled BOOLEAN DEFAULT TRUE,
    notifications_enabled BOOLEAN DEFAULT TRUE,
    -- Statistics
    total_workouts INTEGER DEFAULT 0,
    total_workout_duration_seconds INTEGER DEFAULT 0,
    streak_days INTEGER DEFAULT 0,
    last_workout_date DATE
);

-- RLS Policies for profiles
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- Trigger to create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- =====================================================
-- WORKOUT SESSIONS TABLE
-- =====================================================
CREATE TABLE public.workout_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    workout_type TEXT NOT NULL, -- strength, cardio, flexibility, balance, custom
    status TEXT NOT NULL DEFAULT 'pending', -- pending, active, paused, completed, cancelled
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    total_duration_seconds FLOAT DEFAULT 0,
    pause_count INTEGER DEFAULT 0,
    current_exercise_index INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policies for workout_sessions
CREATE POLICY "Users can view own workout sessions"
    ON public.workout_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own workout sessions"
    ON public.workout_sessions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own workout sessions"
    ON public.workout_sessions FOR UPDATE
    USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX idx_workout_sessions_user_id ON public.workout_sessions(user_id);
CREATE INDEX idx_workout_sessions_status ON public.workout_sessions(status);
CREATE INDEX idx_workout_sessions_created_at ON public.workout_sessions(created_at);

-- =====================================================
-- EXERCISES TABLE
-- =====================================================
CREATE TABLE public.exercises (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES public.workout_sessions(id) ON DELETE CASCADE NOT NULL,
    exercise_type TEXT NOT NULL, -- squat, pushup, plank, etc.
    exercise_order INTEGER NOT NULL,
    reps_completed INTEGER DEFAULT 0,
    reps_target INTEGER,
    duration_seconds FLOAT DEFAULT 0,
    form_score FLOAT DEFAULT 0 CHECK (form_score >= 0 AND form_score <= 100),
    corrections_given TEXT[] DEFAULT ARRAY[]::TEXT[],
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policies for exercises
CREATE POLICY "Users can view own exercises"
    ON public.exercises FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.workout_sessions
            WHERE workout_sessions.id = exercises.session_id
            AND workout_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own exercises"
    ON public.exercises FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workout_sessions
            WHERE workout_sessions.id = exercises.session_id
            AND workout_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own exercises"
    ON public.exercises FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.workout_sessions
            WHERE workout_sessions.id = exercises.session_id
            AND workout_sessions.user_id = auth.uid()
        )
    );

-- Indexes
CREATE INDEX idx_exercises_session_id ON public.exercises(session_id);
CREATE INDEX idx_exercises_exercise_type ON public.exercises(exercise_type);

-- =====================================================
-- POSE ANALYSIS RECORDS (for analytics)
-- =====================================================
CREATE TABLE public.pose_analysis_records (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES public.workout_sessions(id) ON DELETE CASCADE NOT NULL,
    exercise_id UUID REFERENCES public.exercises(id) ON DELETE CASCADE,
    frame_number INTEGER NOT NULL,
    keypoints JSONB NOT NULL,
    overall_confidence FLOAT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    form_score FLOAT NOT NULL CHECK (form_score >= 0 AND form_score <= 100),
    corrections TEXT[] DEFAULT ARRAY[]::TEXT[],
    rep_counted BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policies for pose_analysis_records
CREATE POLICY "Users can view own pose records"
    ON public.pose_analysis_records FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.workout_sessions
            WHERE workout_sessions.id = pose_analysis_records.session_id
            AND workout_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own pose records"
    ON public.pose_analysis_records FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workout_sessions
            WHERE workout_sessions.id = pose_analysis_records.session_id
            AND workout_sessions.user_id = auth.uid()
        )
    );

-- Indexes
CREATE INDEX idx_pose_records_session_id ON public.pose_analysis_records(session_id);
CREATE INDEX idx_pose_records_exercise_id ON public.pose_analysis_records(exercise_id);
CREATE INDEX idx_pose_records_timestamp ON public.pose_analysis_records(timestamp);

-- =====================================================
-- VOICE FEEDBACK RECORDS
-- =====================================================
CREATE TABLE public.voice_feedback (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES public.workout_sessions(id) ON DELETE CASCADE NOT NULL,
    exercise_id UUID REFERENCES public.exercises(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    priority TEXT DEFAULT 'normal', -- low, normal, high, critical
    audio_url TEXT,
    delivered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policies for voice_feedback
CREATE POLICY "Users can view own feedback"
    ON public.voice_feedback FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.workout_sessions
            WHERE workout_sessions.id = voice_feedback.session_id
            AND workout_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own feedback"
    ON public.voice_feedback FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workout_sessions
            WHERE workout_sessions.id = voice_feedback.session_id
            AND workout_sessions.user_id = auth.uid()
        )
    );

-- Indexes
CREATE INDEX idx_voice_feedback_session_id ON public.voice_feedback(session_id);

-- =====================================================
-- WORKOUT TEMPLATES (predefined workouts)
-- =====================================================
CREATE TABLE public.workout_templates (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    workout_type TEXT NOT NULL,
    difficulty_level TEXT, -- beginner, intermediate, advanced
    estimated_duration_minutes INTEGER,
    exercises JSONB NOT NULL, -- Array of exercise definitions
    is_public BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policies for workout_templates
CREATE POLICY "Anyone can view public templates"
    ON public.workout_templates FOR SELECT
    USING (is_public = TRUE);

CREATE POLICY "Users can view own private templates"
    ON public.workout_templates FOR SELECT
    USING (auth.uid() = created_by);

CREATE POLICY "Users can create templates"
    ON public.workout_templates FOR INSERT
    WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Users can update own templates"
    ON public.workout_templates FOR UPDATE
    USING (auth.uid() = created_by);

-- Indexes
CREATE INDEX idx_workout_templates_workout_type ON public.workout_templates(workout_type);
CREATE INDEX idx_workout_templates_difficulty ON public.workout_templates(difficulty_level);

-- =====================================================
-- ACHIEVEMENTS
-- =====================================================
CREATE TABLE public.achievements (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    achievement_type TEXT NOT NULL, -- first_workout, 10_workouts, perfect_form, etc.
    title TEXT NOT NULL,
    description TEXT,
    icon_url TEXT,
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- RLS Policies for achievements
CREATE POLICY "Users can view own achievements"
    ON public.achievements FOR SELECT
    USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX idx_achievements_user_id ON public.achievements(user_id);
CREATE INDEX idx_achievements_earned_at ON public.achievements(earned_at);

-- =====================================================
-- FUNCTIONS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workout_sessions_updated_at BEFORE UPDATE ON public.workout_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exercises_updated_at BEFORE UPDATE ON public.exercises
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workout_templates_updated_at BEFORE UPDATE ON public.workout_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- STORAGE BUCKETS (run these in Supabase Dashboard > Storage)
-- =====================================================

-- Create storage buckets for:
-- 1. avatars - user profile pictures
-- 2. workout-videos - recorded workout sessions
-- 3. pose-snapshots - snapshots of poses for analysis
-- 4. voice-feedback - generated voice feedback audio files

-- Run these in the Supabase Dashboard:
/*
CREATE STORAGE BUCKET avatars
  PUBLIC false
  FILE_SIZE_LIMIT 2MB
  ALLOWED_MIME_TYPES ['image/jpeg', 'image/png', 'image/webp'];

CREATE STORAGE BUCKET workout-videos
  PUBLIC false
  FILE_SIZE_LIMIT 100MB
  ALLOWED_MIME_TYPES ['video/mp4', 'video/webm'];

CREATE STORAGE BUCKET pose-snapshots
  PUBLIC false
  FILE_SIZE_LIMIT 5MB
  ALLOWED_MIME_TYPES ['image/jpeg', 'image/png'];

CREATE STORAGE BUCKET voice-feedback
  PUBLIC false
  FILE_SIZE_LIMIT 5MB
  ALLOWED_MIME_TYPES ['audio/mpeg', 'audio/wav', 'audio/webm'];
*/
