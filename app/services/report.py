import base64

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
import io
from reportlab.pdfbase.ttfonts import TTFont
from typing import List, Any
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from sqlalchemy.orm import Session
from services.client_service import get_client_by_id
from services.form_data_service import get_form_by_id
from services.message_service import get_messages_by_form_id
from schemas.client_schema import ClientOutputSchema
from schemas.form_schema import FormOutputSchema
from schemas.report_schema import ReportInputSchema
from utils.filename_generator import generate_filename
from services.report_service import create_report, get_report_exists_by_form_id, update_report_content
from utils.current_date import get_current_date


class Report:
    @staticmethod
    def add_spaces(elements, height=7):
        elements.append(Spacer(1, height))

    @staticmethod
    def add_table(elements: List, table) -> None:
        elements.append(table)

    @staticmethod
    def add_text(elements: List, style, text: str, alignment=TA_LEFT) -> None:
        para = Paragraph(text, style)
        para.hAlign = alignment
        elements.append(para)

    @staticmethod
    def get_paragraph_style() -> Any:
        paragraph_style = ParagraphStyle('services_description')
        paragraph_style.fontName = 'Abhaya'
        paragraph_style.fontSize = 8
        paragraph_style.bold = False
        return paragraph_style

    @staticmethod
    def get_header_style() -> Any:
        header_style = ParagraphStyle('header')
        header_style.fontName = 'Abhaya'
        header_style.fontSize = 10
        header_style.bold = True
        return header_style

    @staticmethod
    def get_sub_header_style() -> Any:
        sub_header_style = ParagraphStyle('sub_header')
        sub_header_style.fontName = 'Abhaya'
        sub_header_style.fontSize = 8
        sub_header_style.bold = True
        return sub_header_style

    @staticmethod
    def get_title_style() -> Any:
        title_style = ParagraphStyle('title')
        title_style.fontName = 'Abhaya'
        title_style.fontSize = 30
        title_style.bold = True
        title_style.alignment = TA_CENTER
        return title_style

    @staticmethod
    def get_sub_title_style() -> Any:
        sub_title_style = ParagraphStyle('sub_title')
        sub_title_style.fontName = 'Abhaya'
        sub_title_style.fontSize = 16
        sub_title_style.bold = True
        sub_title_style.alignment = TA_CENTER
        return sub_title_style

    @staticmethod
    def get_table_style() -> Any:
        return TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Abhaya', 8),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('WORDWRAP', (0, 0), (-1, -1), True),
        ])

    @staticmethod
    def wrap_long_text(text, max_width):
        return Paragraph(text, ParagraphStyle('wrapped', wordWrap='CJK', fontSize=8, fontName='Abhaya'))

    @staticmethod
    def merge_position_problem(form_data: FormOutputSchema, structured_output: dict) -> str:
        client_data = form_data.position_problem
        fitter_data = structured_output.get("position_problems")

        return f"{client_data}. {fitter_data}."

    @staticmethod
    def merge_annotation_position_problem(form_data: FormOutputSchema, structured_output: dict) -> str:
        client_data = form_data.adnotation_position_problem
        fitter_data = structured_output.get("position_problems_notes")

        return f"{client_data}. {fitter_data}."

    def generate_pdf_report(
            self,
            client_data: ClientOutputSchema,
            form_data: FormOutputSchema,
            structured_output: dict,
            summary: str,
    ) -> io.BytesIO:
        style = self.get_paragraph_style()
        header_style = self.get_header_style()
        title_style = self.get_title_style()
        sub_title_style = self.get_sub_title_style()
        sub_headers_style = self.get_sub_header_style()
        table_style = self.get_table_style()

        current_date = get_current_date()

        merged_position_problems = self.merge_position_problem(form_data, structured_output)
        merged_position_problems_annotation = self.merge_annotation_position_problem(form_data, structured_output)

        col_widths = [3 * inch, 3 * inch]

        buffer = io.BytesIO()
        pdfmetrics.registerFont(TTFont("Abhaya", "Abhaya.ttf"))
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        self.add_text(elements, title_style, "Veloart", alignment=TA_CENTER)
        self.add_spaces(elements, height=20)

        self.add_text(elements, sub_title_style, "Raport podsumowujący w ramach BIKEFITTINGU w Veloart:", alignment=TA_LEFT)
        self.add_spaces(elements, height=20)

        self.add_text(elements, header_style, f"Dane wywiadu i bikefittingu: {current_date}")
        self.add_spaces(elements)

        self.add_text(elements, sub_headers_style, "Dane personalne")

        personal_data = [
            ["Imię i nazwisko", self.wrap_long_text(str(client_data.full_name), col_widths[1])],
            ["Rok urodzenia", self.wrap_long_text(str(client_data.birth_date), col_widths[1])],
            ["Miejsce zamieszkania:", self.wrap_long_text(str(client_data.location), col_widths[1])],
            ["Telefon:", self.wrap_long_text(str(client_data.phone), col_widths[1])],
            ["Adres email:", self.wrap_long_text(str(client_data.email), col_widths[1])],
        ]
        personal_data_table = Table(personal_data, colWidths=col_widths)
        personal_data_table.setStyle(table_style)

        self.add_table(elements, personal_data_table)
        self.add_spaces(elements)

        self.add_text(elements, sub_headers_style, "Antropometria")

        antropometry_data = [
            ["Wysokość ciała", str(structured_output.get("anthropometry", {}).get("body_height", ""))],
            ["Rękojeść mostka/Długość tułowia", str(structured_output.get("anthropometry", {}).get("sternum_handle", ""))],
            ["Długość wew. nogi:", str(structured_output.get("anthropometry", {}).get("inner_leg_length", ""))],
            ["Szerokość ramion:", str(structured_output.get("anthropometry", {}).get("'shoulder_width", ""))],
            ["Zasięg ramion: ", str(structured_output.get("anthropometry", {}).get("arm_span", ""))],
            ["Adnotacje", str(structured_output.get("anthropometry_notes", ""))],
        ]
        antropometry_data_table = Table(antropometry_data, colWidths=col_widths)
        antropometry_data_table.setStyle(table_style)

        self.add_table(elements, antropometry_data_table)
        self.add_spaces(elements)

        self.add_text(elements, sub_headers_style, "Rower sprzęt")

        bike_data = [
            ["Marka/model/rozmiar", form_data.bike if form_data.bike else ""],
            ["Buty/rozmiar", form_data.boots if form_data.boots else ""],
            ["Wkładki", form_data.insoles if form_data.insoles else ""],
            ["Pedały", form_data.pedals if form_data.pedals else ""],
            ["Inne rowery", form_data.other_bikes if form_data.other_bikes else ""],
            ["Adnotacje", form_data.tool_annotation if form_data.tool_annotation else ""],
        ]
        bike_table = Table(bike_data, colWidths=col_widths)
        bike_table.setStyle(table_style)

        self.add_table(elements, bike_table)
        self.add_spaces(elements)

        self.add_text(elements, sub_headers_style, "Historia sportowa/Profil kolarski")

        sport_history_data = [
            [
                "Liczba lat uprawiania kolarstwa/Historia startów, wyniki/Czas treningu w tygodniu/Standardowa jazda długość, charakter/",
                form_data.sport_history if form_data.sport_history else ""
            ],
            [
                "Pomiar mocy, kadencji/Cele sportowe/Inne aktywności sportowe/",
                form_data.sport_annotation if form_data.sport_annotation else ""
            ],
        ]
        sport_history_table = Table(sport_history_data, colWidths=col_widths)
        sport_history_table.setStyle(table_style)

        self.add_table(elements, sport_history_table)
        self.add_spaces(elements)

        self.add_text(elements, sub_headers_style, "Obecne problemy z pozycją na rowerze")
        position_problem_data = [
            ["Obecne problemy", merged_position_problems],
            ["Adnotacje", merged_position_problems_annotation]
        ]
        position_problem_table = Table(position_problem_data, colWidths=col_widths)
        position_problem_table.setStyle(table_style)

        self.add_table(elements, position_problem_table)
        self.add_spaces(elements)

        self.add_text(elements, sub_headers_style, "Profil ortopedyczny/zdrowotny")
        self.add_text(elements, style, str(structured_output.get("orthopedic_profile", "")))

        doc.build(elements)
        buffer.seek(0)

        return buffer


