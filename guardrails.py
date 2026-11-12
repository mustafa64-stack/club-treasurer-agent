import re
from typing import Tuple, Optional, Dict, Any
from database import db
from models import SeverityEnum

# Allow-listed tool definitions only
ALLOWED_TOOLS = {
    "create_invoices",
    "get_treasury_status",
    "check_budget_category",
    "request_payout_approval",
    "send_payment_reminder",
    "search_transactions"
}

# Malicious prompt injection signatures often embedded inside PDFs/receipts/user text
PROMPT_INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"disregard (all )?prior commands",
    r"system prompt override",
    r"you are now in (god|developer) mode",
    r"transfer (all|\d+) funds to",
    r"bypass approval",
    r"auto-?approve payout",
    r"act as (the )?(president|treasurer|admin)",
    r"send paypal to 0x[a-fA-F0-9]+",
    r"<script.*?>",
    r"\{\{.*?\}\}"
]

class SecurityGuardrails:
    @staticmethod
    def inspect_text_for_prompt_injection(content: str) -> Tuple[bool, Optional[str]]:
        """
        Guards against prompt injection attacks hidden inside user prompts or OCR text from receipts.
        Returns: (is_safe, threat_description)
        """
        for pattern in PROMPT_INJECTION_PATTERNS:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                threat = f"Security Violation: Detected malicious injection pattern '{match.group(0)}'"
                db.log_audit(
                    actor="guardrail:firewall",
                    action="PROMPT_INJECTION_BLOCKED",
                    details={"matched_pattern": match.group(0), "snippet": content[:120]},
                    severity=SeverityEnum.ALERT
                )
                return False, threat
        return True, None

    @staticmethod
    def validate_tool_permission(tool_name: str, actor_role: str) -> Tuple[bool, Optional[str]]:
        """
        Ensures the agent never executes non-allowlisted or unauthorized actions.
        Notice: THERE IS NO 'approve_payout' TOOL! AI CAN NEVER APPROVE PAYOUTS!
        """
        if tool_name not in ALLOWED_TOOLS:
            err = f"Security Exception: Tool '{tool_name}' is not in the allow-listed toolset."
            db.log_audit(
                actor="guardrail:authorizer",
                action="UNAUTHORIZED_TOOL_BLOCKED",
                details={"tool_name": tool_name, "role": actor_role},
                severity=SeverityEnum.ALERT
            )
            return False, err

        # Specific role constraints
        if tool_name == "request_payout_approval" and actor_role == "public":
            return False, "Public members cannot request payouts."

        return True, None

    @staticmethod
    def check_payout_limits(amount: float, category: str) -> Dict[str, Any]:
        """
        Validates transaction threshold and budget bounds.
        """
        status = db.get_treasury_status()
        cat_info = next((c for c in status.categories if c.name.lower() == category.lower()), None)

        exceeds_budget = False
        remaining_budget = 0.0
        if cat_info:
            remaining_budget = cat_info.remaining
            if amount > remaining_budget:
                exceeds_budget = True

        requires_dual = amount > status.per_transaction_limit

        return {
            "amount": amount,
            "category": category,
            "per_transaction_limit": status.per_transaction_limit,
            "requires_dual_approval": requires_dual,
            "exceeds_budget": exceeds_budget,
            "remaining_in_category": remaining_budget,
            "is_blocked_by_budget": exceeds_budget
        }

guardrails = SecurityGuardrails()

