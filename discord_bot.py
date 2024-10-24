import discord
from discord.ext import commands
import requests
import json


def send_message(bot_token, user_id, signal, call, put, webhook_url, send_to_user=True, send_to_webhook=True):
    # Set up the bot with a command prefix
    intents = discord.Intents.default()
    intents.message_content = True  # Enable message content intent
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Event triggered when the bot is ready
    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")

        if send_to_user:
            await send_message_to_user(user_id)
        if send_to_webhook:
            send_message_to_webhook(webhook_url, signal, call, put)

        await bot.close()  # Close the bot after sending the message

    # Function that sends a message to a user when triggered
    async def send_message_to_user(user_id):
        user = await bot.fetch_user(user_id)  # Fetch the user object using the user ID
        try:
            await user.send(f"Signal: {signal}\nCall: ${format(float(call), ',')}\nPut: ${format(float(put), ',')}")
            x = float(put)
            y = float(call)
            await user.send(f"Difference: ${format(round(abs(x - y), 2), ',')}")

            print(f"Message sent to {user.name}")
        except discord.Forbidden:
            print(f"Could not send message to {user.name} (they might have DMs disabled)")

    # Function to send a message to a Discord webhook
    def send_message_to_webhook(webhook_url, signal, call, put):
        data = {
            "content": f"Signal: {signal}\nCall: ${format(float(call), ',')}\nPut: ${format(float(put), ',')}\nDifference: ${format(round(abs(float(put) - float(call)), 2), ',')}"
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(webhook_url, data=json.dumps(data), headers=headers)
        if response.status_code == 204:
            print("Message sent to webhook successfully.")
        else:
            print(f"Failed to send message to webhook. Status code: {response.status_code}")

    # Start the bot with your token
    bot.run(bot_token)