def generate_report(db: Session, form_id: int = 1) -> None:
    form_data = get_form_by_id(db, form_id)
    client_data = get_client_by_id(db, form_data.client_id)
    messages = get_messages_by_form_id(db, form_id)

    filename = generate_filename(form_data, client_data)

    # structured_output = get_conversation_information(messages)
    # print(structured_output)
    structured_output = {
        'anthropometry': {
            'body_height': 190,
            'sternum_handle': 20,
            'inner_leg_length': 30,
            'shoulder_width': 120,
            'arm_span': 13
        },
        'anthropometry_notes': 'nie',
        'sports_history': 'nie',
        'sports_history_notes': '',
        'position_problems': 'nie',
        'position_problems_notes': 'nie',
        'orthopedic_profile': 'nie',
        'motor_profile': 'nie',
        'motor_profile_notes': 'nie',
        'bicycle_dimensions': {
            'saddle_height': 12,
            'saddle_model': 'shimano',
            'saddle_size': '30cm',
            'saddle_tilt': 12,
            'seatpost_offset': 11,
            'saddle_to_bottom_bracket': 111,
            'saddle_to_handlebar_center': 21,
            'saddle_to_shifter': 24,
            'height_difference': 90,
            'stem_length': 35,
            'stem_angle': None,
            'handlebar_width': 120,
            'handlebar_model': 'shimano xyz',
            'spacer_height': 97,
            'crank_length': 71,
            'shifter_angle': 18
        },
        'bicycle_dimensions_notes': 'nie'
    }
    # summary = generate_session_summary(form_data, structured_output)
    # print(summary)
    summary = (
        "Na podstawie danych klienta oraz przeprowadzonych sesji bikefittingu, "
        "wprowadzono następujące zmiany w ustawieniach roweru:\n\n"
        "1. Siodełko zostało obniżone o 7 mm, a kąt pochylenia zwiększony do -2 stopni.\n"
        "2. Pozycja kierownicy pozostała bez zmian.\n"
        "3. Mostek został wydłużony o 1 cm.\n"
        "4. Przesunięto siodełko o 6 mm ku tyłowi w celu przeniesienia środka ciężkości.\n"
        "5. Podkładka pod mostkiem została obniżona o 20 mm.\n"
        "6. Zmieniono pedały na model SPD 540.\n"
        "7. Zalecono klientowi ćwiczenia redukujące napięcia, regularne jazdy w stójce, zmiany chwytów oraz kontrolę łokci.\n"
        "8. Zalecono wzmocnienie treningiem siłowym obręczy barkowej i pleców.\n\n"
        "Dzięki powyższym dostosowaniom, zmniejszono napięcia mięśniowe, poprawiono stabilność i komfort jazdy klienta na rowerze."
    )

    buffer = Report().generate_pdf_report(client_data, form_data, structured_output, summary)

    report_content_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    if not get_report_exists_by_form_id(db, form_id):
        create_report(db, ReportInputSchema(report_content=report_content_base64, form_data_id=form_id))
    else:
        update_report_content(
            db, ReportInputSchema(report_content=report_content_base64, form_data_id=form_id)
        )
    return
