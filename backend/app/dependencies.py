from app.config import settings

def get_supabase_url():
    return settings.SUPABASE_URL

def get_supabase_key():
    return settings.SUPABASE_KEY
