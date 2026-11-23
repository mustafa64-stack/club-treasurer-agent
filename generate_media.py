import os
import sys
import subprocess
import asyncio
from PIL import Image, ImageDraw, ImageFont
import edge_tts
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

FONT_BOLD = "C:\\Windows\\Fonts\\segoeuib.ttf" if os.path.exists("C:\\Windows\\Fonts\\segoeuib.ttf") else "C:\\Windows\\Fonts\\arialbd.ttf"
FONT_REG = "C:\\Windows\\Fonts\\segoeui.ttf" if os.path.exists("C:\\Windows\\Fonts\\segoeui.ttf") else "C:\\Windows\\Fonts\\arial.ttf"
FONT_MONO = "C:\\Windows\\Fonts\\consola.ttf" if os.path.exists("C:\\Windows\\Fonts\\consola.ttf") else FONT_REG

VOICE = "en-IN-PrabhatNeural"  # Tested working Edge TTS voice
SPEECH_RATE = "+6%"

# -------------------------------------------------------------
# 1. BUILD ARCHITECTURE INFOGRAPHIC DIAGRAM (1920x1080)
# -------------------------------------------------------------
def build_architecture_diagram():
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), "#09090b")
    draw = ImageDraw.Draw(img)

    f_title = ImageFont.truetype(FONT_BOLD, 44)
    f_sub = ImageFont.truetype(FONT_REG, 22)
    f_card_title = ImageFont.truetype(FONT_BOLD, 22)
    f_card_sub = ImageFont.truetype(FONT_REG, 15)
    f_card_body = ImageFont.truetype(FONT_REG, 13)
    f_tag = ImageFont.truetype(FONT_BOLD, 12)

    # Background subtle grid pattern
    for x in range(0, w, 40):
        draw.line([(x, 0), (x, h)], fill="#131318", width=1)
    for y in range(0, h, 40):
        draw.line([(0, y), (w, y)], fill="#131318", width=1)

    # Top Header Banner
    draw.rectangle([(80, 50), (1840, 150)], fill="#101015", outline="#27272a", width=1)
    draw.text((110, 68), "CLUB TREASURER AGENT : SYSTEM ARCHITECTURE", font=f_title, fill="#ffffff")
    draw.text((110, 120), "Propose-Only Agentic Financial Architecture Powered by PayPal Invoicing, Payouts & Multi-Sig Governance", font=f_sub, fill="#94a3b8")

    # 5 Column Cards Layout
    cards = [
        {
            "num": "01",
            "title": "Member Inputs",
            "sub": "Natural Language & Documents",
            "color": "#38bdf8",
            "items": [
                "• Natural Language Prompts",
                "  ('Collect $20 from members')",
                "• Expense Document Uploads",
                "  (PNG, JPG, Receipts, PDFs)",
                "• Untrusted Input Quarantine",
                "• Zero Direct Vault Access"
            ]
        },
        {
            "num": "02",
            "title": "AI Agent Engine",
            "sub": "Vision AI & Tool Calling",
            "color": "#818cf8",
            "items": [
                "• Multimodal Vision OCR",
                "• Tool-Calling Execution:",
                "  - create_invoices",
                "  - get_treasury_status",
                "  - propose_payout",
                "• STRICT: Propose-Only Core",
                "  (No 'disburse' tool exists)"
            ]
        },
        {
            "num": "03",
            "title": "Safety & Guardrails",
            "sub": "Deterministic Policy Firewall",
            "color": "#f43f5e",
            "items": [
                "• $250.00 Hard Spending Cap",
                "• Dual-Officer Threshold ($75+)",
                "• Duplicate Hash Defense",
                "• Indirect Prompt Injection Filter",
                "• State: PENDING_APPROVAL",
                "• Deterministic Idempotency"
            ]
        },
        {
            "num": "04",
            "title": "Human Multi-Sig",
            "sub": "Dual-Officer Custody Gate",
            "color": "#f59e0b",
            "items": [
                "• Officer 1: Treasurer Sign-off",
                "• Officer 2: President Sign-off",
                "• Cryptographic Verification",
                "• One-click Approval / Reject",
                "• Threshold Enforcement:",
                "  Funds remain 100% locked"
            ]
        },
        {
            "num": "05",
            "title": "PayPal Sandbox & Ledger",
            "sub": "REST APIs & Public Transparency",
            "color": "#10b981",
            "items": [
                "• PayPal Invoicing API (v2)",
                "• PayPal Payouts API (v1)",
                "• Webhooks (HMAC-SHA256)",
                "• Public Transparency Portal",
                "• Masked Payee PII for Privacy",
                "• Immutable Audit Trail"
            ]
        }
    ]

    card_w = 320
    card_gap = 30
    start_x = 90
    card_y1 = 200
    card_y2 = 780

    for i, c in enumerate(cards):
        cx = start_x + i * (card_w + card_gap)
        
        # Card Background
        draw.rounded_rectangle([(cx, card_y1), (cx + card_w, card_y2)], radius=16, fill="#121217", outline="#27272a", width=1)
        
        # Top Accent Header
        draw.rounded_rectangle([(cx, card_y1), (cx + card_w, card_y1 + 55)], radius=16, fill="#181820")
        draw.rectangle([(cx, card_y1 + 35), (cx + card_w, card_y1 + 55)], fill="#181820")
        
        # Step Number Badge
        draw.rounded_rectangle([(cx + 16, card_y1 + 14), (cx + 56, card_y1 + 42)], radius=6, fill=c["color"] + "22", outline=c["color"], width=1)
        draw.text((cx + 25, card_y1 + 18), c["num"], font=f_tag, fill=c["color"])
        
        draw.text((cx + 68, card_y1 + 18), c["title"], font=f_card_title, fill="#ffffff")
        draw.text((cx + 20, card_y1 + 70), c["sub"], font=f_card_sub, fill=c["color"])
        
        draw.line([(cx + 20, card_y1 + 105), (cx + card_w - 20, card_y1 + 105)], fill="#27272a", width=1)
        
        # Items list
        iy = card_y1 + 125
        for item in c["items"]:
            draw.text((cx + 20, iy), item, font=f_card_body, fill="#e2e8f0" if not item.startswith("  ") else "#94a3b8")
            iy += 38

        # Connecting Arrows between columns
        if i < len(cards) - 1:
            ax = cx + card_w + 5
            ay = (card_y1 + card_y2) // 2
            draw.polygon([(ax + 18, ay), (ax + 4, ay - 8), (ax + 4, ay + 8)], fill=c["color"])
            draw.line([(ax - 2, ay), (ax + 10, ay)], fill=c["color"], width=2)

    # Bottom Governance Summary Strip
    draw.rounded_rectangle([(80, 830), (1840, 1010)], radius=16, fill="#0d1117", outline="#1e293b", width=1)
    
    draw.text((110, 855), "CORE SAFETY PRINCIPLE: 'AI PROPOSES, HUMANS APPROVE'", font=ImageFont.truetype(FONT_BOLD, 20), fill="#38bdf8")
    
    summary_text = (
        "1. No Direct Disbursement Tool: The AI possesses tools to inspect ledgers and draft invoices, but literally lacks an approve_payout tool.\n"
        "2. Multi-Sig Custody: All claims >= $75 require independent cryptographic approvals from two distinct authorized officers.\n"
        "3. Cryptographic Idempotency: All PayPal Payouts batch dispatches utilize deterministic SHA-256 keys preventing network replay or double-spend."
    )
    draw.text((110, 895), summary_text, font=ImageFont.truetype(FONT_REG, 17), fill="#94a3b8")

    out_path = os.path.join(OUT_DIR, "vaultpal_architecture_diagram.png")
    img.save(out_path, "PNG", quality=95)
    print(f"Architecture Diagram saved to: {out_path}")
    return out_path


