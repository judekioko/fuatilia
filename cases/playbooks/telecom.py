from .base import Channel, Playbook, Step

CA_CHANNELS = [
    Channel("Communications Authority complaint form", "https://www.ca.go.ke/consumer-complaint", "url"),
    Channel("Email the Communications Authority", "chukuahatua@ca.go.ke", "email"),
    Channel("Communications Authority phone", "+254 703 042 700 or +254 730 172 700", "phone"),
]

TELECOM = Playbook(
    key="telecom",
    name="Phone, internet or airtime problem",
    summary=(
        "Complain to the provider in writing and get a reference number. They should resolve it within 21 days; "
        "if not, escalate to the Communications Authority of Kenya (CA)."
    ),
    categories=["TELECOM"],
    complaint_deadline_days=182,
    complaint_deadline_label="Complain to the provider in writing within 6 months of the problem.",
    complaint_step="provider_complaint",
    evidence_checklist=[
        "Your phone number or account number",
        "Screenshots of the wrong charge, deduction or balance",
        "Bills, statements or the SMS showing the charge",
        "The complaint reference number the provider gave you",
        "Dates and times of calls or chats with customer care",
    ],
    steps=[
        Step(
            key="provider_complaint",
            title="Complain to the provider and get a reference number",
            guidance=[
                "Call, chat or email customer care, or visit a shop. Ask for a complaint reference number. They should "
                "acknowledge within one working day.",
                "Put the complaint in writing so there is a dated record, and save the reference number in this case.",
                "Ask what their internal review (escalation) process is if you are not satisfied.",
            ],
            letter="telecom_complaint",
        ),
        Step(
            key="await_resolution",
            title="Wait for their answer (up to 21 days), then follow up",
            guidance=[
                "The Communications Authority expects providers to resolve complaints within 21 days.",
                "If they have not resolved it, send a follow-up quoting your reference and ask for an internal review.",
            ],
            letter="follow_up",
            wait_days=21,
        ),
        Step(
            key="escalate_ca",
            title="Escalate to the Communications Authority",
            guidance=[
                "Complain to CA using its online form or email. Include your reference number, a summary, what you want, "
                "and copies of your correspondence (use the evidence bundle).",
                "CA aims to acknowledge within 3 days. A provider must answer a complaint CA forwards within 21 days.",
                "If you are unhappy with how the provider handled it you can escalate before the 21 days are up.",
            ],
            letter="escalation",
            wait_days=1,
            escalation=True,
            channels=CA_CHANNELS,
        ),
        Step(
            key="ca_follow_up",
            title="Follow up with CA",
            guidance=[
                "If CA has not responded within about 10 days, follow up quoting the CA reference.",
                "For hidden or misleading charges you can also complain to the Competition Authority of Kenya "
                "(complain@cak.go.ke).",
                "If CA itself fails to act on your complaint, you can complain to the Office of the Ombudsman.",
            ],
            wait_days=10,
            channels=[
                Channel("Competition Authority of Kenya", "complain@cak.go.ke", "email"),
                Channel("Office of the Ombudsman", "https://cmis.ombudsman.go.ke", "url"),
            ],
        ),
    ],
    sources=[
        Channel("CA consumer complaints", "https://www.ca.go.ke/consumer-complaint", "url"),
        Channel("Kenya Information and Communications (Consumer Protection) Regulations, 2010", "https://kenyalaw.org", "url"),
    ],
    reviewed_on="October 2026 (needs review by a Kenyan advocate before launch)",
)

MOBILE_MONEY = Playbook(
    key="mobile_money",
    name="Mobile money problem",
    summary=(
        "Act fast: complain to the provider within 15 days. They have 30 days to resolve it; after that, appeal "
        "to the Central Bank of Kenya (CBK)."
    ),
    categories=["MOBILE_MONEY"],
    complaint_deadline_days=15,
    complaint_deadline_label="Complain to the provider within 15 days of the transaction.",
    complaint_step="written_complaint",
    evidence_checklist=[
        "The transaction confirmation message (paste it as evidence)",
        "Your mobile money statement for the period",
        "The provider's complaint or reversal reference number",
        "Screenshots of any failed transaction or wrong balance",
        "If it was fraud or a SIM swap: the police OB number",
    ],
    steps=[
        Step(
            key="reversal",
            title="Wrong number or failed transfer? Request a reversal now",
            guidance=[
                "M-Pesa: forward the confirmation SMS to 456, or dial *456# and choose reversal.",
                "Airtel Money: use the reversal option in the Airtel Money menu, or call customer care.",
                "Note the reversal or complaint reference number. If this was fraud or a SIM swap, call your provider "
                "to block the line and report to the police.",
            ],
            letter="reversal_request",
        ),
        Step(
            key="written_complaint",
            title="Lodge a written complaint (within 15 days)",
            guidance=[
                "If the reversal did not work, put the complaint in writing to the provider within 15 days of the "
                "transaction. Quote the transaction code and your reference number.",
                "The provider has 30 days to resolve it.",
            ],
            letter="complaint",
        ),
        Step(
            key="follow_up",
            title="Follow up before the 30 days run out",
            guidance=[
                "If there is no answer, follow up in writing and ask for their decision.",
                "Keep every reply; you will need the provider's decision (or proof of silence) to appeal to CBK.",
            ],
            letter="follow_up",
            wait_days=21,
        ),
        Step(
            key="appeal_cbk",
            title="Appeal to the Central Bank of Kenya",
            guidance=[
                "If the provider's decision is unsatisfactory, or 30 days pass without one, write to CBK with full "
                "details and copies of all correspondence (use the evidence bundle).",
                "CBK will not look at a matter that is already in court.",
                "For fraud or a SIM swap, also complain to the Communications Authority about the SIM replacement.",
            ],
            letter="escalation",
            wait_days=9,
            escalation=True,
            channels=[
                Channel("Central Bank of Kenya", "comms@centralbank.go.ke", "email"),
                Channel("Central Bank of Kenya phone", "+254 20 286 0000", "phone"),
                *CA_CHANNELS[:2],
            ],
        ),
    ],
    sources=[
        Channel("National Payment System Regulations, 2014 (regulations 39–40)", "https://kenyalaw.org", "url"),
        Channel("Central Bank of Kenya", "https://www.centralbank.go.ke", "url"),
    ],
    reviewed_on="October 2026 (needs review by a Kenyan advocate before launch)",
)
