import json
import asyncio
import aiohttp
from typing import Callable

# A utility function to create a promise that rejects after a specified timeout
async def timeout(ms: int):
    await asyncio.sleep(ms / 1000)
    raise TimeoutError("Timeout")

async def fetch_streamed_chat_content(options, on_response=None, on_finish=None, on_error=None):

    try:
        async def response_chunk_handler(response_chunk):
            content = json.loads(response_chunk)["choices"][0]["delta"]["content"]
            if content and on_response:
                await on_response(content)

        await fetch_streamed_chat(options, response_chunk_handler)

        if on_finish:
            await on_finish()
    except Exception as error:
        if on_error:
            await on_error(error)

# The main function to fetch a streamed chat response and process it
async def fetch_streamed_chat(options, on_chunk_received: Callable):
    api_key = options.get("apiKey")
    message_input = options.get("messageInput")
    api_url = options.get("apiUrl", "https://api.openai.com/v1/chat/completions")
    model = options.get("model", "gpt-3.5-turbo")
    temperature = options.get("temperature")
    top_p = options.get("topP")
    n = options.get("n")
    stop = options.get("stop")
    max_tokens = options.get("maxTokens")
    presence_penalty = options.get("presencePenalty")
    frequency_penalty = options.get("frequencyPenalty")
    logit_bias = options.get("logitBias")
    user = options.get("user")
    retry_count = options.get("retryCount", 3)
    fetch_timeout = options.get("fetchTimeout", 20000)
    read_timeout = options.get("readTimeout", 10000)
    retry_interval = options.get("retryInterval", 2000)
    total_time = options.get("totalTime", 300000)

    stream = True
    messages = message_input if isinstance(message_input, list) else [{"role": "user", "content": message_input}]
    # Prepare the request body
    body = {
        "model": model,
        "messages": messages,
        "stream": stream,
    }
    if temperature is not None:
        body["temperature"] = temperature
    if top_p is not None:
        body["top_p"] = top_p
    if n is not None:
        body["n"] = n
    if stop is not None:
        body["stop"] = stop
    if max_tokens is not None:
        body["max_tokens"] = max_tokens
    if presence_penalty is not None:
        body["presence_penalty"] = presence_penalty
    if frequency_penalty is not None:
        body["frequency_penalty"] = frequency_penalty
    if logit_bias is not None:
        body["logit_bias"] = logit_bias
    if user is not None:
        body["user"] = user

    body = json.dumps(body)

    start_time = asyncio.get_event_loop().time()

    async def total_time_timeout():
        elapsed_time = asyncio.get_event_loop().time() - start_time
        remaining_time = total_time / 1000 - elapsed_time

        if remaining_time <= 0:
            raise TimeoutError("Total timeout reached")
        else:
            await timeout(remaining_time * 1000)

    # A function to process the response stream and invoke the on_chunk_received callback
    # for each valid line in the stream
    async def process_stream(reader, on_chunk_received):
        while True:
            try:
                # Wait for either the next chunk or a timeout
                result = await asyncio.wait_for(
                    reader.readuntil(b"\n"), read_timeout / 1000, loop=reader._loop)
            except asyncio.TimeoutError:
                raise TimeoutError("Timeout")
            except asyncio.IncompleteReadError:
                result = b''
            except TimeoutError as exc:
                raise exc
            except Exception as e:
                print(f"Error reading stream: {e}")
                raise e

            # Decode the chunk
            chunk = result.decode("utf-8")

            # If the stream is done, return
            if not chunk:
                return

            # Remove the "data: " prefix from the line and split into lines
            messages = chunk.strip().split("\n")
            messages = [msg.replace("data: ", "") for msg in messages if msg.strip() != ""]

            # Process each line
            for message in messages:
                # If the message indicates the end of the stream, return
                if message == "[DONE]":
                    return

                # Otherwise, invoke the on_chunk_received callback with the message
                await on_chunk_received(message)

    # A function to fetch the chat response with retries and timeouts
    async def fetch_chat_response_with_retry(api_key, options, retry_count):
      async with aiohttp.ClientSession() as session:
        for _ in range(retry_count):
            try:
                timeout_task = asyncio.ensure_future(total_time_timeout())
                fetch_task = asyncio.ensure_future(
                    session.post(api_url, headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}",
                    }, data=options["body"], timeout=fetch_timeout / 1000))
                _, pending = await asyncio.wait([fetch_task, timeout_task], return_when=asyncio.FIRST_COMPLETED)

                response = fetch_task.result()

                if response.status == 200:
                    return response

            except Exception as error:
                print(f"Error fetching chat: {error}")
                if retry_count == 1:
                    raise TimeoutError(f"Failed to fetch chat after {retry_count} retry attempts")

            await asyncio.sleep(retry_interval / 1000)
        raise TimeoutError("Unable to fetch chat")

    request_options = {
        "body": body,
        "fetchTimeout": fetch_timeout,
        "retryInterval": retry_interval,
    }

    response = await fetch_chat_response_with_retry(api_key, request_options, retry_count)

    # Initialize the reader
    reader = response.content

    # Process the response stream
    await process_stream(reader, on_chunk_received)


fetch_streamed_chat__name = "fetch_streamed_chat"
fetch_streamed_chat_content__name = "fetch_streamed_chat_content"