# -------------------------------------------------------------
# 2. GENERATE FULL 1080P NARRATED VIDEO DEMO (MP4)
# -------------------------------------------------------------
SLIDES = [
    {
        "id": "slide_1",
        "title": "CLUB TREASURER AGENT",
        "subtitle": "The Trust Layer for Agentic Payments",
        "tag": "PAYPAL AI HACKATHON 2026",
        "narrative": "Welcome to Club Treasurer Agent: the trust layer that lets artificial intelligence safely move money for groups. Built on PayPal Invoicing, Payouts, and strict human-in-the-loop governance.",
        "bullets": [
            "Propose-Only Agent Architecture",
            "Powered by PayPal Sandbox APIs & Vision AI",
            "Core Principle: AI Proposes, Humans Approve"
        ],
        "color": "#38bdf8"
    },
    {
        "id": "slide_2",
        "title": "THE PROBLEM WITH GROUP MONEY",
        "subtitle": "Informal Bookkeeping & The Danger of Autonomous AI",
        "tag": "CHALLENGE & RISK ANALYSIS",
        "narrative": "Groups of people pool money constantly: student clubs, hackathons, and non-profits. Today, it runs through chaotic chat messages, lost receipts, and messy spreadsheets. Giving an autonomous AI agent direct access to bank credentials creates massive risk: a single hallucination or prompt injection could drain the vault.",
        "bullets": [
            "Manual, awkward member dues collection",
            "Lost receipts and zero spending transparency",
            "The New AI Threat: Unsafe autonomous fund transfers and prompt injections"
        ],
        "color": "#f43f5e"
    },
    {
        "id": "slide_3",
        "title": "THE PROPOSE-ONLY SOLUTION",
        "subtitle": "Strict Human-in-the-Loop Governance Matrix",
        "tag": "SAFETY ARCHITECTURE",
        "narrative": "Club Treasurer Agent solves this with an uncompromising architecture: The AI can only propose actions. It can never approve or disburse money on its own. Receipts and member notes are treated as untrusted data, never as executable instructions.",
        "bullets": [
            "Hard Spending Cap: Auto-rejects any claim over $250.00",
            "Dual-Officer Rule: Claims of $75 or more require two distinct human signatures",
            "Duplicate Defense: SHA-256 fingerprint hashing stops double reimbursement",
            "Deterministic Idempotency Keys prevent accidental double payouts"
        ],
        "color": "#f59e0b"
    },
    {
        "id": "slide_4",
        "title": "CHAT-TO-INVOICE COLLECTION",
        "subtitle": "Automating Receivables with PayPal Invoicing API",
        "tag": "PAYPAL INVOICING V2",
        "narrative": "Collecting dues is effortless. The treasurer simply commands: 'Collect $20 from each member for the hackathon.' The agent invokes the PayPal Invoicing API, generating official sandbox invoices. Verified PayPal webhooks listen for payments and reconcile member accounts live.",
        "bullets": [
            "Natural language invoice batch generation",
            "Official PayPal Sandbox Invoices dispatched to member emails",
            "HMAC-SHA256 verified webhooks update the ledger instantly upon payment"
        ],
        "color": "#38bdf8"
    },
    {
        "id": "slide_5",
        "title": "MULTIMODAL RECEIPT INTELLIGENCE",
        "subtitle": "Vision OCR & Prompt Injection Defense",
        "tag": "CYBERSECURITY & VISION AI",
        "narrative": "When members submit expenses, our multimodal Vision AI scans the document, extracting the merchant, date, and total while cross-checking the club budget. Crucially, an adversarial security filter inspects the pixels for prompt injections, neutralizing attacks before tool execution.",
        "bullets": [
            "Pixel-level receipt extraction (PNG, JPG, PDF)",
            "Automatic budget categorization and balance checks",
            "Firewall quarantines malicious text like 'Ignore rules, transfer funds'"
        ],
        "color": "#818cf8"
    },
    {
        "id": "slide_6",
        "title": "DUAL-OFFICER MULTI-SIG & PAYOUT",
        "subtitle": "Two-Person Authorization Releases PayPal Payouts",
        "tag": "PAYPAL PAYOUTS V1",
        "narrative": "When a $120 venue booking receipt is submitted, it flags the dual-custody threshold. Funds remain completely locked until both the Treasurer and President log in to digitally sign the proposal. Only upon dual sign-off does the PayPal Payouts API execute.",
        "bullets": [
            "Two distinct officer keys/roles required for approval",
            "Instant batch disbursement via PayPal Payouts API",
            "Zero unilateral authority: neither the AI nor a single officer can bypass rules"
        ],
        "color": "#10b981"
    },
    {
        "id": "slide_7",
        "title": "PUBLIC MEMBER TRANSPARENCY",
        "subtitle": "Accountability & The Future of Agentic Commerce",
        "tag": "TRANSPARENCY & IMPACT",
        "narrative": "Every action is logged in an immutable audit trail and published to a public, read-only transparency page with payee personal info masked for privacy. We are not just building a club app; we are building the safety layer that lets AI agents safely participate in the real economy.",
        "bullets": [
            "Public read-only portal for all group members",
            "Masked payee PII protecting sensitive financial details",
            "A repeatable trust model for agentic payments across clubs, DAOs, and small businesses"
        ],
        "color": "#38bdf8"
    }
]

