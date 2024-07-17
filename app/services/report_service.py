import base64

from sqlalchemy.orm import Session
from models.report import Report
from schemas.report_schema import ReportOutputSchema


def get_report_by_form_id(db: Session, form_id) -> ReportOutputSchema:
    report = db.query(Report).filter(Report.form_data_id == form_id).first()
    if report:
        report.report_content = base64.b64encode(report.report_content).decode('utf-8')
    return ReportOutputSchema.from_orm(report) if report else None
