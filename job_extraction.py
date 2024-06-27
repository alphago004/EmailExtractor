import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import re
import base64 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    # Check if token.json file exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (or expired) credentials, authenticate using InstalledAppFlow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_job_emails(service):
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    job_emails = []

    if not messages:
        print('No messages found.')
    else:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            msg_data = msg['payload']
            
            # Extract job information using the new function
            job_info = extract_job_information(msg_data)
            if job_info:
                job_emails.append(job_info)

    return job_emails

def extract_job_information(msg_data):
    email_content = ''
    if 'parts' in msg_data:
        for part in msg_data['parts']:
            if part['mimeType'] == 'text/plain':
                email_content += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    elif 'body' in msg_data and 'data' in msg_data['body']:
        email_content = base64.urlsafe_b64decode(msg_data['body']['data']).decode('utf-8')

    job_info = {}

    # Extract job title
    title_match = re.search(r'Job Title:\s*(.*)', email_content)
    if title_match:
        print("Gandu is Pandu 1")
        job_info['Job Title'] = title_match.group(1).strip()

    # Extract location
    location_match = re.search(r'Location:\s*(.*)', email_content)
    if location_match:
        print("Gandu is Pandu 2")
        job_info['Location'] = location_match.group(1).strip()

    # Extract duration
    duration_match = re.search(r'Duration:\s*(.*)', email_content)
    if duration_match:
        print("Gandu is Pandu 3")
        job_info['Duration'] = duration_match.group(1).strip()

    # Extract interview type
    interview_match = re.search(r'Interview type:\s*(.*)', email_content)
    if interview_match:
        print("Gandu is Pandu 4")
        job_info['Interview Type'] = interview_match.group(1).strip()

    # Extract pay range
    pay_range_match = re.search(r'Pay range:\s*(.*)', email_content)
    if pay_range_match:
        print("Gandu is Pandu 5")
        job_info['Pay Range'] = pay_range_match.group(1).strip()

    # Extract job description
    description_match = re.search(r'Job Description:(.*)Must Haves:', email_content, re.DOTALL)
    if description_match:
        print("Gandu is Pandu 6")
        job_info['Job Description'] = description_match.group(1).strip()

    # Extract must-have skills
    must_have_match = re.search(r'Must Haves:(.*)Additional Skills', email_content, re.DOTALL)
    if must_have_match:
        print("Gandu is Pandu 7")
        job_info['Must Haves'] = must_have_match.group(1).strip()

    # Extract additional skills
    additional_skills_match = re.search(r'Additional Skills(.*)Sample Tasks', email_content, re.DOTALL)
    if additional_skills_match:
        print("Gandu is Pandu 8")
        job_info['Additional Skills'] = additional_skills_match.group(1).strip()

    # Extract sample tasks
    sample_tasks_match = re.search(r'Sample Tasks(.*)$', email_content, re.DOTALL)
    if sample_tasks_match:
        print("Gandu is Pandu 9")
        job_info['Sample Tasks'] = sample_tasks_match.group(1).strip()

    return job_info

def parse_job_descriptions(emails):
    job_data = []
    for email in emails:
        job_titles = re.findall(r'(?i)\b(Java Developer|AWS Developer|C# Developer|Python Developer|Data Scientist)\b', email.get('Job Description', ''))
        job_data.extend(job_titles)
    return job_data

def create_report(job_data):
    job_df = pd.DataFrame(job_data, columns=['Job Title'])
    job_counts = job_df['Job Title'].value_counts().reset_index()
    job_counts.columns = ['Job Title', 'Count']
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Job Title', y='Count', data=job_counts)
    plt.title('Job Opportunities by Role')
    plt.xlabel('Job Title')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('job_report.png')
    plt.show()

if __name__ == '__main__':
    service = authenticate_gmail()
    job_emails = get_job_emails(service)
    job_data = parse_job_descriptions(job_emails)
    create_report(job_data)
