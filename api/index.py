"""
Vercel serverless function handler
"""
from app import app
from vercel import WSGI

# Vercel WSGI handler
handler = WSGI(app)

