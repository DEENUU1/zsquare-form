from typing import Optional

import requests
import os
from dotenv import load_dotenv
import logging


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


def check_user_exists(email: str, users: dict) -> tuple[bool, str]:
    tasks = users.get("tasks", [])

    if not tasks:
        return False, ""

    for task in tasks:
        task_id = task.get("id", "")

        custom_fields = task.get("custom_fields", [])
        if not custom_fields:
            continue

        for field in custom_fields:
            field_id = field.get("id", "")
            if field_id == "103d8d8f-210f-440d-8072-2f7c418f4918":
                email_value = field.get("value", "")

                if email_value == email:
                    return True, task_id

    return False, ""


def validate_user(email: str) -> tuple[bool, str]:
    clients = get_clients()
    valid_user, user_id = check_user_exists(email, clients)
    logger.info(f"User exists: {valid_user}")
    logger.info(f"User ID: {user_id}")
    return valid_user, user_id
