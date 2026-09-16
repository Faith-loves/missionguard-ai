import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("WATSONX_API_KEY")
project_id = os.getenv("WATSONX_PROJECT_ID")
url = os.getenv("WATSONX_URL")

print("API key loaded:", bool(api_key))
print("Project ID loaded:", bool(project_id))
print("Watsonx URL:", url)

response = requests.post(
    "https://iam.cloud.ibm.com/identity/token",
    headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    },
    data={
        "grant_type":
            "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key,
    },
    timeout=30,
)

print("IAM status:", response.status_code)

if response.ok:
    data = response.json()
    print(
        "IBM access token received:",
        bool(data.get("access_token"))
    )
else:
    try:
        error = response.json()
        print(
            "IBM error:",
            error.get("errorMessage")
            or error.get("error_description")
            or error.get("error")
        )
    except Exception:
        print("IBM authentication failed.")
