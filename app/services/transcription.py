from io import BytesIO
from typing import Optional, Union

from openai import OpenAI
from config.settings import settings
import logging


logger = logging.getLogger(__name__)


def get_transcription(audio_data: Union[str, bytes]) -> Optional[str]:
    logger.info("Getting transcription")

    try:
        client = OpenAI(api_key=settings.OPENAI_APIKEY)

        if isinstance(audio_data, str):
            with open(audio_data, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
        elif isinstance(audio_data, bytes):
            audio_file = BytesIO(audio_data)
            audio_file.name = "audio.webm"
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            print(transcription)
        else:
            raise ValueError("Invalid input type. Expected str (file path) or bytes.")

        logger.info(f"Transcription: {transcription}")
        return str(transcription)
    except Exception as e:
        logger.error(f"Error in transcription: {str(e)}")
        return None
