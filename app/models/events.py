from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from datetime import datetime

class BaseEvent(BaseModel):
    event_id: str
    event_time: datetime
    ingestion_time: datetime
    customer_id: str
    account_id: Optional[str] = None
    source_system: str
    event_type: str
    schema_version: str
    payload: Dict[str, Any]

class CardPaymentPayload(BaseModel):
    merchant_name: str
    mcc_category: str
    amount: float
    currency: str
    is_international: bool
    card_present: bool
    decline_reason: Optional[str] = None

class CoreBankingPayload(BaseModel):
    amount: float
    balance_after: float
    transaction_type: str

class SupportLogPayload(BaseModel):
    channel: str
    category: str
    raw_text: str
    resolution_status: str

# You can add more payloads as needed for specific domains
