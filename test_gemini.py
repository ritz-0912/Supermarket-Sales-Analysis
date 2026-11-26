
from google import genai
import tomllib

# Read API key securely
with open(".streamlit/secrets.toml", "rb") as file:
    secrets = tomllib.load(file)

# Connect to Gemini
client = genai.Client(
    api_key=secrets["GEMINI_API_KEY"]
)

# Send a test prompt
response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Reply exactly: Gemini connection successful!"
)

print(response.text)
