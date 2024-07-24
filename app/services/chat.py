import os
from typing import Optional, Union, Tuple

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import HumanMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from config.settings import settings
import logging

from services.speech_generator import get_speech
from services.transcription import get_transcription


logger = logging.getLogger(__name__)


store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


class Chatbot:
    def __init__(self, model: str = "gpt-3.5-turbo-1106", temperature: float = 0.4):
        self.model = model
        self.temperature = temperature
        # TODO improve prompt
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant. "
                    "You may not need to use tools for every query - the user may just want to chat!",
                ),
                ("placeholder", "{messages}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

    @staticmethod
    def get_tools() -> list:
        return []

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

    def get_response(
            self,
            input_data: Union[str, bytes],
            session_id: str,
            is_audio: bool = False
    ) -> Tuple[Optional[dict], Optional[dict]]:

        if is_audio:
            transcription = get_transcription(input_data)
            if not transcription:
                return None, None
            input_message = transcription
        else:
            input_message = input_data

        user_message = {"sessionId": session_id, "message": input_message, "isBot": False}

        conversational_agent_executor = self.get_agent()

        if not conversational_agent_executor:
            return user_message, None

        try:
            response = conversational_agent_executor.invoke(
                {"messages": [HumanMessage(input_message)]},
                {"configurable": {"session_id": session_id}},
            )
            logger.info(f"Response: {response}")

            audio_file = get_speech(response["output"], session_id)
            audio_url = f"/audio/{os.path.basename(audio_file)}" if audio_file else None
            bot_message = {
                "sessionId": session_id,
                "message": response["output"],
                "input": input_message,
                "isBot": True,
                "audioUrl": audio_url
            }
            logger.info(f"Bot: {bot_message}")

            return user_message, bot_message

        except Exception as e:
            logger.error(e)
            return user_message, None


