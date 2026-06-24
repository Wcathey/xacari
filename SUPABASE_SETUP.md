# Supabase Setup Guide for Xacari

This guide will help you set up your Supabase project for the Xacari workout coach application.

## Step 1: Get Supabase Credentials

1. Go to your [Supabase Dashboard](https://app.supabase.com)
2. Select your Xacari project (or create a new one)
3. Go to **Settings** → **API**
4. Copy the following values:
   - **Project URL**: `SUPABASE_URL`
   - **anon public key**: `SUPABASE_ANON_KEY`
   - **service_role key**: `SUPABASE_SERVICE_ROLE_KEY` (keep this secret!)

## Step 2: Configure Environment Variables

### Backend (.env)
```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and add your Supabase credentials:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

### Mobile (will be created in Phase 2)
You'll add these to your React Native app environment configuration.

## Step 3: Create Database Schema

1. Go to **SQL Editor** in your Supabase Dashboard
2. Click **New Query**
3. Copy and paste the contents of `supabase_schema.sql`
4. Click **Run** to execute the SQL

This will create:
- ✅ User profiles table
- ✅ Workout sessions table
- ✅ Exercises table
- ✅ Pose analysis records table
- ✅ Voice feedback table
- ✅ Workout templates table
- ✅ Achievements table
- ✅ All necessary RLS policies
- ✅ Indexes for performance
- ✅ Triggers for automatic timestamp updates

## Step 4: Set Up Storage Buckets

Go to **Storage** in your Supabase Dashboard and create these buckets:

### 1. avatars
- **Name**: `avatars`
- **Public**: No
- **File size limit**: 2MB
- **Allowed MIME types**: `image/jpeg`, `image/png`, `image/webp`

**Storage Policy** (add in Storage → Policies):
```sql
-- Allow users to upload their own avatar
CREATE POLICY "Users can upload own avatar"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'avatars' AND
  auth.uid()::text = (storage.foldername(name))[1]
);

-- Allow users to view their own avatar
CREATE POLICY "Users can view own avatar"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'avatars' AND
  auth.uid()::text = (storage.foldername(name))[1]
);

-- Allow users to update their own avatar
CREATE POLICY "Users can update own avatar"
ON storage.objects FOR UPDATE
USING (
  bucket_id = 'avatars' AND
  auth.uid()::text = (storage.foldername(name))[1]
);
```

### 2. workout-videos
- **Name**: `workout-videos`
- **Public**: No
- **File size limit**: 100MB
- **Allowed MIME types**: `video/mp4`, `video/webm`

**Storage Policy**:
```sql
-- Allow users to upload workout videos
CREATE POLICY "Users can upload workout videos"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'workout-videos' AND
  auth.uid()::text = (storage.foldername(name))[1]
);

-- Allow users to view own videos
CREATE POLICY "Users can view own videos"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'workout-videos' AND
  auth.uid()::text = (storage.foldername(name))[1]
);
```

### 3. pose-snapshots
- **Name**: `pose-snapshots`
- **Public**: No
- **File size limit**: 5MB
- **Allowed MIME types**: `image/jpeg`, `image/png`

**Storage Policy**:
```sql
-- Similar to workout-videos policies
CREATE POLICY "Users can manage pose snapshots"
ON storage.objects FOR ALL
USING (
  bucket_id = 'pose-snapshots' AND
  auth.uid()::text = (storage.foldername(name))[1]
);
```

### 4. voice-feedback
- **Name**: `voice-feedback`
- **Public**: No
- **File size limit**: 5MB
- **Allowed MIME types**: `audio/mpeg`, `audio/wav`, `audio/webm`

**Storage Policy**:
```sql
-- Users can view/download their voice feedback
CREATE POLICY "Users can access voice feedback"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'voice-feedback' AND
  auth.uid()::text = (storage.foldername(name))[1]
);
```

## Step 5: Configure Authentication

Go to **Authentication** → **Providers**:

1. **Enable Email/Password** authentication
2. **Optional**: Enable OAuth providers (Google, Apple, etc.)
3. Go to **Authentication** → **URL Configuration**:
   - Add your site URL (for development: `http://localhost:8081`)
   - Add redirect URLs for your mobile app

### Email Templates (Optional)
Customize email templates in **Authentication** → **Email Templates**:
- Confirm signup
- Reset password
- Magic link

## Step 6: Verify Setup

Test your database connection:

```bash
# From backend directory
cd backend
source xacari_env/bin/activate
python -c "
from app.core.config import settings
print(f'Supabase URL: {settings.SUPABASE_URL}')
print(f'Anon Key configured: {bool(settings.SUPABASE_ANON_KEY)}')
"
```

## Database Schema Overview

### Tables Structure

```
auth.users (Supabase managed)
└── profiles (1:1)
    ├── workout_sessions (1:many)
    │   ├── exercises (1:many)
    │   ├── pose_analysis_records (1:many)
    │   └── voice_feedback (1:many)
    └── achievements (1:many)

workout_templates (standalone)
```

### Key Features

- **Row Level Security (RLS)**: All tables have RLS enabled
- **Automatic timestamps**: created_at and updated_at auto-managed
- **Cascading deletes**: When a user is deleted, all their data is removed
- **Profile auto-creation**: Profile created automatically on user signup
- **Indexes**: Optimized queries on common search fields

## Next Steps

After Supabase setup is complete:

1. ✅ Test backend API with Supabase (Phase 1 complete)
2. 🔄 Set up React Native mobile app (Phase 2)
3. 🔄 Implement authentication in mobile app
4. 🔄 Add pose tracking and analysis
5. 🔄 Integrate voice feedback system

## Troubleshooting

### Can't connect to Supabase
- Verify your environment variables are correct
- Check that your Supabase project is active
- Ensure you're using the correct API keys

### RLS Policies blocking queries
- Make sure you're authenticated when making requests
- Check that the user's UUID matches the data they're trying to access
- Test policies using Supabase Dashboard → SQL Editor

### Storage uploads failing
- Verify bucket policies are configured correctly
- Check file size limits
- Ensure MIME types are allowed

## Security Notes

⚠️ **IMPORTANT**:
- Never commit `.env` files to git
- Keep `SUPABASE_SERVICE_ROLE_KEY` secret (server-side only)
- Use `SUPABASE_ANON_KEY` in mobile app (client-side safe)
- Always validate data on the backend before saving

## Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [Storage Guide](https://supabase.com/docs/guides/storage)
- [React Native + Supabase](https://supabase.com/docs/guides/getting-started/tutorials/with-expo-react-native)
