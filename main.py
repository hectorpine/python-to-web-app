from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from simplegmail import Gmail
from googleapiclient.errors import HttpError
import base64
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Initialize the Gmail client
gmail = Gmail()

def get_message_body(payload):
    body = ''
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                body += base64.urlsafe_b64decode(part['body'].get('data', '')).decode('utf-8')
            elif part['mimeType'] == 'text/html':
                body += base64.urlsafe_b64decode(part['body'].get('data', '')).decode('utf-8')
    else:
        body += base64.urlsafe_b64decode(payload['body'].get('data', '')).decode('utf-8')
    return body

def receive_recent_emails(max_results=10):
    try:
        response = gmail.service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            maxResults=max_results,
            q='is:unread'
        ).execute()

        messages = response.get('messages', [])
        email_data = []
        for msg in messages:
            message = gmail.service.users().messages().get(
                userId='me', id=msg['id']
            ).execute()

            email_info = {
                "subject": next(header['value'] for header in message['payload']['headers'] if header['name'] == 'Subject'),
                "sender": next(header['value'] for header in message['payload']['headers'] if header['name'] == 'From'),
                "body": get_message_body(message['payload'])
            }
            email_data.append(email_info)

            # Mark the email as read
            gmail.service.users().messages().modify(
                userId='me',
                id=msg['id'],
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

        return email_data
    except HttpError as error:
        print(f"An error occurred: {error}")
        print(f"Error details: {error.content}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

class EmailRequest(BaseModel):
    email_id: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Email Processing API"}

@app.get("/emails/")
def get_emails(max_results: int = 10):
    emails = receive_recent_emails(max_results)
    if not emails:
        raise HTTPException(status_code=404, detail="No emails found")
    return {"emails": emails}

@app.post("/process-email/")
def process_email(email: EmailRequest):
    email_data = receive_recent_emails(max_results=1)  # Fetch one email for demo purposes
    if not email_data:
        raise HTTPException(status_code=404, detail="Email not found")
    
    email_content = email_data[0]['body']
    return {"email_content": email_content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
