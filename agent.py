# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import urllib.parse
import urllib.request
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
# from google.adk.tools.load_memory_tool import LoadMemoryTool
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

def get_weather(city: str) -> dict:
    """Gets the current weather for a given city.

    Args:
        city: The city name in English (e.g., 'New York', 'Seoul', 'London').
    """
    encoded_city = urllib.parse.quote(city.strip())
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=1&language=en&format=json"
    
    try:
        req = urllib.request.Request(geo_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            geo_data = json.loads(response.read().decode())
            results = geo_data.get("results")
            if not results:
                return {"status": "error", "error_message": f"City '{city}' not found."}
            
            location = results[0]
            lat = location.get("latitude")
            lon = location.get("longitude")
            name = location.get("name")
            country = location.get("country")
            
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m"
        
        req = urllib.request.Request(weather_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            weather_data = json.loads(response.read().decode())
            current = weather_data.get("current")
            if not current:
                return {"status": "error", "error_message": "Could not parse weather data."}
            
            temp = current.get("temperature_2m")
            humidity = current.get("relative_humidity_2m")
            apparent_temp = current.get("apparent_temperature")
            wind_speed = current.get("wind_speed_10m")
            
            report = (
                f"The current weather in {name}, {country} is: "
                f"Temperature: {temp}°C (Apparent: {apparent_temp}°C), "
                f"Humidity: {humidity}%, "
                f"Wind Speed: {wind_speed} km/h."
            )
            return {"status": "success", "report": report}
            
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Could not retrieve weather for city '{city}': {str(e)}",
        }


def get_current_time(timezone: str) -> dict:
    """Gets the current time for a given IANA timezone.

    Args:
        timezone: The IANA timezone identifier (e.g., 'America/New_York', 'Asia/Seoul', 'Europe/London').
    """
    encoded_tz = urllib.parse.quote(timezone.strip())
    url = f"https://timeapi.io/api/Time/current/zone?timeZone={encoded_tz}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            report = f"The current time in {timezone} is {data.get('dateTime')} ({data.get('dayOfWeek')})."
            return {"status": "success", "report": report}
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Could not retrieve time for timezone '{timezone}': {str(e)}",
        }

# https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/adk-quickstart#manage-memories
async def add_session_to_memory_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None

# https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/adk-quickstart?hl=ko#memory-generation-callback
async def generate_memories_callback(callback_context: CallbackContext):
    # Option 1 (Recommended): Send events to Memory Bank for memory generation,
    # which is ideal for incremental processing of events.
    await callback_context.add_events_to_memory(
      events=callback_context.session.events[-5:-1])

    # Option 2: Send the full session to Memory Bank for memory generation.
    # It's recommended to only call this at the end of a session to minimize
    # how many times a single event is re-processed.
    # await callback_context.add_session_to_memory()

    return None

# https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/adk-quickstart?hl=ko#define_a_memory_retrieval_tool
memory_retrieval_tools = [
  # Option 1: Retrieve memories at the start of every turn.
  PreloadMemoryTool(),
  # Option 2: Retrieve memories via tool calls. The model will only call this tool
  # when it decides that memories are necessary to respond to the user query.
#   LoadMemoryTool()
]


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-3.5-flash",
    description="Agent to answer questions about the time and weather in a city.",
    instruction="You are a helpful agent who can answer user questions about the time and weather in a city.",
    tools=[get_weather, get_current_time] + memory_retrieval_tools
)