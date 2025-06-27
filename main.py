# Setup libraries
import os
from datetime import datetime
from requests import Response
import requests
from dotenv import load_dotenv
from twilio.rest import Client
import pandas as pd
from payment_reminder_optimizer import create_sample_data, PaymentReminderOptimizer

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
NOTION_API_BASE_URL = 'https://api.notion.com/v1'
NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

def get_client_details() -> list:
    """fetches client details from notion database"""
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

def is_due(due_date: str) -> bool:
    """checks if the due date is approaching"""
    today = datetime.today()
    delta = datetime.strptime(due_date, "%Y-%m-%d") - today
    return delta.days == 7 or delta.days == 3 or delta.days == 1 or delta.days < 0

def send_reminder(client: dict):
    """sends a whatsapp notification using twilio api"""
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    from_whatsapp_number = 'whatsapp:+14155238886'
    to_whatsapp_number = f"whatsapp:{client['phone_number']}"
    body: str = f"Hi {client['name']}. Your payment of MXN{client['pending_amount']} is due since {client['due_date']}."

    try:
        twilio_client.messages.create(body=body,
                                      from_=from_whatsapp_number,
                                      to=to_whatsapp_number)
        print(f"Sent WhatsApp reminder to {client['name']} at {client['phone_number']}")
    except Exception as e:
        print(f"Error sending message to {client['name']}: {e}")

def run_optimization():
    """runs the payment reminder optimization model"""
    print("=== Payment Reminder Optimization ===")
    
    customer_data, interaction_data = create_sample_data()
    optimizer = PaymentReminderOptimizer()
    
    # run segmentation
    segmented_data = optimizer.segment_customers_rfm(customer_data)
    
    # run channel optimization
    optimizer.optimize_channel_selection(interaction_data)
    
    # run frequency optimization
    optimizer.calculate_optimal_frequency(segmented_data)
    
    # merge data for strategy generation
    merged_data = pd.merge(segmented_data, interaction_data, on='customer_id', how='left')
    
    # generate sample strategies
    print("\nSample Personalized Strategies:")
    for customer_id in customer_data.sample(5)['customer_id']:
        strategy = optimizer.generate_personalized_strategy(customer_id, merged_data)
        print(f"  {customer_id}: {strategy['segment']} -> {strategy['optimal_channel']} -> "
              f"{strategy['reminder_frequency']} reminders (Confidence: {strategy['personalization_confidence']:.1%})")
    
    return optimizer, merged_data

def send_whatsapp_reminders():
    """sends whatsapp reminders to clients from notion database"""
    print("\n=== Sending WhatsApp Reminders ===")
    
    clients = get_client_details()
    if not clients:
        print("No clients found in notion database")
        return
    
    for client in clients:
        if is_due(client['due_date']):
            send_reminder(client)

def main():
    """main function to run the complete payment reminder system"""
    # step 1: run optimization model
    optimizer, merged_data = run_optimization()
    
    # step 2: send whatsapp reminders
    send_whatsapp_reminders()
    
    print("\n=== Payment Reminder System Complete ===")

if __name__ == "__main__":
    main()
