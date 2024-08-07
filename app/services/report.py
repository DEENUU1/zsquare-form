from sqlalchemy.orm import Session

from models.client import Client
from models.form_data import FormData
from services.client_service import get_client_by_id
from services.form_data_service import get_form_by_id
from services.message_processor import convert_messages_to_dict
from services.message_service import get_messages_by_form_id
from utils.filename_generator import generate_filename
import pdfkit


def convert_html_to_pdf(filename: str, html_content: str):
    # TODO change this path later to linux
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdfkit.from_string(html_content, filename, configuration=config)


def build_html(filename: str, form_data: FormData, client_data: Client, summary: str = "", data=None) -> str:
    if data is None:
        data = dict()

    style = """
                <style>
                body {
                    font-family: Arial, sans-serif;
                }
                .container {
                    width: 80%;
                    margin: 0 auto;
                }
                .header {
                    text-align: center;
                    margin-top: 20px;
                }
                .header h1 {
                    font-size: 30px;
                    margin: 10px 0;
                }
                .section {
                    margin-top: 20px;
                }
                .section h2 {
                    font-size: 16px;
                    background-color: #f0f0f0;
                    padding: 5px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }
                table, th, td {
                    border: 1px solid black;
                }
                th, td {
                    padding: 8px;
                    text-align: left;
                }
                .note {
                    color: red;
                }
            </style>
    """

    html = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            {style}
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Veloart</h1>
                    <h2>Raport podsumowujący w ramach BIKEFITTINGU w Veloart</h2>
                    <p>Data wywiadu i bikefittingu: {form_data.created_at}</p>
                </div>
        
                <div class="section">
                    <h2>DANE PERSONALNE:</h2>
                    <table>
                        <tr>
                            <td>Imię i nazwisko:</td>
                            <td>{client_data.full_name}</td>
                        </tr>
                        <tr>
                            <td>Data urodzenia:</td>
                            <td>{client_data.birth_date}</td>
                        </tr>
                        <tr>
                            <td>Miejsce zamieszkania:</td>
                            <td>{client_data.location}</td>
                        </tr>
                        <tr>
                            <td>Telefon:</td>
                            <td>{client_data.phone}</td>
                        </tr>
                        <tr>
                            <td>Adres email:</td>
                            <td>{client_data.email}</td>
                        </tr>
                    </table>
                </div>
        
                <div class="section">
                    <h2>ANTROPOMETRIA:</h2>
                    <table>
                        <tr>
                            <td>Wysokość ciała:</td>
                            <td>160 cm</td>
                        </tr>
                        <tr>
                            <td>Rękojeść mostka/Długość tułowia:</td>
                            <td>130 cm</td>
                        </tr>
                        <tr>
                            <td>Długość wew. nogi:</td>
                            <td>77 cm</td>
                        </tr>
                        <tr>
                            <td>Szerokość ramion:</td>
                            <td>32 cm</td>
                        </tr>
                        <tr>
                            <td>Zasięg ramion:</td>
                            <td>155 cm</td>
                        </tr>
                        <tr>
                            <td>Adnotacje:</td>
                            <td></td>
                        </tr>
                    </table>
                </div>
        
                <div class="section">
                    <h2>ROWER:</h2>
                    <table>
                        <tr>
                            <td>Marka</td>
                            <td>{form_data.bike_brand}</td>
                        </tr>
                        <tr>    
                            <td>Model</td>
                            <td>{form_data.bike_model}</td>
                        </tr>
                        <tr>
                            <td>Rozmiar</td>
                            <td>{form_data.bike_size}</td>
                        </tr>
                        <tr>
                            <td>Rocznik</td>
                            <td>{form_data.bike_year}</td>
                        </tr>
                        <tr>
                            <td>Grupa napędowa</td>
                            <td>{form_data.drive_group}</td>
                        </tr>
                    </table>
                </div>
        
                <div class="section">
                    <h2>HISTORIA SPORTOWA/PROFIL KOLARSKI:</h2>
                    <table>
                        <tr>
                            <td>Roczny dystans</td>
                            <td>{form_data.year_distance}</td>
                        </tr>
                        <tr>
                            <td>Ilość sesji w tygodniu</td>
                            <td>{form_data.weekly_frequency}</td>
                        </tr>
                        <tr>
                            <td>Średni czas na kilometr</td>
                            <td>{form_data.avg_kilometer}</td>
                        </tr>    
                        <tr>
                            <td>Styl jazdy</td>
                            <td>{form_data.ride_style}</td>
                        </tr>  
                        <tr>
                            <td>Udział w eventach / zawodach</td>
                            <td>{form_data.event}</td>
                        </tr>  
                        <tr>
                            <td>Inne aktywności</td>
                            <td>{form_data.other_activity}</td>
                        </tr>      
                    </table>
                </div>
        
                <div class="section">
                    <h2>OBECNE PROBLEMY Z POZYCJĄ NA ROWERZE:</h2>
                    <table>
                        <tr>
                            <td>Cel wizyty</td>
                            <td>{form_data.visit_goal}\n{form_data.visit_problems}</td>
                        </tr>  
                        <tr>
                            <td>Przebyte kontuzje / operacje / choroby</td>
                            <td>{form_data.injuries}</td>
                        </tr> 
                    </table>
                </div>
        
                <div class="section">
                    <h2>PROFIL ORTOPEDYCZNY/ZDROWOTNY:</h2>
                    <table>
                        <tr>
                            <td>Problem z plecami odczuwalny również poza rowerem. //</td>
                        </tr>
                    </table>
                </div>
        
                <div class="section">
                    <h2>PROFIL MOTORYCZNY/OCENA FIZJOTERAPEUTYCZNA:</h2>
                    <table>
                        <tr>
                            <td>TESTY:</td>
                            <td>PRAWA NOGA</td>
                            <td>LEWA NOGA</td>
                        </tr>
                        <tr>
                            <td>
                                Zgięcie kręgosłupa dobre, rotacja miednicy bardzo duża.<br>
                                W teście zgięcia biodra większe napięcia PRAWA strona.<br>
                                W teście stania na jednej nodze i dynamicznie zginając LEWE biodro odczuwalnie mniej stabilne.
                            </td>
                            <td></td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>Adnotacje:</td>
                            <td></td>
                            <td></td>
                        </tr>
                    </table>
                </div>
                <div class="section">
                    <h2>ROWER SZOSOWY/POMIAR ROWERU</h2>
                    <table>
                        <tr>
                            <th></th>
                            <th>KOŃCOWE</th>
                            <th>OPCJONALNIE</th>
                        </tr>
                        <tr>
                            <td>1.Wysokość siodła</td>
                            <td>648 mm</td>
                            <td>651-653</td>
                        </tr>
                        <tr>
                            <td>2. Model siodła</td>
                            <td>Decathlon Triban Woman</td>
                            <td>Selle Italia SLR Lady</td>
                        </tr>
                        <tr>
                            <td>3. Rozmiar siodła</td>
                            <td>145 mm</td>
                            <td>130 mm</td>
                        </tr>
                        <tr>
                            <td>4. Nachylenie siodła</td>
                            <td>-3,8° (czujca)</td>
                            <td>-2,8-3,8°</td>
                        </tr>
                        <tr>
                            <td>5. Offset czujcy</td>
                            <td>-20 mm</td>
                            <td>Płynna regulacja kąta</td>
                        </tr>
                        <tr>
                            <td>6. Odsunięcie siodła od osi suportu</td>
                            <td>- 29 mm (151 mm)</td>
                            <td>- 42 mm (172 mm)</td>
                        </tr>
                        <tr>
                            <td>7. Końcówka siodła do środka kierownicy</td>
                            <td>430-435 mm</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>8. Końcówka siodła do manetki</td>
                            <td>590 mm</td>
                            <td>575 mm</td>
                        </tr>
                        <tr>
                            <td>9. Różnica wysokości (DROP)</td>
                            <td>- 40 mm</td>
                            <td>- 35 / - 45</td>
                        </tr>
                        <tr>
                            <td>10.Mostek długość/kąt</td>
                            <td>60 mm / -7°</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>11. Szerokość kierownicy</td>
                            <td>38 cm CC (36 manetki)</td>
                            <td>32 cm CC</td>
                        </tr>
                        <tr>
                            <td>12. Model kierownicy</td>
                            <td>Seryna</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>13. Wysokość podkładek</td>
                            <td>35 mm (10 mm regulacji)</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>14. Długość korby</td>
                            <td>165 mm</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td>15. Kąt manetek (kierownica/dźwignia)</td>
                            <td>X</td>
                            <td></td>
                        </tr>
                    </table>
                </div>
            </div>
        </body>
    </html>
    """

    return html


def generate_report(db: Session, form_id: int = 1) -> None:
    form_data = get_form_by_id(db, form_id)
    client_data = get_client_by_id(db, form_data.client_id)
    messages = get_messages_by_form_id(db, form_id)
    messages_dict = convert_messages_to_dict(messages)

    filename = generate_filename(form_data, client_data)
    # session_summary = generate_session_summary(form_data, messages_dict)
    session_summary = "xyz"

    # structured_conversation_data = get_conversation_information(messages_dict)
    structured_conversation_data = None
    html_content = build_html(filename, form_data, client_data, session_summary, structured_conversation_data)
    pdf = convert_html_to_pdf(filename, html_content)

    # buffer = Report().generate_pdf_report(client_data, form_data, structured_output, summary)
    #
    # report_content_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # if not get_report_exists_by_form_id(db, form_id):
    #     create_report(db, ReportInputSchema(report_content=report_content_base64, form_data_id=form_id))
    # else:
    #     update_report_content(
    #         db, ReportInputSchema(report_content=report_content_base64, form_data_id=form_id)
    #     )
    return
