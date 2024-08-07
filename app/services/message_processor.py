import logging
import os
from typing import Any, Optional, List

from langchain.chains import TransformChain
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import chain
from langchain_openai import ChatOpenAI
from config.settings import settings
from schemas.message_schema import MessageOutputSchema
from schemas.form_schema import FormOutputSchema
from openai import OpenAI


os.environ["OPENAI_API_KEY"] = settings.OPENAI_APIKEY

logger = logging.getLogger(__name__)


class Anthropometry(BaseModel):
    body_height: float = Field(..., description="Wysokość ciała w centymetrach")
    sternum_handle: float = Field(..., description="Długość rękojeści mostka / długość tułowia w centymetrach")
    inner_leg_length: float = Field(..., description="Długość wewnętrzna nogi w centymetrach")
    shoulder_width: float = Field(..., description="Szerokość ramion w centymetrach")
    arm_span: float = Field(..., description="Zasięg ramion w centymetrach")


class BicycleDimensions(BaseModel):
    saddle_height: Optional[float] = Field(None, description="Wysokość siodła w centymetrach")
    saddle_model: Optional[str] = Field(None, description="Model siodła")
    saddle_size: Optional[str] = Field(None, description="Rozmiar siodła")
    saddle_tilt: Optional[float] = Field(None, description="Nachylenie siodła w stopniach")
    seatpost_offset: Optional[float] = Field(None, description="Offset sztycy w milimetrach")
    saddle_to_bottom_bracket: Optional[float] = Field(
        None, description="Odsunięcie siodła od osi suportu w centymetrach"
    )
    saddle_to_handlebar_center: Optional[float] = Field(
        None, description="Odległość końcówki siodła od środka kierownicy w centymetrach"
    )
    saddle_to_shifter: Optional[float] = Field(
        None, description="Odległość końcówki siodła do manetki w centymetrach"
    )
    height_difference: Optional[float] = Field(None, description="Różnica wysokości (DROP) w centymetrach")
    stem_length: Optional[float] = Field(None, description="Długość mostka w milimetrach")
    stem_angle: Optional[float] = Field(None, description="Kąt mostka w stopniach")
    handlebar_width: Optional[float] = Field(None, description="Szerokość kierownicy w centymetrach")
    handlebar_model: Optional[str] = Field(None, description="Model kierownicy")
    spacer_height: Optional[float] = Field(None, description="Wysokość podkładek w milimetrach")
    crank_length: Optional[float] = Field(None, description="Długość korby w milimetrach")
    shifter_angle: Optional[float] = Field(None, description="Kąt manetek (kierownica / dźwignia) w stopniach")


class ConversationInformation(BaseModel):
    anthropometry: Anthropometry = Field(
        ...,
        description="Antropometria zawierająca szczegółowe pomiary",
    )
    anthropometry_notes: str = Field(..., description="Adnotacje dotyczące antropometrii")
    sports_history: str = Field(..., description="Historia sportowa")
    sports_history_notes: str = Field(..., description="Adnotacja dotycząca historii sportowej")
    position_problems: str = Field(..., description="Obecne problemy z pozycją na rowerze")
    position_problems_notes: str = Field(..., description="Adnotacja dotycząca problemów z pozycją na rowerze")
    orthopedic_profile: str = Field(..., description="Profil ortopedyczny/zdrowotny")
    motor_profile: str = Field(..., description="Profil motoryczny/ocena fizjoterapeutyczna")
    motor_profile_notes: str = Field(
        ..., description="Adnotacje dotyczące profilu motorycznego/oceny fizjoterapeutycznej"
    )
    bicycle_dimensions: BicycleDimensions = Field(..., description="Szczegółowe wymiary roweru")
    bicycle_dimensions_notes: str = Field(..., description="Adnotacje dotyczące wymiarów roweru")


parser = JsonOutputParser(pydantic_object=ConversationInformation)


def load_messages(inputs: dict) -> dict:
    return {"messages": inputs["message_dict"]}


load_message_chain = TransformChain(
    input_variables=["message_dict"],
    output_variables=["messages"],
    transform=load_messages
)


@chain
def conversation_model(inputs: dict) -> str | list[str | dict[Any, Any]]:
    model: ChatOpenAI = ChatOpenAI(
        temperature=0.5,
        model="gpt-4",
        max_tokens=1024,
    )
    msg = model.invoke(
        [
            HumanMessage(
                content=[
                    {"type": "text", "text": inputs["prompt"]},
                    {"type": "text", "text": parser.get_format_instructions()},
                    {"type": "text", "text": str(inputs['messages'])},
                ]
            )
        ]
    )
    logger.info(f"Model response: {msg.content}")
    return msg.content


def convert_messages_to_dict(messages: List[MessageOutputSchema]) -> list[dict]:
    conversation = []

    for message in messages:
        conversation.append(
            {"role": message.role, "content": message.text}
        )

    return conversation


