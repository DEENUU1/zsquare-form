import requests
import os
from dotenv import load_dotenv
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


load_dotenv()

CLICKUP_APIKEY = os.getenv("CLICKUP_APIKEY")


def get_clients():
    try:
        response = requests.get(
            "https://api.clickup.com/api/v2/list/901202897167/task",
            headers={"Authorization": CLICKUP_APIKEY},
        )

        logger.info(f"Response status code: {response.status_code}")

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Error: {e}")
        return None


def check_user_exists(email: str, users: dict) -> bool:
    tasks = users.get("tasks", [])

    if not tasks:
        return True

    for task in tasks:
        custom_fields = task.get("custom_fields", [])
        if not custom_fields:
            continue

        for field in custom_fields:
            field_id = field.get("id", "")
            if field_id == "103d8d8f-210f-440d-8072-2f7c418f4918":
                email_value = field.get("value", "")

                if email_value == email:
                    return True

    return False


def validate_user(email: str) -> bool:
    clients = get_clients()
    valid_user = check_user_exists(email, clients)
    return valid_user


if __name__ == "__main__":
    import json

