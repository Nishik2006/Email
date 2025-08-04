#!/usr/bin/env python3
"""
Check Gmail API status and provide fixes
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def check_gmail_api():
    """Check if Gmail API is enabled"""
    print("🔧 Checking Gmail API Status")
    print("=" * 50)
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found")
        print("Please download your Gmail API credentials from Google Cloud Console")
        return False
    
    try:
        # Load credentials
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        # Extract project ID
        if 'installed' in creds_data:
            project_id = creds_data['installed'].get('project_id', 'Unknown')
        else:
            project_id = 'Unknown'
        
        print(f"📁 Project ID: {project_id}")
        
        # Try to authenticate
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        # Try to build service
        service = build('gmail', 'v1', credentials=creds)
        
        # Test API call
        try:
            results = service.users().messages().list(userId='me', maxResults=1).execute()
            print("✅ Gmail API is enabled and working!")
            return True
        except HttpError as e:
            if 'accessNotConfigured' in str(e):
                print("❌ Gmail API is NOT enabled")
                print(f"\n🔗 Enable Gmail API here:")
                print(f"https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project={project_id}")
                print(f"\nOr manually:")
                print("1. Go to Google Cloud Console")
                print("2. Select your project")
                print("3. Go to APIs & Services > Library")
                print("4. Search for 'Gmail API'")
                print("5. Click Enable")
                return False
            else:
                print(f"❌ Other error: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = check_gmail_api()
    if success:
        print("\n🎉 Gmail API is ready! You can now use the Gmail AI Summarizer.")
    else:
        print("\n⚠️  Please enable Gmail API and try again.") 