import discord
from discord.ext import commands

def run_discord_bot(bot_token, user_id, signal, call, put):
    # Set up the bot with a command prefix
    intents = discord.Intents.default()
    intents.message_content = True  # Enable message content intent
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Event triggered when the bot is ready
    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")
        await send_message_to_user(user_id)
        await bot.close()  # Close the bot after sending the message

    # Function that sends a message to a user when triggered
    async def send_message_to_user(user_id):
        user = await bot.fetch_user(user_id)  # Fetch the user object using the user ID
        try:
            await user.send(f"Signal: {signal}\nCall: {call}\nPut: {put}")
            x = put.replace("$", "").replace(",", "")
            y = call.replace("$", "").replace(",", "")
            x = float(x)
            y = float(y)
            await user.send(f"Difference: ${format(round(abs(x-y),2), ",")}")

            print(f"Message sent to {user.name}")
        except discord.Forbidden:
            print(f"Could not send message to {user.name} (they might have DMs disabled)")

    # Start the bot with your token
    bot.run(bot_token)

# Example usage:
# Replace "YOUR_DISCORD_BOT_TOKEN" and "USER_ID" with actual values

