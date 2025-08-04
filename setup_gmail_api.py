#!/usr/bin/env python3
"""
Gmail API Setup Helper Script
This script helps you set up Gmail API credentials for the AI Summarizer tool.
"""

import os
import webbrowser
import json
from pathlib import Path

def print_step(step_num, title, description):
    """Print a formatted step"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*60}")
    print(description)
    print()

def main():
    print("🔧 Gmail API Setup Helper")
    print("This script will guide you through setting up Gmail API credentials.")
    print("Follow each step carefully to get your credentials.json file.\n")
    
    # Step 1: Google Cloud Console
    print_step(1, "Access Google Cloud Console", 
               "1. Open your web browser\n"
               "2. Go to: https://console.cloud.google.com/\n"
               "3. Sign in with your Google account\n"
               "4. Create a new project or select an existing one")
    
    input("Press Enter when you're ready to continue...")
    
    # Step 2: Enable Gmail API
    print_step(2, "Enable Gmail API",
               "1. In the Google Cloud Console, go to 'APIs & Services' > 'Library'\n"
               "2. Search for 'Gmail API'\n"
               "3. Click on 'Gmail API'\n"
               "4. Click 'Enable' button")
    
    input("Press Enter when you've enabled the Gmail API...")
    
    # Step 3: Create Credentials
    print_step(3, "Create OAuth 2.0 Credentials",
               "1. Go to 'APIs & Services' > 'Credentials'\n"
               "2. Click 'Create Credentials' > 'OAuth client ID'\n"
               "3. If prompted, configure the OAuth consent screen:\n"
               "   - User Type: External\n"
               "   - App name: Gmail AI Summarizer\n"
               "   - User support email: your email\n"
               "   - Developer contact email: your email\n"
               "   - Save and continue through all steps\n"
               "4. Back to credentials, select 'Desktop application'\n"
               "5. Name: Gmail AI Summarizer\n"
               "6. Click 'Create'")
    
    input("Press Enter when you've created the credentials...")
    
    # Step 4: Download Credentials
    print_step(4, "Download Credentials",
               "1. After creating credentials, you'll see a download button\n"
               "2. Click 'Download JSON'\n"
               "3. Rename the downloaded file to 'credentials.json'\n"
               "4. Move it to this project directory")
    
    # Check if credentials.json exists
    if os.path.exists('credentials.json'):
        print("✅ Found credentials.json in the current directory!")
        
        # Validate the file
        try:
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
            
            if 'installed' in creds or 'web' in creds:
                print("✅ Credentials file appears to be valid!")
                print("\n🎉 Setup complete! You can now run the Gmail AI Summarizer.")
                print("\nNext steps:")
                print("1. Set up your OpenAI API key (see README.md)")
                print("2. Run: streamlit run gmail_ai_summarizer.py")
            else:
                print("❌ Credentials file format seems incorrect.")
                print("Please ensure you downloaded the OAuth 2.0 client credentials.")
        except json.JSONDecodeError:
            print("❌ Invalid JSON file. Please check your credentials.json file.")
    else:
        print("❌ credentials.json not found in the current directory.")
        print("Please download and place the credentials file here.")
    
    print("\n" + "="*60)
    print("📚 Additional Resources:")
    print("• README.md - Complete setup and usage guide")
    print("• Google Cloud Console: https://console.cloud.google.com/")
    print("• Gmail API Documentation: https://developers.google.com/gmail/api")
    print("="*60)

if __name__ == "__main__":
    main() 