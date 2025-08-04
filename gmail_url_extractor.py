#!/usr/bin/env python3
"""
Gmail URL Extractor - Works without OpenAI API
Extracts URLs and basic email information from Gmail
"""

import os
import base64
import re
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import urllib.parse

import streamlit as st
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailURLExtractor:
    def __init__(self):
        self.service = None
    
    def authenticate_gmail(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Check if token.json exists
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Check if credentials.json exists
                if not os.path.exists('credentials.json'):
                    st.error("""
                    Please download your Gmail API credentials:
                    1. Go to Google Cloud Console
                    2. Create a new project or select existing one
                    3. Enable Gmail API
                    4. Create credentials (OAuth 2.0 Client ID)
                    5. Download as credentials.json
                    6. Place it in this directory
                    """)
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            return True
        except Exception as e:
            st.error(f"Error building Gmail service: {e}")
            return False
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extract URLs from text content"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return list(set(urls))  # Remove duplicates
    
    def clean_email_content(self, content: str) -> str:
        """Clean and extract text content from email"""
        if not content:
            return ""
        
        # Decode base64 if needed
        try:
            content = base64.urlsafe_b64decode(content).decode('utf-8')
        except:
            pass
        
        # Parse HTML and extract text
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def get_email_content(self, message_id: str) -> Tuple[str, str, str, str]:
        """Get email content, subject, sender, and date"""
        try:
            message = self.service.users().messages().get(userId='me', id=message_id).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
            # Extract body content
            body = ""
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = part['body'].get('data', '')
                        break
                    elif part['mimeType'] == 'text/html':
                        body = part['body'].get('data', '')
            else:
                body = message['payload']['body'].get('data', '')
            
            cleaned_content = self.clean_email_content(body)
            return cleaned_content, subject, sender, date
            
        except Exception as e:
            st.error(f"Error getting email content: {e}")
            return "", "", "", ""
    
    def fetch_emails(self, query: str = "", max_results: int = 50) -> List[Dict]:
        """Fetch emails based on query"""
        if not self.service:
            st.error("Gmail service not initialized. Please authenticate first.")
            return []
            
        try:
            results = self.service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                content, subject, sender, date = self.get_email_content(message['id'])
                urls = self.extract_urls_from_text(content)
                
                email_data = {
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'content': content[:500] + "..." if len(content) > 500 else content,
                    'urls': urls,
                    'url_count': len(urls)
                }
                emails.append(email_data)
            
            return emails
            
        except Exception as e:
            st.error(f"Error fetching emails: {e}")
            return []
    
    def get_date_range_query(self, start_date: str, end_date: str) -> str:
        """Create Gmail query for date range"""
        return f"after:{start_date} before:{end_date}"
    
    def create_digest(self, emails: List[Dict]) -> Dict:
        """Create a comprehensive digest of emails"""
        if not emails:
            return {}
        
        # Extract all URLs
        all_urls = []
        for email in emails:
            all_urls.extend(email['urls'])
        
        # Top senders
        sender_counts = {}
        for email in emails:
            sender = email['sender']
            sender_counts[sender] = sender_counts.get(sender, 0) + 1
        
        # URL domains
        url_domains = {}
        for url in all_urls:
            try:
                domain = urllib.parse.urlparse(url).netloc
                url_domains[domain] = url_domains.get(domain, 0) + 1
            except:
                pass
        
        return {
            'total_emails': len(emails),
            'unique_urls': list(set(all_urls)),
            'total_urls': len(all_urls),
            'top_senders': sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'url_domains': sorted(url_domains.items(), key=lambda x: x[1], reverse=True)[:10],
            'date_range': {
                'start': emails[-1]['date'] if emails else None,
                'end': emails[0]['date'] if emails else None
            }
        }

def main():
    st.set_page_config(
        page_title="Gmail URL Extractor",
        page_icon="🔗",
        layout="wide"
    )
    
    st.title("🔗 Gmail URL Extractor")
    st.markdown("---")
    st.info("📧 This tool extracts URLs from your Gmail without requiring OpenAI API")
    
    # Initialize the extractor
    extractor = GmailURLExtractor()
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # Check if already authenticated
    if not hasattr(st.session_state, 'authenticated'):
        st.session_state.authenticated = False
    
    # Check if token.json exists (user was previously authenticated)
    if os.path.exists('token.json') and not st.session_state.authenticated:
        st.sidebar.info("🔑 Previous authentication found. Click 'Authenticate Gmail' to refresh.")
    
    # Authentication
    if st.sidebar.button("🔐 Authenticate Gmail"):
        with st.spinner("Authenticating with Gmail..."):
            if extractor.authenticate_gmail():
                st.sidebar.success("✅ Gmail authenticated successfully!")
                st.session_state.authenticated = True
                st.session_state.extractor = extractor
                st.rerun()
            else:
                st.sidebar.error("❌ Gmail authentication failed!")
    
    # Check if authenticated
    if not st.session_state.authenticated:
        st.warning("Please authenticate with Gmail first using the sidebar button.")
        
        # Show authentication status
        if os.path.exists('credentials.json'):
            st.success("✅ credentials.json found")
        else:
            st.error("❌ credentials.json not found - please download from Google Cloud Console")
        
        st.stop()
    
    # Email fetching options
    st.sidebar.header("Email Options")
    
    fetch_option = st.sidebar.selectbox(
        "Fetch emails by:",
        ["All emails", "Date range", "Custom query"]
    )
    
    max_results = st.sidebar.slider("Max emails to fetch:", 10, 100, 50)
    
    query = ""
    if fetch_option == "Date range":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("Start date", datetime.now() - timedelta(days=7))
        with col2:
            end_date = st.date_input("End date", datetime.now())
        
        query = extractor.get_date_range_query(
            start_date.strftime('%Y/%m/%d'),
            end_date.strftime('%Y/%m/%d')
        )
    
    elif fetch_option == "Custom query":
        query = st.sidebar.text_input("Gmail query (e.g., 'from:example@gmail.com', 'subject:meeting')")
    
    # Fetch emails button
    if st.sidebar.button("📥 Fetch Emails"):
        with st.spinner("Fetching emails and extracting URLs..."):
            # Use the authenticated extractor from session state
            if hasattr(st.session_state, 'extractor'):
                emails = st.session_state.extractor.fetch_emails(query, max_results)
            else:
                emails = extractor.fetch_emails(query, max_results)
            
            if emails:
                st.session_state.emails = emails
                st.session_state.digest = extractor.create_digest(emails)
                st.success(f"✅ Fetched {len(emails)} emails and extracted URLs!")
            else:
                st.error("No emails found or error occurred.")
    
    # Display results
    if hasattr(st.session_state, 'emails') and st.session_state.emails:
        emails = st.session_state.emails
        digest = st.session_state.digest
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Summary", "📧 Email List", "🔗 URLs"])
        
        with tab1:
            st.header("📊 Email Summary")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Emails", digest['total_emails'])
            
            with col2:
                st.metric("Total URLs", digest['total_urls'])
            
            with col3:
                st.metric("Unique URLs", len(digest['unique_urls']))
            
            # Top senders
            st.subheader("Top Senders")
            if digest['top_senders']:
                sender_df = pd.DataFrame(
                    digest['top_senders'],
                    columns=['Sender', 'Email Count']
                )
                st.dataframe(sender_df)
            
            # URL domains
            st.subheader("Top URL Domains")
            if digest['url_domains']:
                domain_df = pd.DataFrame(
                    digest['url_domains'],
                    columns=['Domain', 'URL Count']
                )
                st.bar_chart(domain_df.set_index('Domain'))
        
        with tab2:
            st.header("📧 Email List")
            
            # Search/filter
            search_term = st.text_input("Search emails:", placeholder="Search by subject, sender, or content...")
            
            filtered_emails = emails
            if search_term:
                filtered_emails = [
                    email for email in emails
                    if search_term.lower() in email['subject'].lower() or
                       search_term.lower() in email['sender'].lower() or
                       search_term.lower() in email['content'].lower()
                ]
            
            for i, email in enumerate(filtered_emails):
                with st.expander(f"📧 {email['subject']} - {email['sender']} ({email['url_count']} URLs)"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**From:** {email['sender']}")
                        st.write(f"**Date:** {email['date']}")
                        st.write(f"**URLs found:** {email['url_count']}")
                        
                        st.subheader("Content Preview")
                        st.write(email['content'])
                    
                    with col2:
                        if email['urls']:
                            st.subheader("URLs Found")
                            for url in email['urls']:
                                st.write(f"🔗 [{url}]({url})")
        
        with tab3:
            st.header("🔗 All URLs Found")
            
            if digest['unique_urls']:
                st.write(f"Found {len(digest['unique_urls'])} unique URLs:")
                
                for i, url in enumerate(digest['unique_urls'], 1):
                    st.write(f"{i}. [{url}]({url})")
                
                # Export URLs
                if st.button("📥 Export URLs"):
                    urls_text = "\n".join(digest['unique_urls'])
                    st.download_button(
                        label="Download URLs",
                        data=urls_text,
                        file_name="extracted_urls.txt",
                        mime="text/plain"
                    )
            else:
                st.info("No URLs found in the emails.")

if __name__ == "__main__":
    main() 