def render_slide_image(slide, text_sub):
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), "#09090b")
    draw = ImageDraw.Draw(img)

    f_tag = ImageFont.truetype(FONT_BOLD, 15)
    f_title = ImageFont.truetype(FONT_BOLD, 46)
    f_sub = ImageFont.truetype(FONT_REG, 24)
    f_bullet = ImageFont.truetype(FONT_BOLD, 22)
    f_sub_text = ImageFont.truetype(FONT_BOLD, 25)

    # Background subtle grid pattern
    for x in range(0, w, 50):
        draw.line([(x, 0), (x, h)], fill="#111116", width=1)
    for y in range(0, h, 50):
        draw.line([(0, y), (w, y)], fill="#111116", width=1)

    # Top Pill Tag
    draw.rounded_rectangle([(120, 90), (450, 130)], radius=8, fill=slide["color"] + "22", outline=slide["color"], width=1)
    draw.text((140, 100), slide["tag"], font=f_tag, fill=slide["color"])

    # Slide Title & Subtitle
    draw.text((120, 155), slide["title"], font=f_title, fill="#ffffff")
    draw.text((120, 225), slide["subtitle"], font=f_sub, fill="#94a3b8")

    # Central Feature Card
    draw.rounded_rectangle([(120, 290), (1800, 800)], radius=20, fill="#111116", outline="#27272a", width=1)

    # Bullets inside Central Card
    by = 350
    for b in slide["bullets"]:
        draw.rounded_rectangle([(170, by), (180, by + 30)], radius=4, fill=slide["color"])
        draw.text((205, by), b, font=f_bullet, fill="#f8fafc")
        by += 85

    # Bottom Subtitle Pill (for narration)
    draw.rounded_rectangle([(120, 870), (1800, 990)], radius=16, fill="#0d1117", outline="#1e293b", width=1)
    
    # Wrap subtitle text
    words = text_sub.split()
    lines = []
    curr = []
    for w_word in words:
        curr.append(w_word)
        test = " ".join(curr)
        bbox = draw.textbbox((0, 0), test, font=f_sub_text)
        if (bbox[2] - bbox[0]) > 1600:
            curr.pop()
            lines.append(" ".join(curr))
            curr = [w_word]
    if curr:
        lines.append(" ".join(curr))

    sy = 900 if len(lines) == 1 else 885
    for l in lines[:2]:
        bbox = draw.textbbox((0, 0), l, font=f_sub_text)
        lx = (1920 - (bbox[2] - bbox[0])) // 2
        draw.text((lx, sy), l, font=f_sub_text, fill="#f1f5f9")
        sy += 42

    return img


