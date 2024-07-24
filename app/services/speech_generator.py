from typing import Optional

from openai import OpenAI
import logging
from config.settings import settings
from utils.save_temp import save_temp_file

logger = logging.getLogger(__name__)


def get_speech(text: str, session_id: str) -> Optional[str]:
    logger.info("Getting speech")

    try:
        client = OpenAI(api_key=settings.OPENAI_APIKEY)
        response = client.audio.speech.create(
            model="tts-1",
            voice="shimmer",
            response_format="mp3",
            input=text,
        )

        saved_file = save_temp_file(response.content, session_id)

        logger.info("Speech generated successfully")

        return saved_file

    except Exception as e:
        logger.error(e)
        return None
