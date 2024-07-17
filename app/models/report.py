from sqlalchemy import Column, Integer, ForeignKey, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class Report(Base):
    __tablename__ = 'report'

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_content = Column(LargeBinary, nullable=False)
    form_data_id = Column(Integer, ForeignKey('form.id'), unique=True, nullable=False)
    form_data = relationship("FormData", back_populates="report", uselist=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
