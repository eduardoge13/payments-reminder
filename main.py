# Setup libraries
import os
from datetime import datetime
from requests import Response
import requests
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
NOTION_API_BASE_URL = 'https://api.notion.com/v1'
NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

# 1. get_client_details function to fetch client details from Notion
def get_client_details() -> list:
    """
    This function calls the Notion API to get a list of clients that we will test the reminder on.
    """

    headers: dict = {
        'Authorization': f'Bearer {NOTION_API_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28',
    }

    
    response: Response = requests.post(
        f'{NOTION_API_BASE_URL}/databases/{NOTION_DATABASE_ID}/query', headers=headers)

    if response.status_code == 200:
        json_response: dict = response.json()['results']
    else:
        print("Something went wrong, STATUS CODE:", response.status_code)
        return []

    # 2. Parse the JSON response to extract client details
    clients: list = []
    for item in json_response:
        client: dict = {
            'id': item['id'],
            'name': item['properties']['Name']['title'][0]['plain_text'],
            'phone_number': item['properties']['Phone No.']['phone_number'],
            'email': item['properties']['Email']['email'],
            'due_date': item['properties']['Due Date']['date']['start'],
            'pending_amount': item['properties']['Pending Amount']['number'],
            
            
        }
        clients.append(client)

    return clients

# is_due function to check if the due date is approaching
def is_due(due_date: str) -> bool:
    """
    This function checks if the date is due or not.
    """

    today = datetime.today()
    delta = datetime.strptime(due_date, "%Y-%m-%d") - today
    return delta.days == 7 or delta.days == 3 or delta.days == 1 or delta.days < 0


# Send reminder function to send Whatsapp reminders
def send_reminder(client: dict):
    """
    This function sends a WhatsApp notification using the Twilio WhatsApp Business API.
    """

    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    # DONT CHANGE THE NUMBER THATS THE TWILIO SANDBOX NUMBER
    from_whatsapp_number = 'whatsapp:+14155238886',
    to_whatsapp_number = f"whatsapp:{client['phone_number']}"
    body: str = f"Hi {client['name']}. Your payment of MXN{client['pending_amount']} is due since {client['due_date']}."

    try:
        twilio_client.messages.create(body=body,
                                      from_=from_whatsapp_number,
                                      to=to_whatsapp_number)
    except Exception as e:
        print(e)
        print('There was an error sending the message')

# main function to run the script
def main():
    clients: list = get_client_details()
    for client in clients:
        if is_due(client['due_date']):
            print(client)
            send_reminder(client)

if __name__ == '__main__':
    main()
