from simplegmail import Gmail
from googleapiclient.errors import HttpError
import base64
from bs4 import BeautifulSoup

# Initialize the Gmail client
gmail = Gmail()

def receive_recent_emails(max_results=10):
    try:
        # Fetch the messages with the specified query
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

def process_emails(email_data):
    # Example processing: Log email subjects
    for email in email_data:
        print(f"Processing email from {email['sender']}: {email['subject']}")
        # Add your processing logic here

def export_to_txt(subject, body, filename="draft.txt"):
    try:
        with open(filename, 'w') as file:
            file.write(f"Subject: {subject}\n\n")
            file.write(body)
        print(f"Draft exported to {filename}")
    except Exception as e:
        print(f"An error occurred while writing to file: {e}")

# Main function to integrate with CrewAI
def main():
    emails = receive_recent_emails(max_results=10)
    process_emails(emails)
    # Example: Export the first email processed to a text file
    if emails:
        export_to_txt(emails[0]['subject'], emails[0]['body'])

if __name__ == "__main__":
    main()
