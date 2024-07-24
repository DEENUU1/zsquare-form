from datetime import datetime
import logging


logger = logging.getLogger(__name__)


def save_temp_file(audio_data: bytes, session_id: str) -> str:
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    temp_file_path = f"static/audio/temp_audio_{session_id}_{current_time}.webm"

    try:
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(audio_data)

    except Exception as e:
        logger.error(f"Error saving temporary file: {e}")

    return temp_file_path
