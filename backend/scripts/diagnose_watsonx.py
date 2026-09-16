import os
from dotenv import load_dotenv

from ibm_watsonx_ai import (
    APIClient,
    Credentials,
)

from ibm_watsonx_ai.foundation_models import (
    ModelInference,
)


load_dotenv()


url = os.getenv("WATSONX_URL")
project_id = os.getenv("WATSONX_PROJECT_ID")
api_key = os.getenv("WATSONX_API_KEY")


print("Watsonx URL:", url)
print("Project ID loaded:", bool(project_id))
print("API key loaded:", bool(api_key))


credentials = Credentials(
    url=url,
    api_key=api_key,
)

client = APIClient(
    credentials
)


print("\nSTEP 1 - PROJECT CONNECTION")
print("--------------------------------")

try:
    client.set.default_project(
        project_id
    )

    print(
        "Project connection: SUCCESS"
    )

except Exception as exc:
    print(
        "Project connection: FAILED"
    )

    print(
        "Error type:",
        type(exc).__name__
    )

    print(
        "IBM message:",
        str(exc)
    )

    raise SystemExit


print("\nSTEP 2 - MODEL DETAILS")
print("--------------------------------")


model_id = (
    "ibm/granite-3-3-8b-instruct"
)


try:
    model = ModelInference(
        model_id=model_id,
        api_client=client,
        project_id=project_id,
    )

    details = model.get_details()

    print(
        "Model access: SUCCESS"
    )

    print(
        "Model ID:",
        details.get(
            "model_id"
        )
    )

    print(
        "Model label:",
        details.get(
            "label"
        )
    )

except Exception as exc:
    print(
        "Model access: FAILED"
    )

    print(
        "Error type:",
        type(exc).__name__
    )

    print(
        "IBM message:",
        str(exc)
    )
