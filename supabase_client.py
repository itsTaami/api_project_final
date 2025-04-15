from supabase import create_client, Client

url: str = "https://gqajdjmciuzhiwcqniho.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdxYWpkam1jaXV6aGl3Y3FuaWhvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE4Mzk2MDQsImV4cCI6MjA1NzQxNTYwNH0.m719elC1ldMX51cBJuv4fhlbPq3jyf5Z_z4relZvVQo"

supabase: Client = create_client(url, key)