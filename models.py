from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RoleEnum(str, Enum):
    TREASURER = "treasurer"
    APPROVER_1 = "approver_1"  # e.g., President
    APPROVER_2 = "approver_2"  # e.g., Vice President
    PUBLIC = "public"


class InvoiceStatus(str, Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class PayoutStatus(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    DISPATCHED = "DISPATCHED"
    REJECTED = "REJECTED"
    FLAGGED = "FLAGGED_SECURITY_RISK"


class SeverityEnum(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ALERT = "ALERT"


class Member(BaseModel):
    id: str
    name: str
    email: str
    avatar: str


class Invoice(BaseModel):
    id: str
    member_id: str
    member_name: str
    amount: float
    currency: str = "INR"
    note: str
    status: InvoiceStatus = InvoiceStatus.UNPAID
    paypal_invoice_id: Optional[str] = None
    webhook_signature_verified: bool = True
    created_at: str
    paid_at: Optional[str] = None


class PayoutRequest(BaseModel):
    id: str
    vendor: str
    amount: float
    category: str
    note: str
    receipt_filename: Optional[str] = None
    status: PayoutStatus = PayoutStatus.PENDING_APPROVAL
    requires_dual_approval: bool = True
    flags: List[str] = ["OVER_LIMIT", "NEW_PAYEE", "DUPLICATE_CHECK_PASSED"]
    idempotency_key: str = "IDEM-77a82b"
    approver1_approved: bool = False
    approver1_name: Optional[str] = None
    approver1_at: Optional[str] = None
    approver2_approved: bool = False
    approver2_name: Optional[str] = None
    approver2_at: Optional[str] = None
    paypal_payout_batch_id: Optional[str] = None
    security_flag: Optional[str] = None
    created_at: str
    updated_at: str


class AuditLogEntry(BaseModel):
    id: str
    timestamp: str
    actor: str
    action: str
    details: Dict[str, Any]
    request_id: str
    hash_signature: str
    severity: SeverityEnum = SeverityEnum.INFO


class ToolExecutionTrace(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    output: Dict[str, Any]
    status: str = "success"  # "success" or "blocked"
    reason: Optional[str] = None


class AgentChatRequest(BaseModel):
    message: str
    actor_role: RoleEnum = RoleEnum.TREASURER
    conversation_history: List[Dict[str, str]] = []


class AgentChatResponse(BaseModel):
    reply: str
    tool_traces: List[ToolExecutionTrace] = []
    actions_taken: List[str] = []
    guardrail_status: str = "PASSED"
    security_alert: Optional[str] = None


class ReceiptAnalysisResult(BaseModel):
    vendor: str
    amount: float
    category: str
    date: str
    confidence_score: float
    is_safe: bool = True
    security_warning: Optional[str] = None
    budget_remaining: float
    fits_budget: bool = True
    requires_approval: bool = True
    raw_ocr_preview: Optional[str] = None


class BudgetCategory(BaseModel):
    name: str
    allocated: float
    spent: float
    remaining: float


class TreasuryStatus(BaseModel):
    total_budget: float
    total_collected: float
    total_spent: float
    current_balance: float
    per_transaction_limit: float
    pending_payouts_count: int
    unpaid_invoices_count: int
    categories: List[BudgetCategory]

