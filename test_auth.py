#!/usr/bin/env python3
"""
Test script to verify Gmail authentication
"""

import os
from dotenv import load_dotenv
from gmail_ai_summarizer import GmailAISummarizer

def test_authentication():
    """Test Gmail authentication"""
    print("🔧 Testing Gmail Authentication")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check files
    print("📁 Checking required files...")
    if os.path.exists('credentials.json'):
        print("✅ credentials.json found")
    else:
        print("❌ credentials.json not found")
        return False
    
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("❌ .env file not found")
        return False
    
    # Check OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("✅ OpenAI API key found")
    else:
        print("❌ OpenAI API key not found in .env file")
        return False
    
    # Test Gmail authentication
    print("\n🔐 Testing Gmail authentication...")
    try:
        summarizer = GmailAISummarizer()
        if summarizer.authenticate_gmail():
            print("✅ Gmail authentication successful!")
            
            # Test fetching emails
            print("\n📧 Testing email fetch...")
            emails = summarizer.fetch_emails(max_results=1)
            if emails:
                print(f"✅ Successfully fetched {len(emails)} email(s)")
                print(f"📧 First email subject: {emails[0]['subject']}")
            else:
                print("⚠️  No emails found (this might be normal if inbox is empty)")
            
            return True
        else:
            print("❌ Gmail authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return False

if __name__ == "__main__":
    success = test_authentication()
    if success:
        print("\n🎉 All tests passed! Your setup is working correctly.")
        print("You can now run: streamlit run gmail_ai_summarizer.py")
    else:
        print("\n❌ Tests failed. Please check your setup.")
        print("Make sure you have:")
        print("1. credentials.json from Google Cloud Console")
        print("2. .env file with OPENAI_API_KEY")
        print("3. Gmail API enabled in Google Cloud Console") 