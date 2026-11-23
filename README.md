# Weather Application

A command-line weather assistant powered by Groq and OpenWeatherMap.

## Setup

1. Create a `.env` file in the project directory with your API keys:

   ```text
   GROQ_API_KEY=your_groq_api_key
   WEATHER_API_KEY=your_openweathermap_api_key
   ```

2. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Run the application:

   ```powershell
   python main.py
   ```

The application prompts for a city name and prints its current weather.
