import hashlib
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from models import (
    Member, Invoice, InvoiceStatus, PayoutRequest, PayoutStatus,
    AuditLogEntry, SeverityEnum, BudgetCategory, TreasuryStatus
)

def current_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def generate_hash(data_str: str) -> str:
    return hashlib.sha256(data_str.encode('utf-8')).hexdigest()[:16]

class InMemoryDatabase:
    def __init__(self):
        self.reset_to_seed_data()

    def reset_to_seed_data(self):
        # 1. Members
        self.members: List[Member] = [
            Member(id="m1", name="Rahul Sharma", email="rahul.sharma@example.com", avatar="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&h=100&fit=crop"),
            Member(id="m2", name="Priya Patel", email="priya.patel@example.com", avatar="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop"),
            Member(id="m3", name="Aman Gupta", email="aman.gupta@example.com", avatar="https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=100&h=100&fit=crop"),
            Member(id="m4", name="Sneha Rao", email="sneha.rao@example.com", avatar="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop"),
            Member(id="m5", name="Rohan Verma", email="rohan.verma@example.com", avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop"),
        ]

        # 2. Invoices (Initial hackathon collection: 5 members, 500 each)
        self.invoices: List[Invoice] = [
            Invoice(id="inv_101", member_id="m1", member_name="Rahul Sharma", amount=500.0, note="Hackathon 2026 Registration Fee", status=InvoiceStatus.PAID, paypal_invoice_id="INV2-984F-B21A", created_at="2026-11-10T10:15:00Z", paid_at="2026-11-10T14:22:10Z"),
            Invoice(id="inv_102", member_id="m2", member_name="Priya Patel", amount=500.0, note="Hackathon 2026 Registration Fee", status=InvoiceStatus.PAID, paypal_invoice_id="INV2-832A-77CF", created_at="2026-11-10T10:15:00Z", paid_at="2026-11-10T15:40:02Z"),
            Invoice(id="inv_103", member_id="m3", member_name="Aman Gupta", amount=500.0, note="Hackathon 2026 Registration Fee", status=InvoiceStatus.UNPAID, paypal_invoice_id="INV2-411E-90DA", created_at="2026-11-10T10:15:00Z"),
            Invoice(id="inv_104", member_id="m4", member_name="Sneha Rao", amount=500.0, note="Hackathon 2026 Registration Fee", status=InvoiceStatus.UNPAID, paypal_invoice_id="INV2-628D-33AB", created_at="2026-11-10T10:15:00Z"),
            Invoice(id="inv_105", member_id="m5", member_name="Rohan Verma", amount=500.0, note="Hackathon 2026 Registration Fee", status=InvoiceStatus.UNPAID, paypal_invoice_id="INV2-119C-55EE", created_at="2026-11-10T10:15:00Z"),
        ]

        # 3. Budget Categories
        self.categories: Dict[str, Dict[str, float]] = {
            "Venue & Hall": {"allocated": 10000.0, "spent": 0.0},
            "Food & Catering": {"allocated": 8000.0, "spent": 1200.0},
            "Prizes & Swag": {"allocated": 5000.0, "spent": 0.0},
            "Logistics & Misc": {"allocated": 2000.0, "spent": 350.0},
        }

        # 4. Governance limits
        self.per_transaction_limit: float = 1000.0  # Above this needs 2 approvers!
        self.initial_treasury_balance: float = 23950.0

        # 5. Payout Requests
        self.payout_requests: List[PayoutRequest] = [
            PayoutRequest(
                id="pay_901",
                vendor="Grand Auditorium & Expo Services",
                amount=3200.0,
                category="Venue & Hall",
                note="Auditorium deposit for Hackathon Finals",
                receipt_filename="venue_deposit_receipt.pdf",
                status=PayoutStatus.PENDING_APPROVAL,
                requires_dual_approval=True,
                approver1_approved=False,
                approver2_approved=False,
                created_at="2026-11-11T09:30:00Z",
                updated_at="2026-11-11T09:30:00Z"
            )
        ]

        # 6. Audit Trail
        self.audit_log: List[AuditLogEntry] = [
            AuditLogEntry(
                id="aud_01",
                timestamp="2026-11-10T10:15:00Z",
                actor="agent:treasurer-ai",
                action="INVOICES_BATCH_CREATED",
                details={"count": 5, "total_requested": 2500.0, "currency": "INR", "reason": "Hackathon 2026 registration dues"},
                request_id="req_init_inv",
                hash_signature="7f8b92d6e41c30a2",
                severity=SeverityEnum.INFO
            ),
            AuditLogEntry(
                id="aud_02",
                timestamp="2026-11-10T14:22:10Z",
                actor="paypal:webhook",
                action="INVOICE_PAID",
                details={"invoice_id": "inv_101", "member": "Rahul Sharma", "amount": 500.0},
                request_id="wh_00192a83f",
                hash_signature="11a4c9e8f002b5d1",
                severity=SeverityEnum.INFO
            ),
            AuditLogEntry(
                id="aud_03",
                timestamp="2026-11-11T09:30:00Z",
                actor="treasurer:alex",
                action="PAYOUT_REQUESTED",
                details={"payout_id": "pay_901", "vendor": "Grand Auditorium", "amount": 3200.0, "limit": 1000.0, "status": "2_APPROVALS_REQUIRED"},
                request_id="req_pay_aud_01",
                hash_signature="e93b12984ac37fa0",
                severity=SeverityEnum.WARNING
            )
        ]

        # 7. Telegram Bot Channel Simulation
        self.telegram_messages: List[Dict[str, Any]] = [
            {
                "id": "tg_01",
                "chat_name": "🏛️ Hackathon Executive Board",
                "sender": "Club Treasurer AI Bot",
                "is_bot": True,
                "text": "🚨 *Action Required: Payout Approval Request*\n\nVendor: *Grand Auditorium & Expo Services*\nAmount: *₹3,200.00* (Exceeds ₹1,000 threshold)\nCategory: *Venue & Hall*\nBudget Remaining: *₹10,000.00*\n\nTwo approvals are required before PayPal Payouts release.",
                "timestamp": "2026-11-11T09:30:00Z",
                "payout_id": "pay_901",
                "status": "AWAITING_APPROVALS",
                "inline_keyboard": [
                    {"label": "✅ Approve (Approver 1)", "action": "approve_1", "role": "approver_1", "name": "Priya Patel (President)"},
                    {"label": "✅ Approve (Approver 2)", "action": "approve_2", "role": "approver_2", "name": "Dev Verma (VP)"},
                    {"label": "❌ Reject Payout", "action": "reject", "role": "approver_1", "name": "Board Approver"}
                ]
            }
        ]

    # --- Methods ---
    def get_telegram_messages(self) -> List[Dict[str, Any]]:
        return self.telegram_messages

    def push_telegram_notification(self, payout: PayoutRequest):
        msg_id = f"tg_{uuid.uuid4().hex[:6]}"
        self.telegram_messages.append({
            "id": msg_id,
            "chat_name": "🏛️ Hackathon Executive Board",
            "sender": "Club Treasurer AI Bot",
            "is_bot": True,
            "text": f"🚨 *New Payout Request Submitted*\n\nVendor: *{payout.vendor}*\nAmount: *₹{payout.amount:,.2f}*\nCategory: *{payout.category}*\nNote: {payout.note}\n\nStrict governance mandate: 2 approvals required.",
            "timestamp": current_iso(),
            "payout_id": payout.id,
            "status": "AWAITING_APPROVALS",
            "inline_keyboard": [
                {"label": "✅ Approve (President)", "action": "approve_1", "role": "approver_1", "name": "Priya Patel (President)"},
                {"label": "✅ Approve (VP)", "action": "approve_2", "role": "approver_2", "name": "Dev Verma (VP)"},
                {"label": "❌ Reject Payout", "action": "reject", "role": "approver_1", "name": "Board Approver"}
            ]
        })
    def get_members(self) -> List[Member]:
        return self.members

    def get_invoices(self) -> List[Invoice]:
        return sorted(self.invoices, key=lambda x: x.created_at, reverse=True)

    def add_invoice(self, member_name: str, amount: float, note: str, member_email: Optional[str] = None) -> Invoice:
        # Check if member exists, otherwise create
        member = next((m for m in self.members if m.name.lower() == member_name.lower()), None)
        if not member:
            member_id = f"m_{len(self.members) + 1}"
            email = member_email or f"{member_name.lower().replace(' ', '.')}@example.com"
            member = Member(id=member_id, name=member_name, email=email, avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop")
            self.members.append(member)

        inv_id = f"inv_{uuid.uuid4().hex[:6]}"
        now = current_iso()
        paypal_id = f"INV2-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:4].upper()}"

        inv = Invoice(
            id=inv_id,
            member_id=member.id,
            member_name=member.name,
            amount=amount,
            currency="INR",
            note=note,
            status=InvoiceStatus.UNPAID,
            paypal_invoice_id=paypal_id,
            created_at=now
        )
        self.invoices.append(inv)

        self.log_audit(
            actor="agent:treasurer-ai",
            action="INVOICE_CREATED",
            details={"invoice_id": inv_id, "member": member.name, "amount": amount, "paypal_id": paypal_id},
            severity=SeverityEnum.INFO
        )
        return inv

    def mark_invoice_paid(self, invoice_id: str) -> Optional[Invoice]:
        for inv in self.invoices:
            if inv.id == invoice_id or inv.paypal_invoice_id == invoice_id:
                inv.status = InvoiceStatus.PAID
                inv.paid_at = current_iso()
                self.log_audit(
                    actor="paypal:webhook_simulator",
                    action="INVOICE_PAID",
                    details={"invoice_id": inv.id, "member": inv.member_name, "amount": inv.amount},
                    severity=SeverityEnum.INFO
                )
                return inv
        return None

    def get_payout_requests(self) -> List[PayoutRequest]:
        return sorted(self.payout_requests, key=lambda x: x.created_at, reverse=True)

    def create_payout_request(self, vendor: str, amount: float, category: str, note: str, receipt_filename: Optional[str] = None) -> PayoutRequest:
        now = current_iso()
        payout_id = f"pay_{uuid.uuid4().hex[:6]}"
        requires_dual = amount > self.per_transaction_limit

        req = PayoutRequest(
            id=payout_id,
            vendor=vendor,
            amount=amount,
            category=category,
            note=note,
            receipt_filename=receipt_filename,
            status=PayoutStatus.PENDING_APPROVAL,
            requires_dual_approval=requires_dual,
            created_at=now,
            updated_at=now
        )
        self.payout_requests.append(req)

        self.log_audit(
            actor="agent:treasurer-ai",
            action="PAYOUT_REQUEST_SUBMITTED",
            details={
                "payout_id": payout_id,
                "vendor": vendor,
                "amount": amount,
                "category": category,
                "requires_dual_approval": requires_dual,
                "threshold": self.per_transaction_limit
            },
            severity=SeverityEnum.WARNING if requires_dual else SeverityEnum.INFO
        )

        if requires_dual:
            self.push_telegram_notification(req)

        return req

    def sign_payout_approval(self, payout_id: str, approver_role: str, approver_name: str, approve: bool = True) -> Optional[PayoutRequest]:
        req = next((p for p in self.payout_requests if p.id == payout_id), None)
        if not req:
            return None

        now = current_iso()
        if not approve:
            req.status = PayoutStatus.REJECTED
            req.updated_at = now
            self.log_audit(
                actor=f"{approver_role}:{approver_name}",
                action="PAYOUT_REJECTED",
                details={"payout_id": payout_id, "amount": req.amount, "vendor": req.vendor},
                severity=SeverityEnum.ALERT
            )
            return req

        if approver_role == "approver_1":
            req.approver1_approved = True
            req.approver1_name = approver_name
            req.approver1_at = now
        elif approver_role == "approver_2":
            req.approver2_approved = True
            req.approver2_name = approver_name
            req.approver2_at = now

        # Evaluate state machine
        if req.requires_dual_approval:
            if req.approver1_approved and req.approver2_approved:
                req.status = PayoutStatus.DISPATCHED
                req.paypal_payout_batch_id = f"BATCH-PAYPAL-{uuid.uuid4().hex[:8].upper()}"
                # Deduct from budget
                if req.category in self.categories:
                    self.categories[req.category]["spent"] += req.amount
                self.log_audit(
                    actor="paypal:payouts_api",
                    action="PAYOUT_DISPATCHED",
                    details={
                        "payout_id": req.id,
                        "batch_id": req.paypal_payout_batch_id,
                        "amount": req.amount,
                        "vendor": req.vendor,
                        "approver1": req.approver1_name,
                        "approver2": req.approver2_name
                    },
                    severity=SeverityEnum.INFO
                )
                self.telegram_messages.append({
                    "id": f"tg_{uuid.uuid4().hex[:6]}",
                    "chat_name": "🏛️ Hackathon Executive Board",
                    "sender": "Club Treasurer AI Bot",
                    "is_bot": True,
                    "text": f"🎉 *Payout Fully Authorized & Dispatched!*\n\nBoth Approver 1 ({req.approver1_name}) and Approver 2 ({req.approver2_name}) have signed.\n\nPayPal Batch ID: `{req.paypal_payout_batch_id}`\nAmount: ₹{req.amount:,.2f} to {req.vendor}",
                    "timestamp": current_iso(),
                    "payout_id": req.id,
                    "status": "DISPATCHED",
                    "inline_keyboard": []
                })
            else:
                req.status = PayoutStatus.PENDING_APPROVAL
                self.telegram_messages.append({
                    "id": f"tg_{uuid.uuid4().hex[:6]}",
                    "chat_name": "🏛️ Hackathon Executive Board",
                    "sender": "Club Treasurer AI Bot",
                    "is_bot": True,
                    "text": f"✍️ *Signature Recorded: 1 of 2 Received*\n\n{approver_name} signed approval for #{req.id} (₹{req.amount:,.2f}).\nAwaiting second executive approval.",
                    "timestamp": current_iso(),
                    "payout_id": req.id,
                    "status": "PARTIALLY_APPROVED",
                    "inline_keyboard": [
                        {"label": "✅ Sign as Second Approver", "action": "approve_2" if approver_role == "approver_1" else "approve_1", "role": "approver_2" if approver_role == "approver_1" else "approver_1", "name": "Dev Verma (VP)" if approver_role == "approver_1" else "Priya Patel (President)"}
                    ]
                })
        else:
            # Single approval sufficient
            req.status = PayoutStatus.DISPATCHED
            req.paypal_payout_batch_id = f"BATCH-PAYPAL-{uuid.uuid4().hex[:8].upper()}"
            if req.category in self.categories:
                self.categories[req.category]["spent"] += req.amount

        req.updated_at = now
        return req

    def get_public_transparency(self) -> Dict[str, Any]:
        status = self.get_treasury_status()
        transactions = []
        for p in self.payout_requests:
            masked_vendor = p.vendor[:8] + "*** [Verified Vendor]" if len(p.vendor) > 8 else p.vendor
            transactions.append({
                "id": p.id,
                "masked_vendor": masked_vendor,
                "amount": p.amount,
                "category": p.category,
                "status": p.status.value,
                "purpose": p.note,
                "created_at": p.created_at,
                "approvers": [name for name in [p.approver1_name, p.approver2_name] if name],
                "batch_id": p.paypal_payout_batch_id
            })
        return {
            "club_name": "Hackathon & Tech Club Treasury",
            "current_balance": status.current_balance,
            "total_spent": status.total_spent,
            "categories": [{"name": c.name, "spent": c.spent, "allocated": c.allocated} for c in status.categories],
            "approved_transactions": transactions,
            "policy": "Two-Person Rule mandatory on all disbursements > ₹1,000",
            "last_synced": current_iso()
        }

    def capture_paypal_order(self, order_id: str, invoice_id: str, amount: float, payer_name: str, payer_email: str) -> Optional[Invoice]:
        inv = next((i for i in self.invoices if i.id == invoice_id or i.paypal_invoice_id == invoice_id), None)
        if not inv:
            return None
        inv.status = InvoiceStatus.PAID
        inv.paid_at = current_iso()
        self.log_audit(
            actor="paypal:smart_buttons_sdk",
            action="PAYPAL_CAPTURE_SUCCESS",
            details={
                "order_id": order_id,
                "invoice_id": inv.id,
                "amount": amount,
                "payer": payer_name,
                "email": payer_email,
                "sdk_version": "PayPal JS SDK v5/v6"
            },
            severity=SeverityEnum.INFO
        )
        return inv

    def get_treasury_status(self) -> TreasuryStatus:
        total_collected = sum(inv.amount for inv in self.invoices if inv.status == InvoiceStatus.PAID)
        total_spent = sum(c["spent"] for c in self.categories.values())
        total_budget = sum(c["allocated"] for c in self.categories.values())
        current_balance = self.initial_treasury_balance + total_collected - total_spent

        cat_list = [
            BudgetCategory(
                name=k,
                allocated=v["allocated"],
                spent=v["spent"],
                remaining=max(0.0, v["allocated"] - v["spent"])
            )
            for k, v in self.categories.items()
        ]

        pending_payouts = len([p for p in self.payout_requests if p.status == PayoutStatus.PENDING_APPROVAL])
        unpaid_invoices = len([i for i in self.invoices if i.status == InvoiceStatus.UNPAID])

        return TreasuryStatus(
            total_budget=total_budget,
            total_collected=total_collected,
            total_spent=total_spent,
            current_balance=current_balance,
            per_transaction_limit=self.per_transaction_limit,
            pending_payouts_count=pending_payouts,
            unpaid_invoices_count=unpaid_invoices,
            categories=cat_list
        )

    def get_audit_log(self) -> List[AuditLogEntry]:
        return sorted(self.audit_log, key=lambda x: x.timestamp, reverse=True)

    def log_audit(self, actor: str, action: str, details: Dict[str, Any], severity: SeverityEnum = SeverityEnum.INFO) -> AuditLogEntry:
        now = current_iso()
        req_id = f"req_{uuid.uuid4().hex[:8]}"
        data_sig = f"{now}|{actor}|{action}|{req_id}|{str(details)}"
        entry = AuditLogEntry(
            id=f"aud_{uuid.uuid4().hex[:6]}",
            timestamp=now,
            actor=actor,
            action=action,
            details=details,
            request_id=req_id,
            hash_signature=generate_hash(data_sig),
            severity=severity
        )
        self.audit_log.append(entry)
        return entry

db = InMemoryDatabase()

