import asyncio
from streamed_api import fetch_streamed_chat_content

API_KEY = ""
MESSAGE_INPUT = "What is the capital of France?"

async def handle_response(response):
    print(f"Assistant: {response}")

async def on_finish():
    print("Chat finished")

async def on_error(error):
    print(f"Error: {error}")

options = {
    "apiKey": API_KEY,
    "messageInput": MESSAGE_INPUT,
}

async def main():
    await fetch_streamed_chat_content(options, on_response=handle_response, on_finish=on_finish, on_error=on_error)

# Run the main function
asyncio.run(main())
