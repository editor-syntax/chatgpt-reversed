# OpenAI API Client

This package provides a Python client for the OpenAI API, which allows you to use AI models to generate text, answer questions, and more. This client currently supports version 1 of the OpenAI API.

## It is kinda reversed, so yeah

## Generating Text

To generate text with the OpenAI API, you can use the generate method of the `V1` class. This method takes a prompt argument, which is a string containing the starting text that the AI model will use to generate more text. Here's an example:

```py
response = gpt.generate(prompt="Once upon a time")
print(response.text)
```

This will generate a new text continuation starting from the prompt "Once upon a time". The generated text will be returned as a string in the `text` attribute of the response.

## Asking Questions

You can also use the OpenAI API to answer questions using the `search` method of the `V1` class. This method takes a query argument, which is a string containing the question that you want to ask. Here's an example:

```py
response = gpt.search(query="What is the meaning of life?")
print(response.answers)
```

## Customizing the API Client

The `V1` class constructor also accepts several optional arguments that allow you to customize the behavior of the OpenAI API client. For example, you can set the `engine` parameter to specify which AI model to use, or set the `max_tokens` parameter to control the maximum length of the generated text. Here's an example:

```py
gpt = V1(api_key, engine="davinci", max_tokens=50)
response = gpt.generate(prompt="Once upon a time")
print(response.text)
```
