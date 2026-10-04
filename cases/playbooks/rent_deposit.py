from .base import Channel, Playbook, Step

RENT_DEPOSIT = Playbook(
    key="rent_deposit",
    name="Rent deposit not returned",
    summary=(
        "Ask in writing, give a final written demand, then claim it yourself in the Small Claims Court "
        "(claims up to KES 1,000,000, no lawyer needed, decided within 60 days of filing)."
    ),
    categories=["RENT_DEPOSIT"],
    evidence_checklist=[
        "Tenancy agreement (or proof of an oral tenancy: rent receipts, messages)",
        "Proof you paid the deposit: receipt, M-Pesa message or bank slip",
        "Photos or video of the house when you moved in and when you moved out, with dates",
        "Your notice to vacate and the key handover acknowledgement",
        "Rent statement or receipts showing you owed no rent",
        "Final water and electricity bills or meter readings",
        "Every message with the landlord or agent about the deposit",
        "The landlord's correct full name and address (needed to file and serve a claim)",
    ],
    steps=[
        Step(
            key="move_out_records",
            title="Gather your move-out records",
            guidance=[
                "Add your agreement, deposit receipt and move-out photos to the evidence tab.",
                "If the landlord did a handover inspection, note the date and anything they said was damaged.",
                "Find the landlord's correct legal name and physical address. A claim against the wrong name cannot be enforced.",
            ],
        ),
        Step(
            key="written_request",
            title="Ask for the deposit back in writing",
            guidance=[
                "Send a polite written request with the amount, the date you moved out and how to pay you.",
                "If they intend to deduct anything, ask them to list each deduction with receipts or photos.",
                "Kenyan law sets no fixed refund deadline, so give a clear one yourself (14 days is usual).",
            ],
            letter="deposit_request",
        ),
        Step(
            key="final_demand",
            title="Send a final written demand",
            guidance=[
                "If there is no refund by your deadline, send a final demand giving 14 more days.",
                "Dispute any deduction that is normal wear and tear or has no receipt.",
                "Keep proof of delivery: the sent email, a WhatsApp delivery tick, or a signed copy.",
            ],
            letter="deposit_demand",
            wait_days=14,
        ),
        Step(
            key="small_claims",
            title="File your own claim in the Small Claims Court",
            guidance=[
                "Use the Small Claims Court for deposits up to KES 1,000,000. You file it yourself; no lawyer is needed.",
                "File Form SCC 1 on the Judiciary e-filing portal and pay the filing fee by M-Pesa "
                "(fees start from about KES 200 and depend on the amount).",
                "Attach your evidence bundle from this case. The court must decide within 60 days of filing.",
                "Other forums: the Rent Restriction Tribunal only covers homes with rent of KES 2,500 a month or less; "
                "the Business Premises Rent Tribunal covers shops and offices. Claims over KES 1,000,000 go to the "
                "Magistrates' Court.",
                "Time limit: a claim for money owed under a contract must be brought within 6 years.",
            ],
            wait_days=14,
            escalation=True,
            channels=[
                Channel("Judiciary e-filing portal", "https://efiling.court.go.ke", "url"),
                Channel("Small Claims Court information", "https://judiciary.go.ke", "url"),
            ],
        ),
        Step(
            key="serve_and_hearing",
            title="Serve the claim and attend the hearing",
            guidance=[
                "Serve the claim on the landlord in person (or by registered post if that fails), then file proof of "
                "service (Form SCC 5). You have 6 months to serve.",
                "The landlord has 14 days to respond. Bring your evidence bundle and originals to the hearing.",
                "Only you, a close relative the court approves, or an advocate can speak for you in court.",
            ],
            wait_days=7,
        ),
        Step(
            key="enforce",
            title="Collect the money if you win",
            guidance=[
                "If the landlord does not pay after judgment, ask the court how to enforce it (for example by attaching property).",
                "Record the payment here and close the case.",
            ],
            wait_days=30,
        ),
    ],
    sources=[
        Channel("Small Claims Court Act, 2016", "https://kenyalaw.org", "url"),
        Channel("Judiciary e-filing", "https://efiling.court.go.ke", "url"),
    ],
    reviewed_on="October 2026 (needs review by a Kenyan advocate before launch)",
)
