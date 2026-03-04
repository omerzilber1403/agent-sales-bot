from .connection import init_db as _create_tables, SessionLocal
from ..models.company import Company
import secrets


def init_db():
    """Initialize database tables (creates all schema if not exists)."""
    _create_tables()


def seed_demo_company():
    """Insert the Forcepoint Demo company if it doesn't already exist.

    Safe to call on every startup — checks for the demo domain first.
    """
    db = SessionLocal()
    try:
        exists = db.query(Company).filter(
            Company.domain == "forcepoint-demo.example.com"
        ).first()
        if exists:
            print("Demo company already seeded — skipping.")
            return

        company = Company(
            name="Forcepoint Demo",
            domain="forcepoint-demo.example.com",
            api_key=f"ak_{secrets.token_urlsafe(32)}",
            locale="en-US",
            timezone="UTC",
            currency="USD",
            business_type="B2B",
            one_line_value=(
                "AI-native data security that stops breaches before they happen "
                "— without slowing your team down."
            ),
            products=[
                {
                    "id": "platform",
                    "name": "AI-Native Data Security Platform",
                    "summary": (
                        "Real-time data protection powered by behavioral AI — "
                        "covers endpoint, cloud, email, and network in one platform."
                    ),
                    "base_price": "Contact for pricing",
                    "addons": "CASB integration, DLP module, insider threat detection",
                }
            ],
            pain_points=[
                "data leaks via email and cloud storage",
                "insider threats going undetected for months",
                "compliance violations (GDPR, HIPAA, SOC 2, FedRAMP)",
                "legacy DLP tools generating thousands of false positives daily",
            ],
            handoff_rules={
                "triggers": [
                    "pricing negotiation",
                    "enterprise contract",
                    "legal questions",
                    "security assessment",
                    "competitor comparison",
                ],
                "target_queue": "sales-team",
                "user_msg_on_handoff": (
                    "I'm connecting you with a Forcepoint security expert "
                    "who will be in touch shortly."
                ),
            },
            faq_kb_refs=[
                {
                    "q": "What is Forcepoint?",
                    "a": (
                        "Forcepoint is an AI-native cybersecurity company specializing "
                        "in data security and insider threat protection across endpoint, "
                        "cloud, and network environments."
                    ),
                },
                {
                    "q": "How does the AI work?",
                    "a": (
                        "Forcepoint's behavioral AI continuously learns normal user and "
                        "data-access patterns, then detects anomalies in real-time — "
                        "blocking real threats while letting legitimate work flow."
                    ),
                },
                {
                    "q": "Which compliance standards do you support?",
                    "a": (
                        "GDPR, CCPA, HIPAA, SOC 2, ISO 27001, and FedRAMP — "
                        "with built-in policy templates and automated audit trails."
                    ),
                },
                {
                    "q": "Can it protect data in the cloud?",
                    "a": (
                        "Yes — native integrations with Microsoft 365, Google Workspace, "
                        "Salesforce, and all major cloud storage providers to enforce "
                        "data policies wherever your data lives."
                    ),
                },
                {
                    "q": "How is this different from traditional DLP?",
                    "a": (
                        "Traditional DLP uses static rules and generates massive false-positive "
                        "rates. Forcepoint understands intent using behavioral AI — stopping "
                        "real threats without blocking employees from doing their jobs."
                    ),
                },
                {
                    "q": "What does onboarding look like?",
                    "a": (
                        "Typical enterprise deployment takes 2–4 weeks: policy mapping, "
                        "connector setup, and tuning. A dedicated customer success engineer "
                        "guides every step."
                    ),
                },
            ],
            brand_voice={
                "style": "professional, confident, concise, security-expert tone",
                "emoji_policy": "none",
                "closing_tone": "offer_demo_or_call",
            },
        )

        db.add(company)
        db.commit()
        print("✅ Forcepoint Demo company seeded successfully.")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Seeding demo data...")
    seed_demo_company()
    print("Done!")
