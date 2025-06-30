# Payment Reminder System

An automated payment reminder system that uses machine learning optimization and WhatsApp messaging to improve payment collection rates.

## Features

- Customer segmentation using RFM analysis
- Machine learning model for optimal channel selection
- Automated WhatsApp reminders via Twilio
- Integration with Notion database for client management
- Daily automated execution via GitHub Actions

## Prerequisites

- Python 3.8+
- Notion API access
- Twilio account with WhatsApp Business API
- GitHub account

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/eduardoge13/payments-reminder
   cd payment-reminders
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Create a .env file with your API credentials
   ```
   NOTION_API_TOKEN=your_notion_api_token
   NOTION_DATABASE_ID=your_database_id
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   ```

## Usage

Run the complete system:
```bash
python main.py
```

This will:
1. Run the optimization model and display results
2. Send WhatsApp reminders to clients with due payments

## Notion Database Setup

Your Notion database should have these properties:
- Name (Title): Client name
- Phone No. (Phone): Client phone number
- Email (Email): Client email address
- Due Date (Date): Payment due date
- Pending Amount (Number): Amount pending

## GitHub Actions Setup

1. Add repository secrets in GitHub:
   - NOTION_API_TOKEN
   - NOTION_DATABASE_ID
   - TWILIO_ACCOUNT_SID
   - TWILIO_AUTH_TOKEN

2. The workflow will run automatically:
   - Daily at 9 AM UTC
   - Can be triggered manually from Actions tab

## Project Structure

- main.py: Main application with optimization and WhatsApp sending
- payment_reminder_optimizer.py: Machine learning optimization engine
- requirements.txt: Python dependencies
- .github/workflows/main.yml: GitHub Actions workflow

## Testing

Test your setup:
```bash
python main.py
```

Check the output for:
- Optimization results and customer segments
- WhatsApp message sending status
- Any error messages

## Troubleshooting

- Verify all API credentials in .env file
- Check Notion database structure matches requirements
- Ensure Twilio WhatsApp Business API is enabled
- Review GitHub Actions logs for detailed error information

# References and Sources
- [Cursor AI Assistant](https://cursor.sh/) - AI-powered code editor used for development and optimization of this payment reminder system
- [Notion API Documentation - Retrieve a database](https://developers.notion.com/reference/retrieve-a-database)
- [Twilio WhatsApp API Documentation](https://www.twilio.com/docs/whatsapp)
- [How to Build Client Payment Reminders using Twilio, Notion, and Python](https://www.twilio.com/en-us/blog/payment-reminders-twilio-notion-python)
- [RFM Customer Segmentation Analysis In Action!](https://justdataplease.medium.com/rfm-customer-segmentation-analysis-in-action-9108c906c628)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [What is a payment reminder? How to write and send one successfully](https://stripe.com/mx/resources/more/what-is-a-payment-reminder-how-to-write-and-send-one-successfully)
- [payment-reminders-twilio-notion-python - Github](https://github.com/ravgeetdhillon/payment-reminders-twilio-notion-python)