def get_conversation_information(messages: list[dict]) -> Optional[dict]:
    vision_prompt = """
    Process conversation and return structured output based on the given schema.
    Collect the following data:
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
    6. Profil otropedyczny/zdrowotny - zapytaj o wszelkie schorzenia
    7. Profil motoryczny/ocena fizjoterapeutyczna 
    8. Adnotacje dotyczące profilu motorycznego/oceny fizjoterapeutycznej
    9. Wymiary roweru (zapytaj krok po kroku o każdy wymiar)
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
    conversation_chain = load_message_chain | conversation_model | parser

    try:
        return conversation_chain.invoke(
            {"message_dict": messages, "prompt": vision_prompt}
        )
    except OutputParserException as e:
        logger.error(f"Failed to parse the output (OutputParserException): {e}")
        return None

    except Exception as e:
        logger.error(f"Failed to get conversation information (Unknown Exception): {e}")
        return None


def generate_session_summary(form_data: FormOutputSchema, conversation_structured_output: Any) -> Optional[str]:
    if not settings.OPENAI_APIKEY:
        raise ValueError("OPENAI_APIKEY is not set")

    prompt = f"""
    ### !IMPORTANT!
    Your answer must be in polish. Return only the summary of changes nothing more.
    Based on the provided data from the fitter-chatbot conversation and data from the user form, 
    create a summary of changes introduced in the bike settings.

    # Rules
    - Include only data based on client data and conversation data.
    - Do not include any additional information that is not related to the bike settings changes.
    - If there are no changes, do not include any information about it.
    - Return only the summary of changes nothing more.
    
    
    ### Client data
    {form_data}

    ### Conversation data
    {conversation_structured_output}

    ### Example 1
    wobec pozycji wyjściowej siodełko klienta zostało obniżone, bez kompensacyjnej zmiany przesunięcia przód-tył.
    Kąt pochylenia został zachowany, sam model siodełka Bontrager Verse COMP, w obiektywne cenie na macie 
    tensometrycznej spełnia swoją rolę i podpiera kości kulszowe w akceptowalnych wartościach sił.
    Dokonano też próby obiektywnej na siodełku w szerokości 152 mm model PRO Stealth, które wykazywało większą 
    niestabilność miednicy i zwiększyło wartości sił podporu.
    Obniżona pozycja na siodełku zapewnia mniejszy roking miednicy, stabilniejszą pozycję w siodle i mniejsze 
    wartości ciśnienia w podporze.
    Pozycja mostka i szerokość kierownicy bez zmian.
    Wobec pozycji wyjściowej podkładki zostały obniżone spod mostka o 20 mm w dół.
    Powyższe pozwoliło osiągnąć swobodniejszy podpór w obręczy barkowej i dać przestrzeń dość długim kończyną
    górnym klienta.
    W trakcie sesji dokonano wyboru nowego obuwia i przejścia z systemu SPD SL na system SPD MTB.
    Wybrane buty to Lake MX238 w rozmiarze 44,5 regular. Bloki zostały ustawione tożsamo to poprzednich butów. 
    Zarówno w poprzednich butach jak i nowych wobec pozycji wyjściowej do butów MTB nie zdecydowałem się 
    dokładać 3 mm dystansu tak jak miało to miejsce wcześniej. Klient został poinformowany o tym fakcie 
    i postawiona została argumentacja natury fittingowej.
    Polecam regularne ćwiczenia redukujące ustawienie łokci w delikatnym zgięciu, poprzez zginanie łokcia w dół do 
    siebie, a następnie stopniowe odkładanie dłoni na manetkę.
    Na prośbę klienta skontrolowałem również i zarekomendowałem odpowiedni kąt ustawienia przystawki 
    czasowej.
    Klient w dwóch parach obuwia z którymi się zgłosił miał wkładki Bontrager w kolorze żółtym, których zasadność 
    zastosowania wobec budowa anatomicznej stopy potwierdzam.
    Na ten moment do nowych butów Lake skorzystałem z krócej dociętych wkładek Bontrager. 
    W przyszłości jeżeli pozostawałaby jakaś pusta przestrzeń w bucie, zapraszam do kontaktu i ewentualnego 
    wykonania wkładek custom.

    ### Example 2
    W oparciu o zgłoszony problem napięć i bólu okolic mięśnia triceps i miesienia deltoideus akton boczny i tylny
    przeprowadziłem szereg prób mających na celu zniesienia nadmiernego napięcia mięśniowego.
    Finalnie na drodze testowania pozycji zdecydowałem się obniżyć pozycję kierownicy odwracając kąt mostka i
    obniżając podkładkę w dół o 10 mm wobec pozycji wyjściowej.
    Test szerszej kierownicy i wyższej pozycji pogarszały wrażenia z napięć wyżej wymienionych okolic.
    Siodełko przesunięte zostało o 6 mm wstecz celem przeniesienia środka ciężkości do tyłu. 
    W trakcie sesji zostały też wykonane indywidulane wkładki Foot Ballance 100% Balance do butów marki Shimano.

    ### Example 3
    Antropometria: wzrost 179 cm, wysokość rękojeści mostka 146 cm, przekork 86,5 cm, szerokość ramion 40 cm, 
    zasięg kończyn górnych 179 cm 
    Podsumowanie: 
    W oparciu o wywiad, ocenę funkcjonalną i antropometryczną przeprowadziłem sesję bikefittigu roweru Kross
    Esker 6.0 w rozmiarze L. 
    Wobec pozycji wyjściowej siodełko zostało obniżone o 7 mm, zwiększony został kąt pochylenia do -2 stopni.
    Pozycja kierownicy w kwestii rotacji bez zmian.
    Mostek wydłużony został o 1 cm.
    W trakcie sesji zmienione zostały zużyte pedały i bloki SPD 520, na pedały SPD 540.
    Dzięki powyższemu mniejszy luz roboczy utrzymuje lewą nogę w osiowości cyklu pedałowania, zimniejsze jest
    rotacja do wew. podudzia. 
    Klient ma ćwiczyć i regularnie przechodzić do jazdy w stójce, regularnie zmieniać chwyty, kontrolować łokcie
    w delikatnym zgięciu. 
    Niezależnie należałoby wzmocnić treningiem siłowym obręcz barkową i plecy.
    """

    try:
        client = OpenAI(api_key=settings.OPENAI_APIKEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
            ],
        )
        if not response:
            return None
        return response.choices[0].message.content

    except Exception as e:
        logger.error(e)
        return None
