from .base import Channel, Playbook, Step

GENERAL = Playbook(
    key="general",
    name="General complaint",
    summary="For any organisation: ask in writing, keep records, chase, then escalate to the body that oversees them.",
    categories=["BANK", "INSURANCE", "EMPLOYER", "EDUCATION", "MERCHANT", "TRAVEL", "OTHER"],
    evidence_checklist=[
        "Proof of payment or the transaction (receipt, M-Pesa message, bank statement)",
        "Your contract, policy, offer letter or terms",
        "Every reference or ticket number they gave you",
        "Messages and emails between you and them, with dates",
        "Photos or screenshots of the problem",
    ],
    steps=[
        Step(
            key="first_contact",
            title="Raise it with them and get a reference number",
            guidance=[
                "Call, visit or message their customer care and explain the problem.",
                "Ask for a ticket or reference number and the name of the person you spoke to.",
                "Write the reference into this case so every later letter quotes it.",
            ],
        ),
        Step(
            key="written_complaint",
            title="Send a written complaint",
            guidance=[
                "Put the complaint in writing so there is a dated record.",
                "Say exactly what you want them to do and give a clear deadline (14 days is reasonable).",
                "Send it by email if you can, and keep the sent copy.",
            ],
            letter="complaint",
        ),
        Step(
            key="follow_up",
            title="Follow up if they have not resolved it",
            guidance=[
                "If the deadline passes without a proper answer, send a short follow-up quoting your earlier letter.",
                "Ask who you can escalate to inside the organisation (complaints manager, ombudsman unit).",
            ],
            letter="follow_up",
            wait_days=14,
        ),
        Step(
            key="escalate",
            title="Escalate to the body that oversees them",
            guidance=[
                "Banks: Central Bank of Kenya. Insurance: Insurance Regulatory Authority. Public offices: the "
                "Commission on Administrative Justice (Office of the Ombudsman). Unfair trade or bad goods: the "
                "Competition Authority of Kenya. Employers: the County Labour Office.",
                "Attach your evidence bundle and copies of your letters. Regulators usually ask for proof that "
                "you complained to the organisation first.",
            ],
            letter="escalation",
            wait_days=7,
            escalation=True,
            channels=[
                Channel("Office of the Ombudsman (public offices)", "https://www.ombudsman.go.ke", "url"),
                Channel("Central Bank of Kenya (banks)", "https://www.centralbank.go.ke", "url"),
                Channel("Insurance Regulatory Authority", "https://www.ira.go.ke", "url"),
                Channel("Competition Authority of Kenya (consumer complaints)", "https://www.cak.go.ke", "url"),
            ],
        ),
        Step(
            key="legal_help",
            title="Consider legal help if it is still unresolved",
            guidance=[
                "For money claims up to the Small Claims Court limit you can file without a lawyer.",
                "Free legal aid: National Legal Aid Service, Kituo cha Sheria, or the Law Society's pro bono desks.",
                "Fuatilia helps you organise your case; it is not a law firm and does not give legal advice.",
            ],
            wait_days=14,
        ),
    ],
)
