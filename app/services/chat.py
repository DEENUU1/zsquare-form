import os
import datetime
from typing import Optional, Union, Tuple

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import HumanMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from config.database import get_db
from config.settings import settings
import logging
from schemas.message_schema import MessageInputSchema
from services.message_service import create_message, get_messages_by_form_id
from services.speech_generator import get_speech
from services.transcription import get_transcription


logger = logging.getLogger(__name__)

store = {}


def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class CurrentTimeTool(BaseTool):
    name = "current_time_tool"
    description = "Useful for when you need to answer questions about current date and time"

    def _to_args_and_kwargs(self, tool_input: Union[str, dict]) -> Tuple[Tuple, dict]:
        return (), {}

    def _run(self) -> str:
        return get_current_time()

    async def _arun(self) -> str:
        raise NotImplementedError("custom_search does not support async")


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()

        db = next(get_db())
        messages = get_messages_by_form_id(db, int(session_id))

        for message in messages:
            if message.role == "user":
                store[session_id].add_user_message(message.text)
            elif message.role == "assistant":
                store[session_id].add_ai_message(message.text)

    return store[session_id]


class Chatbot:
    def __init__(self, model: str = "gpt-3.5-turbo-1106", temperature: float = 0.4):
        self.model = model
        self.temperature = temperature
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    ## Important
                    !!!You need to answer write in Polish language!!!
                
                    you are the assistant of a "fitter" who interviews a customer about a bicycle, 
                    the "fitter" must collect the appropriate data. 
                    Ask the "fitter" one by one about the appropriate data according to the scenario given below, 
                    what data it needs to collect. 
                
                    ## Important
                    "Fitter" can also provide data in a different order, 
                    so you need to pay attention to what you are asking about
                
                    ## Data to collect
                    1. Antropometria
                    - wysokość ciała
                    - rękojeść mostka/długość tułowia
                    - długość wewnętrzna nogi
                    - szerokość ramion
                    - zasięg ramion
                    - adnotacje dotyczące antropometrii
                    2. Historia sportowana
                    3. Adnotacja dotycząca historii sportowej, zapytaj czy trzeba coś dodać
                    4. Obecne problemy z pozycja na rowerze
                    5. Adnotacja dotycząca problemów z pozycją na rowerze, zapytaj czy trzeba coś dodać
                    6. Profil otropedyczny/zdrowotny - HERE ASK ABOUT ANY MEDICAL CONDITIONS
                    7. Profil motoryczny/ocena fizjoterapeutyczna 
                    8. Adnotacje dotyczące profilu motorycznego/oceny fizjoterapeutycznej
                    9. Wymiary roweru (tutaj zapytaj krok po kroku o każdy wymiar)
                    - Wysokość siodła [Końcowe i opcjonalne]
                    - Model siodła [Końcowe i opcjonalne]
                    - Rozmiar siodła [Końcowe i opcjonalne]
                    - Nachylenie siodła [Końcowe i opcjonalne]
                    - Offset sztycy [Końcowe i opcjonalne]
                    - Odsunięcie siodła od osi suportu [Końcowe i opcjonalne]
                    - Końcówka siodła od środka kierownicy [Końcowe i opcjonalne]
                    - Końcówka siodła do manetki [Końcowe i opcjonalne]
                    - Różnica wysokości (DROP) [Końcowe i opcjonalne]
                    - Mostek długość / kąt [Końcowe i opcjonalne]
                    - Szerokość kierownicy [Końcowe i opcjonalne]
                    - Model kierownicy [Końcowe i opcjonalne]
                    - Wysokość podkładek [Końcowe i opcjonalne]
                    - Długość korby [Końcowe i opcjonalne]
                    - Kąt manetek (kierownica / dźwignia) [Końcowe i opcjonalne]
                    10. Adnotacje dotyczące wymiarów roweru
                    """
                ),
                ("placeholder", "{messages}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

    @staticmethod
    def get_tools() -> list:
        return [CurrentTimeTool()]

    def get_openai_chat(self) -> Optional[ChatOpenAI]:
        try:
            return ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                openai_api_key=settings.OPENAI_APIKEY,
            )
        except Exception as e:
            logger.error(e)
            return None

    def get_agent(self) -> Optional[RunnableWithMessageHistory]:
        try:
            chat = self.get_openai_chat()
            if not chat:
                logger.error("Failed to get OpenAI chat instance")
                return None

            tools = self.get_tools()

            agent = create_tool_calling_agent(chat, tools, self.prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            return RunnableWithMessageHistory(
                agent_executor,
                get_session_history,
                input_messages_key="messages",
                output_messages_key="output",
            )
        except Exception as e:
            logger.error(e)
            return None

    async def get_response(
            self, input_data: Union[str, bytes], form_id: int, is_audio: bool = False
    ) -> Tuple[Optional[dict], Optional[dict]]:
        if is_audio:
            transcription = get_transcription(input_data)
            if not transcription:
                return None, None
            input_message = transcription
        else:
            input_message = input_data

        user_message = {"sessionId": str(form_id), "message": input_message, "isBot": False}
        conversational_agent_executor = self.get_agent()

        if not conversational_agent_executor:
            return user_message, None

        try:
            response = conversational_agent_executor.invoke(
                {"messages": [HumanMessage(input_message)]},
                {"configurable": {"session_id": str(form_id)}},
            )
            logger.info(f"Response: {response}")

            audio_file = get_speech(response["output"], str(form_id))
            audio_url = f"/static/audio/{os.path.basename(audio_file)}" if audio_file else None
            bot_message = {
                "sessionId": str(form_id),
                "message": response["output"],
                "input": input_message,
                "isBot": True,
                "audioUrl": audio_url,
            }

            create_message(next(get_db()), MessageInputSchema(
                role="user",
                text=input_message,
                form_id=int(form_id),
            ))

            create_message(next(get_db()), MessageInputSchema(
                role="assistant",
                text=response["output"],
                form_id=int(form_id),
            ))

            logger.info(f"Bot: {bot_message}")

            return user_message, bot_message

        except Exception as e:
            logger.error(e)
            return user_message, None
