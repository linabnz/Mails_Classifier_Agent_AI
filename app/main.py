import time
from typing import List
from fastapi import FastAPI
from groq import RateLimitError

from .config import settings
from .gmail_client import authenticate_gmail, get_all_emails
from .groq_client import TicketClassifier
from .sheets_client import SheetWriter
from .models import ProcessResult, ProcessResponse

print(f"🔑 GROQ_API_KEY : {'OK' if settings.groq_api_key else '❌ MISSING'}")

app = FastAPI(
    title   = "Email ticket classification agent",
    version = "1.0.0",
)

gmail_service = authenticate_gmail()
classifier    = TicketClassifier()
csv_writer    = SheetWriter()

BATCH_SIZE = 20


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/process_all_emails", response_model=ProcessResponse)
def process_all_emails():
    emails    = get_all_emails(gmail_service)
    total     = len(emails)
    processed: List[ProcessResult] = []

    print(f"\n📨 PROCESSING START: {total} emails\n")

    for index, mail in enumerate(emails):
        subject = mail["subject"]
        body    = mail["body"]

        print(f"\n--- Email {index + 1}/{total} ---")
        print(f"📩 Subject: {subject}")

        while True:
            try:
                result = classifier.classify(subject, body)
                break
            except RateLimitError:
                print("⏳ Groq rate limit — waiting 30s...")
                time.sleep(30)

        categorie = result["categorie"]
        urgence   = result["urgence"]
        resume    = result["resume"]

        print(f"📌 Category: {categorie}")
        print(f"⚠️  Urgency: {urgence}")
        print(f"📝 Summary: {resume[:120]}...")

        csv_writer.append_ticket(categorie, subject, urgence, resume)
        print("✅ Saved.")

        processed.append(ProcessResult(
            subject      = subject,
            body_preview = body[:200],
            categorie    = categorie,
            urgence      = urgence,
            resume       = resume,
        ))

        if (index + 1) % BATCH_SIZE == 0:
            print(f"\n⏸️  Waiting 5s...\n")
            time.sleep(5)

    print("\n🎉 PROCESSING COMPLETE.\n")
    return ProcessResponse(total_emails=total, processed=processed)