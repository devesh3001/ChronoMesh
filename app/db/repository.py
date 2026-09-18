from sqlalchemy import Column, String, DateTime, Integer, JSON
from sqlalchemy.orm import Session
from app.db.database import Base
from datetime import datetime
import json
import uuid

class EvidenceRecord(Base):
    __tablename__ = "evidence_contracts"
    id = Column(String, primary_key=True, index=True)
    evidence_id = Column(String, index=True)
    customer_id = Column(String, index=True)
    claim_type = Column(String)
    structured_value = Column(String)
    source_role = Column(String)
    confidence = Column(String)
    source_event_ids = Column(JSON)
    valid_from = Column(DateTime)
    valid_to = Column(DateTime, nullable=True)
    superseded_by = Column(String, nullable=True)

class CheckpointRecord(Base):
    __tablename__ = "checkpoints"
    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    as_of_time = Column(DateTime)
    inferred_state = Column(String)
    confidence_band = Column(String)
    action = Column(String)
    action_subtype = Column(String, nullable=True)
    hitl_status = Column(String)
    notes = Column(String, nullable=True)

def init_db(engine):
    Base.metadata.create_all(bind=engine)

def save_evidence(db: Session, evidence_data: dict):
    # Ensure ID
    db_record = EvidenceRecord(
        id=str(uuid.uuid4()),
        **evidence_data
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_current_evidence(db: Session, customer_id: str, as_of: datetime):
    # Returns evidence that is valid at the `as_of` time
    records = db.query(EvidenceRecord).filter(
        EvidenceRecord.customer_id == customer_id,
        EvidenceRecord.valid_from <= as_of
    ).all()
    
    # Filter out superseded or expired in python for simplicity in sqlite prototype
    valid_records = []
    for r in records:
        if r.valid_to and r.valid_to < as_of:
            continue
        if r.superseded_by:
            # check if superseded_by happened before as_of
            pass # simplified
        valid_records.append(r)
    return valid_records

def save_checkpoint(db: Session, checkpoint_data: dict, customer_id: str):
    db_record = CheckpointRecord(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        **checkpoint_data
    )
    db.add(db_record)
    db.commit()
    return db_record
