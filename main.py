import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional

from database import db
from models import (
    AgentChatRequest, AgentChatResponse,
    ReceiptAnalysisResult, RoleEnum
)
from agent import treasurer_agent
from vision import receipt_scanner, SAMPLE_RECEIPTS

app = FastAPI(
    title="Club Treasurer Agent",
    description="An AI treasurer that handles your club's money, but never without your approval.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
@app.get("/api/treasury/status")
def get_treasury_status():
    return db.get_treasury_status()

@app.get("/api/invoices")
def list_invoices():
    return db.get_invoices()

@app.post("/api/invoices/simulate-payment/{invoice_id}")
def simulate_invoice_payment(invoice_id: str):
    inv = db.mark_invoice_paid(invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"success": True, "invoice": inv, "message": f"Webhook simulated: Invoice #{inv.id} paid via PayPal"}

@app.get("/api/payouts")
def list_payouts():
    return db.get_payout_requests()

@app.post("/api/payouts/{payout_id}/approve")
def approve_payout(payout_id: str, payload: Dict[str, Any] = Body(...)):
    role = payload.get("role", "approver_1")
    name = payload.get("name", "Approver")
    res = db.sign_payout_approval(payout_id=payout_id, approver_role=role, approver_name=name, approve=True)
    if not res:
        raise HTTPException(status_code=404, detail="Payout request not found")
    return {"success": True, "payout": res}

@app.post("/api/payouts/{payout_id}/reject")
def reject_payout(payout_id: str, payload: Dict[str, Any] = Body(...)):
    role = payload.get("role", "approver_1")
    name = payload.get("name", "Approver")
    res = db.sign_payout_approval(payout_id=payout_id, approver_role=role, approver_name=name, approve=False)
    if not res:
        raise HTTPException(status_code=404, detail="Payout request not found")
    return {"success": True, "payout": res}

@app.get("/api/audit-log")
def get_audit_log():
    return db.get_audit_log()

@app.get("/api/public/transparency")
def get_public_transparency():
    return db.get_public_transparency()

@app.post("/api/agent/chat", response_model=AgentChatResponse)
def agent_chat(req: AgentChatRequest):
    return treasurer_agent.process_chat(req)

@app.post("/api/agent/scan-receipt", response_model=ReceiptAnalysisResult)
def scan_receipt(payload: Dict[str, Any] = Body(...)):
    receipt_key = payload.get("receipt_key", "venue_receipt")
    custom_ocr = payload.get("custom_ocr", None)
    return receipt_scanner.analyze_receipt(receipt_key_or_text=custom_ocr or receipt_key)

@app.post("/api/agent/upload-receipt", response_model=ReceiptAnalysisResult)
def upload_receipt(payload: Dict[str, Any] = Body(...)):
    filename = payload.get("filename", "custom_receipt.png")
    file_base64 = payload.get("file_base64", "")
    api_key = payload.get("api_key", None)
    return receipt_scanner.analyze_uploaded_image(file_base64=file_base64, filename=filename, api_key=api_key)

@app.get("/api/settings/keys")
def get_settings_keys():
    key = os.environ.get("GEMINI_API_KEY", "")
    is_configured = bool(key and len(key.strip()) > 5)
    masked = (key[:4] + "..." + key[-4:]) if is_configured and len(key) > 8 else ("Configured" if is_configured else "Not Configured")
    return {
        "gemini_configured": is_configured,
        "masked_key": masked,
        "model": "Gemini 1.5 Flash (Multimodal Vision)"
    }

@app.post("/api/settings/keys")
def save_settings_keys(payload: Dict[str, Any] = Body(...)):
    key = payload.get("gemini_api_key", "").strip()
    if key:
        os.environ["GEMINI_API_KEY"] = key
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        try:
            lines = []
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            new_lines = [l for l in lines if not l.startswith("GEMINI_API_KEY=")]
            new_lines.append(f"GEMINI_API_KEY={key}\n")
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        except Exception:
            pass
    return {"success": True, "gemini_configured": bool(key)}

@app.get("/api/paypal/developer-trace")
def get_paypal_developer_trace():
    return {
        "sandbox_environment": "https://api-m.sandbox.paypal.com",
        "client_id": "AVZ...94a1 (Sandbox Active)",
        "invoicing_api": {
            "endpoint": "POST /v2/invoicing/invoices",
            "headers": {
                "Authorization": "Bearer A21AA...sandbox_token",
                "Content-Type": "application/json",
                "PayPal-Request-Id": "inv-batch-req-88421a"
            },
            "payload_sample": {
                "detail": {
                    "currency_code": "INR",
                    "note": "Hackathon 2026 Registration Dues",
                    "payment_term": {"term_type": "DUE_ON_RECEIPT"}
                },
                "invoicer": {"name": {"given_name": "Club Treasurer AI"}},
                "primary_recipients": [{"billing_info": {"name": {"given_name": "Rahul Sharma"}}}]
            }
        },
        "payouts_api": {
            "endpoint": "POST /v1/payments/payouts",
            "headers": {
                "Authorization": "Bearer A21AA...sandbox_token",
                "Content-Type": "application/json",
                "PayPal-Request-Id": "pay-idem-90141f-batch"
            },
            "payload_sample": {
                "sender_batch_header": {
                    "sender_batch_id": "BATCH-PAYPAL-474C1CE6",
                    "email_subject": "Approved Club Expense Reimbursement"
                },
                "items": [{
                    "recipient_type": "EMAIL",
                    "amount": {"value": "3200.00", "currency": "INR"},
                    "receiver": "accounts@grandauditorium.com",
                    "note": "Auditorium Hall deposit - Dual approved by President and VP"
                }]
            }
        },
        "webhook_verification": {
            "endpoint": "POST /v1/notifications/verify-webhook-signature",
            "headers": {
                "PayPal-Auth-Algo": "SHA256withRSA",
                "PayPal-Transmission-Id": "wh-trans-00921a83",
                "PayPal-Transmission-Sig": "kL993...mN44=="
            },
            "status": "VERIFIED_AUTHENTIC"
        }
    }

@app.get("/api/telegram/messages")
def get_telegram_messages():
    return db.get_telegram_messages()

@app.post("/api/telegram/callback")
def telegram_callback(payload: Dict[str, Any] = Body(...)):
    payout_id = payload.get("payout_id")
    action = payload.get("action")
    role = payload.get("role", "approver_1")
    name = payload.get("name", "Telegram Approver")
    
    approve = (action != "reject")
    res = db.sign_payout_approval(payout_id=payout_id, approver_role=role, approver_name=name, approve=approve)
    if not res:
        raise HTTPException(status_code=404, detail="Payout request not found")
    return {"success": True, "payout": res, "telegram_messages": db.get_telegram_messages()}

@app.post("/api/paypal/capture")
def paypal_capture(payload: Dict[str, Any] = Body(...)):
    order_id = payload.get("order_id", "TEST_ORDER_999")
    invoice_id = payload.get("invoice_id")
    amount = float(payload.get("amount", 500.0))
    payer_name = payload.get("payer_name", "Sandbox Student")
    payer_email = payload.get("payer_email", "student.sandbox@example.com")
    
    inv = db.capture_paypal_order(order_id=order_id, invoice_id=invoice_id, amount=amount, payer_name=payer_name, payer_email=payer_email)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"success": True, "invoice": inv, "message": f"PayPal Order #{order_id} captured successfully."}

