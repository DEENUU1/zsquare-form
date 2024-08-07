import base64
from sqlalchemy.orm import Session
from schemas.report_schema import ReportInputSchema, ReportOutputSchema
from models.report import Report


def create_report(db: Session, report: ReportInputSchema) -> ReportOutputSchema:
    report_content_binary = base64.b64decode(report.report_content)

    new_report = Report(
        report_content=report_content_binary,
        form_data_id=report.form_data_id
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return ReportOutputSchema.from_orm(new_report)


def update_report_content(db: Session, report: ReportInputSchema) -> ReportOutputSchema:
    report_content_binary = base64.b64decode(report.report_content)

    report_to_update = db.query(Report).filter(Report.form_data_id == report.form_data_id).first()

    report_to_update.report_content = report_content_binary

    db.commit()
    db.refresh(report_to_update)

    return ReportOutputSchema.from_orm(report_to_update)


def get_report_by_form_id(db: Session, form_id: int) -> ReportOutputSchema:
    report = db.query(Report).filter(Report.form_data_id == form_id).first()
    if report:
        report.report_content = base64.b64encode(report.report_content).decode('utf-8')
    return ReportOutputSchema.from_orm(report) if report else None


def get_report_exists_by_form_id(
        db: Session,
        form_id: int
) -> bool:
    report = db.query(Report).filter(Report.form_data_id == form_id).first()

    return True if report else False
