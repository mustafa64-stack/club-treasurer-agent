from typing import List, Dict, Any, Optional
from database import db
from guardrails import guardrails
from models import ToolExecutionTrace

def tool_create_invoices(member_names: List[str], amount: float, note: str) -> Dict[str, Any]:
    created = []
    for name in member_names:
        inv = db.add_invoice(member_name=name.strip(), amount=amount, note=note)
        created.append({
            "invoice_id": inv.id,
            "member_name": inv.member_name,
            "amount": inv.amount,
            "paypal_invoice_id": inv.paypal_invoice_id,
            "status": inv.status.value
        })
    return {
        "success": True,
        "count": len(created),
        "total_amount": amount * len(created),
        "currency": "INR",
        "invoices": created,
        "message": f"Successfully created {len(created)} PayPal Sandbox invoices for ₹{amount} each."
    }

def tool_get_treasury_status() -> Dict[str, Any]:
    status = db.get_treasury_status()
    return {
        "success": True,
        "current_balance": status.current_balance,
        "total_budget": status.total_budget,
        "total_collected": status.total_collected,
        "total_spent": status.total_spent,
        "per_transaction_limit": status.per_transaction_limit,
        "pending_payouts_count": status.pending_payouts_count,
        "unpaid_invoices_count": status.unpaid_invoices_count,
        "categories": [
            {
                "name": c.name,
                "allocated": c.allocated,
                "spent": c.spent,
                "remaining": c.remaining
            }
            for c in status.categories
        ]
    }

def tool_check_budget_category(category: str) -> Dict[str, Any]:
    status = db.get_treasury_status()
    matched = None
    for c in status.categories:
        if category.lower() in c.name.lower():
            matched = c
            break

    if not matched:
        return {
            "success": False,
            "message": f"Category '{category}' not found.",
            "available_categories": [c.name for c in status.categories]
        }

    return {
        "success": True,
        "category": matched.name,
        "allocated": matched.allocated,
        "spent": matched.spent,
        "remaining": matched.remaining,
        "utilization_pct": round((matched.spent / matched.allocated * 100) if matched.allocated else 0, 1)
    }

def tool_request_payout_approval(vendor: str, amount: float, category: str, note: str, receipt_filename: Optional[str] = None) -> Dict[str, Any]:
    # Check guardrails
    limit_check = guardrails.check_payout_limits(amount, category)
    if limit_check["is_blocked_by_budget"]:
        return {
            "success": False,
            "error": "BUDGET_EXCEEDED",
            "message": f"Blocked: Amount ₹{amount} exceeds remaining budget ₹{limit_check['remaining_in_category']} in '{category}'."
        }

    payout_req = db.create_payout_request(
        vendor=vendor,
        amount=amount,
        category=category,
        note=note,
        receipt_filename=receipt_filename
    )

    return {
        "success": True,
        "payout_id": payout_req.id,
        "vendor": payout_req.vendor,
        "amount": payout_req.amount,
        "category": payout_req.category,
        "requires_dual_approval": payout_req.requires_dual_approval,
        "status": payout_req.status.value,
        "message": (
            f"Payout request #{payout_req.id} created for ₹{amount} to {vendor}. "
            f"Because it is > ₹{limit_check['per_transaction_limit']}, it requires approval from both Approver 1 (President) and Approver 2 (VP)."
            if payout_req.requires_dual_approval else
            f"Payout request #{payout_req.id} created and queued for single approval."
        )
    }

def tool_send_payment_reminder(member_name: str) -> Dict[str, Any]:
    invoices = db.get_invoices()
    unpaid = [i for i in invoices if i.member_name.lower() == member_name.lower() and i.status.value == "UNPAID"]
    if not unpaid:
        return {
            "success": False,
            "message": f"No unpaid invoices found for {member_name}."
        }

    inv = unpaid[0]
    reminder_text = (
        f"Hi {inv.member_name}! Quick friendly reminder from your Club Treasurer: "
        f"Invoice {inv.paypal_invoice_id} for ₹{inv.amount} ({inv.note}) is awaiting payment. "
        f"Please clear it via PayPal when you get a chance!"
    )
    return {
        "success": True,
        "member_name": inv.member_name,
        "invoice_id": inv.id,
        "amount": inv.amount,
        "reminder_message": reminder_text
    }

TOOL_REGISTRY = {
    "create_invoices": tool_create_invoices,
    "get_treasury_status": tool_get_treasury_status,
    "check_budget_category": tool_check_budget_category,
    "request_payout_approval": tool_request_payout_approval,
    "send_payment_reminder": tool_send_payment_reminder
}

