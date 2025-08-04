#!/usr/bin/env python3
"""
Demo script for Gmail AI Summarizer
This script demonstrates how to use the GmailAISummarizer class programmatically.
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from gmail_ai_summarizer import GmailAISummarizer

def main():
    """Demo the Gmail AI Summarizer functionality"""
    
    # Load environment variables
    load_dotenv()
    
    print("🚀 Gmail AI Summarizer Demo")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key not found!")
        print("Please set OPENAI_API_KEY in your .env file")
        return
    
    # Initialize the summarizer
    print("📧 Initializing Gmail AI Summarizer...")
    summarizer = GmailAISummarizer()
    
    # Authenticate with Gmail
    print("🔐 Authenticating with Gmail...")
    if not summarizer.authenticate_gmail():
        print("❌ Gmail authentication failed!")
        print("Please ensure you have credentials.json in the current directory")
        return
    
    print("✅ Gmail authenticated successfully!")
    
    # Demo different email fetching scenarios
    print("\n📥 Fetching emails...")
    
    # Scenario 1: Recent emails
    print("\n1️⃣ Fetching recent emails...")
    recent_emails = summarizer.fetch_emails(max_results=5)
    
    if recent_emails:
        print(f"✅ Found {len(recent_emails)} recent emails")
        
        # Show first email details
        first_email = recent_emails[0]
        print(f"\n📧 First email:")
        print(f"   Subject: {first_email['subject']}")
        print(f"   From: {first_email['sender']}")
        print(f"   Date: {first_email['date']}")
        print(f"   Sentiment: {first_email['sentiment']}")
        print(f"   URLs found: {len(first_email['urls'])}")
        print(f"   Summary: {first_email['summary']}")
        
        if first_email['key_points']:
            print(f"   Key points: {', '.join(first_email['key_points'])}")
        
        if first_email['action_items']:
            print(f"   Action items: {', '.join(first_email['action_items'])}")
    else:
        print("❌ No recent emails found")
    
    # Scenario 2: Date range (last 7 days)
    print("\n2️⃣ Fetching emails from last 7 days...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    date_query = summarizer.get_date_range_query(
        start_date.strftime('%Y/%m/%d'),
        end_date.strftime('%Y/%m/%d')
    )
    
    date_emails = summarizer.fetch_emails(query=date_query, max_results=10)
    
    if date_emails:
        print(f"✅ Found {len(date_emails)} emails in the last 7 days")
        
        # Create digest
        digest = summarizer.create_digest(date_emails)
        print(f"\n📊 Digest Summary:")
        print(f"   Total emails: {digest['total_emails']}")
        print(f"   Unique URLs: {len(digest['unique_urls'])}")
        print(f"   Action items: {len(digest['action_items'])}")
        print(f"   Sentiment distribution: {digest['sentiment_distribution']}")
        
        if digest['top_senders']:
            print(f"   Top sender: {digest['top_senders'][0][0]} ({digest['top_senders'][0][1]} emails)")
        
        if digest['unique_urls']:
            print(f"\n🔗 Sample URLs found:")
            for i, url in enumerate(digest['unique_urls'][:3], 1):
                print(f"   {i}. {url}")
        
        if digest['action_items']:
            print(f"\n📋 Sample action items:")
            for i, item in enumerate(digest['action_items'][:3], 1):
                print(f"   {i}. {item}")
    else:
        print("❌ No emails found in the last 7 days")
    
    # Scenario 3: Custom query (emails with attachments)
    print("\n3️⃣ Fetching emails with attachments...")
    attachment_emails = summarizer.fetch_emails(query="has:attachment", max_results=5)
    
    if attachment_emails:
        print(f"✅ Found {len(attachment_emails)} emails with attachments")
        
        # Show attachment email details
        for i, email in enumerate(attachment_emails[:2], 1):
            print(f"\n📎 Email {i} with attachment:")
            print(f"   Subject: {email['subject']}")
            print(f"   From: {email['sender']}")
            print(f"   Sentiment: {email['sentiment']}")
            print(f"   Summary: {email['summary'][:100]}...")
    else:
        print("❌ No emails with attachments found")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\n💡 Tips:")
    print("• Use the web interface for better visualization: streamlit run gmail_ai_summarizer.py")
    print("• Try different Gmail search queries for specific results")
    print("• Adjust max_results based on your needs")
    print("• Check the README.md for more features and usage examples")

if __name__ == "__main__":
    main() 