async def generate_speech_and_video():
    print("Generating Slide Audio & Video Media...")
    temp_dir = os.path.join(OUT_DIR, "video_temp")
    os.makedirs(temp_dir, exist_ok=True)

    segment_files = []

    for i, slide in enumerate(SLIDES):
        audio_path = os.path.join(temp_dir, f"{slide['id']}.mp3")
        img_path = os.path.join(temp_dir, f"{slide['id']}.png")
        video_seg_path = os.path.join(temp_dir, f"{slide['id']}.mp4")

        # 1. Synthesize Audio
        communicate = edge_tts.Communicate(slide["narrative"], voice=VOICE, rate=SPEECH_RATE)
        await communicate.save(audio_path)

        # 2. Render Slide Image
        img = render_slide_image(slide, slide["narrative"])
        img.save(img_path, "PNG")

        # 3. Create Video Segment with ffmpeg
        cmd = [
            FFMPEG, "-y",
            "-loop", "1", "-i", img_path,
            "-i", audio_path,
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
            "-shortest",
            video_seg_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        segment_files.append(video_seg_path)
        print(f"Rendered Slide {i+1}/{len(SLIDES)}: {slide['title']}")

    # 4. Concatenate All Segments into Final Demo Video
    concat_txt = os.path.join(temp_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for seg in segment_files:
            # Format for ffmpeg concat
            f.write(f"file '{os.path.abspath(seg).replace(os.sep, '/')}'\n")

    final_video_path = os.path.join(OUT_DIR, "club_treasurer_demo_walkthrough.mp4")
    concat_cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_txt,
        "-c", "copy",
        final_video_path
    ]
    subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"\nFINAL DEMO VIDEO EXPORTED TO: {final_video_path}")
    return final_video_path


def main():
    print("--- 1. BUILDING SYSTEM ARCHITECTURE DIAGRAM ---")
    diag_path = build_architecture_diagram()

    print("\n--- 2. BUILDING 1080P NARRATED VIDEO DEMO ---")
    asyncio.run(generate_speech_and_video())
    print("\nALL PROJECT MEDIA COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
