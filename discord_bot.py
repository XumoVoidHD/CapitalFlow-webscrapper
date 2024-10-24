import discord
from discord.ext import commands
import requests
import json


def send_message(bot_token, user_id, signal, call, put, webhook_url, send_to_user=True, send_to_webhook=True):
    
    intents = discord.Intents.default()
    intents.message_content = True  
    bot = commands.Bot(command_prefix="?", intents=intents)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")

        if send_to_user:
            await send_message_to_user(user_id)
        if send_to_webhook:
            send_message_to_webhook(webhook_url, signal, call, put)

        await bot.close() 

    async def send_message_to_user(user_id):
        user = await bot.fetch_user(user_id)  
        try:
            await user.send(f"Signal: {signal}\nCall: ${format(float(call), ',')}\nPut: ${format(float(put), ',')}")
            x = float(put)
            y = float(call)
            await user.send(f"Difference: ${format(round(abs(x - y), 2), ',')}")

            print(f"Message sent to {user.name}")
        except discord.Forbidden:
            print(f"Could not send message to {user.name} (they might have DMs disabled)")

    def send_message_to_webhook(webhook_url, signal, call, put):
        data = {
            "content": f"Signal: {signal}\nCall: ${format(float(call), ',')}\nPut: ${format(float(put), ',')}\nDifference: ${format(round(abs(float(put) - float(call)), 2), ',')}"
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(webhook_url, data=json.dumps(data), headers=headers)
        if response.status_code == 204:
            print("Success")
        else:
            print(f"Failed. Status code: {response.status_code}")

    bot.run(bot_token)
