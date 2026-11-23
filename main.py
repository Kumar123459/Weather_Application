
from dotenv import load_dotenv
from groq import Groq, GroqError
import os
import json
import requests
from requests import RequestException
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")

if not groq_api_key:
    raise RuntimeError("GROQ_API_KEY is missing. Add it to the .env file.")
if not weather_api_key:
    raise RuntimeError("WEATHER_API_KEY is missing. Add it to the .env file.")

client = Groq(api_key=groq_api_key)

def get_weather(location):
    url = "https://api.openweathermap.org/data/2.5/weather"
    try:
        response = requests.get(
            url,
            params={
                "q": location,
                "units": "metric",
                "appid": weather_api_key,
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except RequestException as exc:
        return json.dumps({
            "error": f"Unable to fetch weather data: {exc}"
        })

    if data.get("cod") == 200:
        return json.dumps({
            "location": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        })

    message = data.get("message", "Something went wrong.")
    return json.dumps({"error": message})

tools = [
  {
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "Get current weather for a city",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "City name like Mumbai, London"
            }
            },
      "required": ["location"]
           }
       }
   }
]

llm_messages = [
  {
    "role": "system",
    "content": "You are a weather assistant. Use get_weather function when asked about weather."
  }
]

location = input("Enter city name: ").strip()
if not location:
    raise ValueError("City name cannot be empty")

llm_messages.append({
  "role": "user",
  "content": f"What's the weather in {location}?"
})

try:
    response = client.chat.completions.create(
      model="openai/gpt-oss-120b",
      messages=llm_messages,
      tools=tools,
      tool_choice="auto"
    )

    response_message = response.choices[0].message

    if response_message.tool_calls:
      tool_call = response_message.tool_calls[0]
      arguments = json.loads(tool_call.function.arguments)
      location = arguments.get("location", "").strip()
      if not location:
          raise ValueError("The model did not provide a city name.")

      weather_data = get_weather(location)

      llm_messages.append(response_message)
      llm_messages.append({
          "role": "tool",
          "tool_call_id": tool_call.id,
          "content": weather_data
      })

      final_response = client.chat.completions.create(
          messages=llm_messages,
          model="openai/gpt-oss-120b",
          tools=tools,
          tool_choice="auto"
      )
      print(final_response.choices[0].message.content)
    elif response_message.content:
      print(response_message.content)
    else:
      print("The weather assistant did not return a response.")
except GroqError as exc:
    print(f"Error: {exc}")