from typing import Optional

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


def update_custom_value(task_id: str, field_id: str, value: str) -> None:
    try:
        response = requests.post(
            f"https://api.clickup.com/api/v2/task/{task_id}/field/{field_id}",
            headers={
                "Content-Type": "application/json",
                "Authorization": CLICKUP_APIKEY
            },
            json={
                "value": value
            }
        )

        logger.info(f"Response status code: {response.status_code}")
        logger.info(response.json())
        response.raise_for_status()

        return

    except Exception as e:
        logger.error(e)
        return None


def update_user(
        user_id: str,
        birth_date: Optional[str],
        location: Optional[str],
        client_id: int
) -> None:
    update_custom_value(user_id, "26333d2a-fad7-4fb3-bace-d3d6f460239a", birth_date)
    update_custom_value(user_id, "d3341242-bdf9-467e-9672-5d4193e683e2", location)
    update_custom_value(user_id, "40da14a4-2887-4929-8996-51da3e59d5d1", str(client_id))
    return


def validate_user(email: str) -> tuple[bool, str]:
    clients = get_clients()
    valid_user, user_id = check_user_exists(email, clients)
    return valid_user, user_id


def create_clickup_form(
        client_id: int,
        created_at: str,
        form_id: int,
        updated_at: str,
        bike: Optional[str] = None,
        boots: Optional[str] = None,
        insoles: Optional[str] = None,
        other_bikes: Optional[str] = None,
        pedals: Optional[str] = None,
        sport_annotation: Optional[str] = None,
        sport_history: Optional[str] = None,
        tool_annotation: Optional[str] = None,
) -> None:
    try:
        response = requests.post(
            "https://api.clickup.com/api/v2/list/901202897723/task",
            headers={
                "Content-Type": "application/json",
                "Authorization": CLICKUP_APIKEY
            },
            json={
                "name": f"{form_id}-{client_id}-{str(created_at)[:10]}",
                "custom_fields": [
                    {
                        "id": "369fc13e-0219-45b6-bac8-0fd08fdfceb1",
                        "value": bike
                    },
                    {
                        "id": "3b309b11-adc6-47a6-8344-dd8e5d4f2acd",
                        "value": boots
                    },
                    {
                        "id": "40da14a4-2887-4929-8996-51da3e59d5d1",
                        "value": client_id
                    },
                    {
                        "id": "b69113b9-a887-4a92-b27a-e9b4bf293d23",
                        "value": created_at
                    },
                    {
                        "id": "01446bfb-ccc4-420a-8b3c-0a83e0ce8616",
                        "value": form_id
                    },
                    {
                        "id": "3ac2af4a-3feb-4063-b941-1d61860a1b74",
                        "value": insoles
                    },
                    {
                        "id": "4708d541-59f1-4316-9a56-f1c8c05cb4a3",
                        "value": other_bikes
                    },
                    {
                        "id": "60033b27-24ef-487d-bfce-590682103fa6",
                        "value": pedals
                    },
                    {
                        "id": "6c7ddc6e-875a-4281-9429-d5d17dcaab71",
                        "value": sport_annotation
                    },
                    {
                        "id": "08beb4c4-9f37-43e7-8eef-5092ed44d4c9",
                        "value": sport_history
                    },
                    {
                        "id": "41126927-a771-4575-81b7-a27a4e8a3cc6",
                        "value": tool_annotation
                    },
                    {
                        "id": "88c4e4b1-206d-4872-8f82-6fda1a3ddd7e",
                        "value": updated_at
                    }
                ]
            }
        )

        logger.info(f"Response status code: {response.status_code}")
        logger.info(response.json())
        response.raise_for_status()

        return

    except Exception as e:
        logger.error(e)
        return None