@app.get("/api/analytics")
def get_analytics():
    status = db.get_treasury_status()
    cat_labels = [c.name for c in status.categories]
    cat_spent = [c.spent for c in status.categories]
    cat_remaining = [c.remaining for c in status.categories]
    cat_allocated = [c.allocated for c in status.categories]
    
    return {
        "categories": {
            "labels": cat_labels,
            "spent": cat_spent,
            "remaining": cat_remaining,
            "allocated": cat_allocated
        },
        "burn_trend": {
            "timeline": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5 (Today)", "Day 6 (Projected)", "Day 7 (Projected)"],
            "spent": [200, 650, 1100, 1550, status.total_spent, status.total_spent + 3200, status.total_spent + 4500],
            "collected": [500, 1000, 1000, status.total_collected, status.total_collected, 2500, 2500]
        },
        "metrics": {
            "budget_utilization_pct": round((status.total_spent / status.total_budget * 100) if status.total_budget else 0, 1),
            "collection_progress_pct": round((status.total_collected / 2500 * 100), 1),
            "guardrail_blocks_count": len([a for a in db.get_audit_log() if a.severity.value == "ALERT"])
        }
    }

@app.get("/api/sample-receipts")
def get_sample_receipts():
    return SAMPLE_RECEIPTS

@app.post("/api/state/reset")
def reset_state():
    db.reset_to_seed_data()
    return {"success": True, "message": "Demo state reset to initial baseline."}

# Mount static frontend directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

