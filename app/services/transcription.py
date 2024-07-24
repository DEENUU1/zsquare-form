from typing import Optional

from openai import OpenAI
from openai.types.audio import Transcription

from config.settings import settings
import logging


logger = logging.getLogger(__name__)


def get_transcription(file_path: str) -> Optional[Transcription]:
    logger.info("Getting transcription")

    try:
        client = OpenAI(api_key=settings.OPENAI_APIKEY)
        audio_file = open(file_path, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
        logger.info(f"Transcription: {transcription}")
        return transcription
    except Exception as e:
        logger.error(e)
        return None
