# Telecom and mobile money disputes in Kenya: escalation playbook (research notes)

Researched 2026-10-04. Status tags: **[VERIFIED-PRIMARY]** = read in the official document itself; **[VERIFIED-SECONDARY]** = news or operator site only; **[UNVERIFIED]** = could not confirm.

---

## 0. Who has jurisdiction (routing table)

| Dispute type | Provider first | Regulator to escalate to | Legal basis |
|---|---|---|---|
| Wrong airtime/data charges, data bundle disputes, billing, unsolicited/premium subscriptions, network/QoS | Telco (Safaricom/Airtel/Telkom) | **Communications Authority of Kenya (CA)** | KICA (Consumer Protection) Regs 2010 reg 7; CA Consumer Protection Guidelines 2025 s.6.3–6.4 |
| SIM swap / unauthorised SIM replacement | Telco | **CA** (SIM security is a CA priority); plus police/DCI for the fraud itself | Same + KICA (Registration of SIM-Cards) Regs 2015 |
| Failed, reversed or wrongly sent M-Pesa/Airtel Money transfers, unauthorised wallet debits, M-Pesa charges | Mobile money provider (as a Payment Service Provider) | **Central Bank of Kenya (CBK)**: "the customer may appeal to the Bank" | National Payment System Regulations 2014 regs 38–40 |
| Bank-linked mobile products (M-Shwari, KCB M-Pesa, etc.) | Partner bank | **CBK** (bank complaints route) | CBK Prudential Guideline CBK/PG/22 |
| Charges not disclosed in advance, unconscionable conduct, misleading promotions (any sector) | Provider | **Competition Authority of Kenya (CAK)** Consumer Protection Dept (parallel or fallback route) | Competition Act s.55–56, s.70A |
| A regulator (CA/CBK) itself sits on your complaint | — | **Commission on Administrative Justice (Ombudsman)**, which covers public bodies only, never Safaricom/Airtel directly | CAJ Act 2011 |

Notes:
- In practice CA also accepts "Digital Financial Services and Mobile Money" complaints (110 in Q4 FY2025/26, mostly fraud and scams). So for fraud that runs through a SIM or telco channel, CA is a valid route. For disputes about the money transaction itself, the statutory appeal route is CBK. [VERIFIED-PRIMARY: CA Q4 report below; NPS Regs reg 40(5)]
- Safaricom's own guideline reportedly names CA for telecom escalation and CBK for M-Pesa disputes. [VERIFIED-SECONDARY: search snippet of https://www.safaricom.co.ke/images/Downloads/Safaricom-Complaint-Handling-Procedure.pdf. The PDF returned 403 to direct fetches, so the full text was not read.]

---

## 1. Step 1: complain to the provider

### Telecom (CA-regulated licensees)
- **Put it in writing within 6 months** of the incident: "A customer who wishes to lodge a complaint shall reduce the complaint in writing and lodge it within six months from the date of the incident" (reg 7(2)). [VERIFIED-PRIMARY] https://www.ca.go.ke/sites/default/files/2023-06/Consumer-Protection-Regulations-2010-1.pdf
- **Reference number**: every complaint "shall be acknowledged and issued with unique and easy to remember reference numbers" (Guidelines 6.3.1.1(i)). [VERIFIED-PRIMARY] https://www.ca.go.ke/sites/default/files/2025-03/Consumer%20Protection%20Guidelines%20and%20Customer%20Care%20Standards%202025.pdf
- **Acknowledgement within 1 working day**, or immediately if the complaint is filed interactively (call or chat) (6.3.1.1(ii); customer care standards table: "Acknowledgement of a complaint or enquiry: 1 working day"). [VERIFIED-PRIMARY, same URL]
- **Resolution standard: 21 days** (standards table: "Resolution of a complaint: 21 days"). [VERIFIED-PRIMARY, same URL]
- **Records preserved**: call data records and transaction data for a complaint must be kept while it is unresolved (6.3.1.2). Billing records must be kept until the dispute settles if the dispute starts within 12 months of the bill (6.10.4.5). The number under complaint must not be reassigned until the complaint is resolved (6.3.1.3–4). [VERIFIED-PRIMARY]
- **Internal escalation**: if dissatisfied, the licensee must offer an internal escalation where "a suitably qualified person" re-examines the decision (reg 7(8)). Complaint handling is free (reg 7(10)). A charge may apply only for retrieving records more than 12 months old, and only with the customer's agreement after referral to the regulator (reg 7(11)–(12)). [VERIFIED-PRIMARY, Regs 2010 URL]
- **Outage credits**: licensees must have an outage credit or rebate policy (Guidelines 6.12). [VERIFIED-PRIMARY]
- Safaricom's published "service resolution times": Voice 24h; Data 24–48h; Billing 24–48h; SIM card 6–72h; VAS 6–72h; **Financial services (M-PESA, Fuliza) 12–168h**. [VERIFIED-SECONDARY: operator site, last updated 30 Jul 2025] https://www.safaricom.co.ke/our-service-delivery

### Mobile money (CBK-regulated Payment Service Providers)
- **File with the PSP within 15 days of the occurrence**: "shall file such complaints with the payment service provider within a period of fifteen days from the date of occurrence" (NPS Regs 2014 reg 39(1)). **This is the tightest deadline in the playbook and the app must warn about it.** [VERIFIED-PRIMARY] https://www.centralbank.go.ke/images/docs/legislation/NPSRegulations2014.pdf
- The PSP must acknowledge the complaint and advise the expected actions and timing (reg 39(2)–(3)). The process is free (reg 39(7)). The PSP must have "a clear mechanism to address consumer complaints due to loss of funds through fraudulent means" (reg 38(c)). [VERIFIED-PRIMARY]
- **PSP must resolve within 30 days of filing** (reg 40(1)). A complaint reference number "may" be used (reg 40(3)). The PSP must tell the customer the outcome (reg 40(4)). [VERIFIED-PRIMARY]
- Caution: some secondary sites cite "60 days to resolve / 30 days to lodge" from CBK's **E-Money Regulations 2013**, which I could not confirm were ever gazetted. Use the NPS Regulations 2014 figures (15 days to file, 30 days to resolve). [UNVERIFIED status of the 2013 E-Money Regs] https://www.centralbank.go.ke/images/docs/NPS/Regulations%20and%20Guidelines/Regulations%20-%20E-%20Money%20regulations%202013.pdf
- **Self-service reversals (wrong recipient)**:
  - M-Pesa: forward the confirmation SMS to **456** or use *456# / *234# "Reverse Transaction", or call 100/200. Reversal needs the recipient's funds to still be there or the recipient's consent. [VERIFIED-SECONDARY] https://www.kenyans.co.ke/news/23381-safaricom-announces-how-reverse-m-pesa-transactions-sms. A "24-hour" window for the self-service SMS route is reported only by unofficial blogs. [UNVERIFIED]
  - Airtel Money: Airtel's own post gives dial *222# > My Account > Reverse wrong transaction, while blogs cite *334#; the code has changed over time. Airtel care: 100 or +254 733 100 100. [VERIFIED-SECONDARY] https://x.com/AIRTEL_KE/status/1196331777909903360 ; https://paybillke.com/guides/how-to-reverse-airtel-money
- Bank-linked products: the bank must acknowledge **within 48 hours** and undertake to resolve **within 7 days**, advising a timeline if it will take longer. [VERIFIED-PRIMARY] https://www.centralbank.go.ke/wp-content/uploads/2023/12/Customer-Complaints-Handling-Mechanism.pdf

### What the consumer should keep (evidence checklist)
- Provider complaint/ticket reference number and the date and time it was lodged (Guidelines 6.3.1.1; NPS reg 40(3)).
- Transaction codes (M-Pesa/Airtel Money confirmation SMS IDs), amounts, timestamps, recipient numbers.
- Screenshots of balance or data usage, bundle purchase SMS, bills or itemised statements.
- All correspondence with the provider and the provider's final response. CBK explicitly requires "copies of all relevant correspondence". (CBK mechanism PDF above)
- For SIM swap: the time service was lost, the police OB number, and the bank or wallet statements.
- CA's page lists: name and contact, description, relevant dates and times, "any reference numbers", supporting documents. [VERIFIED-PRIMARY] https://www.ca.go.ke/index.php/our-role-your-protection

---

## 2. Step 2: when the consumer may escalate

- **Telecom, to CA**: when "not satisfied with the manner in which a complaint was handled by a licensee or its resolution exceeded 21 days" (Guidelines 6.4.1). The Regulations say after going through the licensee's escalation process (reg 7(9)). Licensees must tell customers of this right (6.5.2). [VERIFIED-PRIMARY]
- **Mobile money, to CBK**: "Where a customer is not satisfied with the decision of the payment service provider regarding a complaint, the customer may appeal to the Bank" (reg 40(5)). Read with the 30-day resolution duty, escalation is available on an unsatisfactory decision or after 30 days without resolution (the second is an inference). The customer may also have "further recourse" under the Consumer Protection Act 2012 (reg 39(4)). [VERIFIED-PRIMARY]
- **Formal dispute before CA**: the consumer may ask CA to treat the complaint as a dispute (Guidelines 6.4.1). CA has discretion to accept it or handle it as a complaint (6.4.2). The process is under the KICA (Dispute Resolution) Regulations 2010 (see section 4). [VERIFIED-PRIMARY]

---

## 3. Step 3: escalation channels and regulator timelines

### Communications Authority of Kenya (CA)
- Online complaint form: https://www.ca.go.ke/consumer-complaint. The page returned "Access denied" to automated fetches but is the URL CA itself publishes.
- Email: **chukuahatua@ca.go.ke** (also complaints@ca.go.ke on the "Our Role" page)
- Hotlines (per Q4 FY2025/26 report): **+254 703 042 700; +254 730 172 700**. The "Our Role" page also lists +254 703 042 000, which is the general line.
- Walk-in: CA Centre, Waiyaki Way, Westlands. Letter: The Director-General, CA, P.O. Box 14448-00800 Nairobi. Also social media.
- Sources [VERIFIED-PRIMARY]: CA Q4 FY2025/26 Consumer Complaints report https://www.ca.go.ke/sites/default/files/2026-08/Consumer%20Complaints%20Statistics%20for%20Q4%20FY%202025-2026.docx ; https://www.ca.go.ke/index.php/our-role-your-protection
- **CA timelines**:
  - CA's page says complaints are "acknowledged within three (3) days of receipt" and "responded to substantively within ten (10) days", with resolution in "1 - 30 days" (complex cases longer). [VERIFIED-PRIMARY, Our Role page]
  - When CA forwards a complaint, the licensee must acknowledge within **1 working day** and respond substantively within **21 days** (Guidelines 6.3.1.5). [VERIFIED-PRIMARY]
  - No SMS short code for CA complaints was found. [UNVERIFIED]

### Central Bank of Kenya (CBK)
- No dedicated online complaints portal or consumer-complaints email for PSP/mobile money appeals could be found on centralbank.go.ke. The confirmed channels are general ones: **comms@centralbank.go.ke**; +254 20 286 0000 / 286 1000 / 286 3000; +254 709 081 000 / 709 083 000; Haile Selassie Avenue, P.O. Box 60000-00200 Nairobi. [VERIFIED-PRIMARY] https://www.centralbank.go.ke/fraud-safety/
- One search snippet cited "cpd@centralbank.go.ke" and a "consumer-protection" page. Neither was confirmed on CBK's site. **[UNVERIFIED: do not hard-code it]**
- What to send: write to CBK "providing full details of the grievance and the [provider's] response thereto" with "copies of all relevant correspondence". CBK hears both parties and aims for an amicable solution. **CBK will not consider matters already before the courts.** [VERIFIED-PRIMARY, the bank mechanism; applied by analogy to PSPs] https://www.centralbank.go.ke/wp-content/uploads/2023/12/Customer-Complaints-Handling-Mechanism.pdf
- No published CBK response timeline for appeals was found. A "CBK escalates within 14 days" claim seen in a search summary is [UNVERIFIED].
- In the pipeline: the **Financial Consumer Protection Framework for Kenya (Draft, March 2026)**, a joint document from CBK, CMA, IRA, RBA, SASRA, CA and CAK. It would require a unique reference number per complaint (2.7.2(1)), full complaint records (2.7.3), and a right to escalate to a regulator (2.7.5). It is **still a draft and not yet binding**. [VERIFIED-PRIMARY] https://www.centralbank.go.ke/wp-content/uploads/2026/04/Consumer-Protection-Framework-March-2026.pdf

### Competition Authority of Kenya (CAK), Consumer Protection Department
- Portal: **https://competition.cak.go.ke:444/** (consumer complaint form). Email: **complain@cak.go.ke**. Tel: +254 20 2628233 / +254 20 2779000. Office: CBK Pension Towers, 15th Floor, Harambee Ave, P.O. Box 36265-00200 Nairobi. [VERIFIED-PRIMARY] https://cak.go.ke/e-services/file-consumer-complaint ; user manual https://cak.go.ke/sites/default/files/Consumer_Complaints_User_Manual.pdf
- Process: acknowledge and flag information gaps, analyse, contact the trader, then apply administrative remedies (refund, replacement, etc.). Complaints outside CAK's jurisdiction are referred to the relevant agency. Unresolved matters may go to the ODPP. [VERIFIED-PRIMARY, same page]
- A "CAK aims to resolve within 90 days" claim appears only on a third-party blog. [UNVERIFIED]
- When to use CAK for telecom or mobile money: charges imposed without prior disclosure (s.56(3)), unconscionable conduct (s.56), or misleading promotions (s.55). CAK's guidelines say s.56(3) reaches "banking, micro-finance and insurance and other services", and list "internet, transmission" among the "other services". [VERIFIED-PRIMARY] https://cak.go.ke/arch/sites/default/files/guidelines/consumer-protection/Consumer%20Protection%20Guidelines.pdf (Revised Dec 2017, paras 85–89; the guidelines "do not have the force of law")

### Ombudsman (Commission on Administrative Justice)
- Covers **public institutions only**: "delay, abuse of power, unfair treatment, manifest injustice or discourtesy". It is a route only if CA or CBK itself mishandles or sits on the complaint. CA is a public body (CA appears in CAJ's 2024/25 MDA list). Channels: http://cmis.ombudsman.go.ke ; toll-free 0800 221 349 ; +254 20 2270000 ; info@ombudsman.go.ke. [VERIFIED-PRIMARY] https://www.ombudsman.go.ke/

---

## 4. Statutory deadlines that matter (summary)

| Deadline | Who | Source |
|---|---|---|
| **15 days** from occurrence to file a mobile money complaint with the PSP | Consumer | NPS Regs 2014 reg 39(1) [primary] |
| **6 months** from incident to lodge a written telecom complaint | Consumer | KICA (Consumer Protection) Regs 2010 reg 7(2) [primary] |
| 1 working day to acknowledge (immediately if interactive); unique reference number | Telco | CA Guidelines 2025, 6.3.1.1 [primary] |
| **21 days** to resolve, after which the consumer may go to CA | Telco | CA Guidelines 2025, standards table and 6.4.1 [primary] |
| **30 days** to resolve; then appeal to CBK | PSP | NPS Regs 2014 reg 40(1), (5) [primary] |
| 48 h acknowledge / 7 days resolve | Banks | CBK/PG/22 per CBK mechanism PDF [primary] |
| CA: 3 days acknowledge, 10 days substantive response, 1–30 days resolution | CA | ca.go.ke "Our Role" page [primary] |
| Telco: 1 working day to acknowledge and 21 days to respond to a CA referral | Telco | Guidelines 6.3.1.5 [primary] |
| **60 days** from the dispute's occurrence to notify CA of a formal dispute (in writing, with fee) | Consumer | KICA (Dispute Resolution) Regs 2010 reg 4(1) [primary] https://www.ca.go.ke/sites/default/files/2023-06/Dispute-Resolution-Regulations-2010-1.pdf |
| CA serves the respondent within 7 days; respondent replies within 21 days; hearing date set within 15 days of last pleading; written decision within 30 days of hearing | CA / parties | Dispute Regs regs 5, 7, 8 [primary] |
| **15 days** to appeal a CA dispute decision to the Communications and Multimedia Appeals Tribunal | Either party | Dispute Regs reg 8(6) [primary] |
| Billing records kept until the dispute settles if it starts within 12 months of the bill | Telco | Guidelines 6.10.4.5 [primary] |
| Penalty for licensee offences under the Consumer Protection Regs: up to KES 300,000 fine or 3 years | Licensee | Regs 2010 reg 23(3) [primary] |

The Dispute Regulations still say "Commission" (CCK). They now apply to CA under KICA as amended. The 60-day dispute window runs from the dispute's occurrence, so a consumer who waits out the 21-day licensee period still has time but should not delay.

---

## 5. SIM swap specifics
- SIM registration requires the person to appear in person with original ID (KICA (Registration of SIM-Cards) Regulations 2015, LN 163/2015). I could not read the exact SIM-replacement clause (kenyalaw PDF blocked). [VERIFIED-SECONDARY] https://new.kenyalaw.org/akn/ke/act/ln/2015/163/eng@2022-12-31
- CA's Q4 FY2025/26 report names "unauthorized SIM replacement" and "weaknesses in customer identity verification" as emerging risks. CA is monitoring SIM replacement and verification compliance and reviewing the safeguards. [VERIFIED-PRIMARY, Q4 report]
- Playbook: (1) call the telco immediately (Safaricom 100/200, Airtel 100) to block the line and the wallet; (2) report to police/DCI; (3) file a written complaint with the telco and the PSP within 15 days for the money loss (reg 39(1)); (4) escalate to CA (SIM issuance failure) and CBK (wallet loss) after 21 or 30 days.
- No law found that guarantees compensation for SIM-swap losses. CBK is reportedly developing a fraud compensation framework under NFIS 2025–2028 [VERIFIED-SECONDARY] https://techtrendske.co.ke/2025/09/28/cbk-digital-fraud-compensation-plan-mobile-money/

---

## 6. Verification of the two statistics

### Claim A: "CA received 670 escalated complaints in Q4 FY2025/26, 122 still under regulatory follow-up". **CONFIRMED (primary).**
CA's *Quarter 4 FY 2025/2026 Consumer Complaints Report* (April–June 2026) says: 670 escalated complaints; **548 resolved (82%)**; **122 under active regulatory follow-up**. https://www.ca.go.ke/sites/default/files/2026-08/Consumer%20Complaints%20Statistics%20for%20Q4%20FY%202025-2026.docx (listed at https://www.ca.go.ke/reports-and-studies)

Breakdown (total / resolved / in progress):
- Telecommunications: 239 / 167 / 72. Within data services, "Billing & Charges" = 75 (59 resolved).
- Digital Financial Services and Mobile Money: 110 / 109 / 1, including Fraud and Scams 86 / 81 / 5.
- Cybercrime/criminal use of ICT: 75.
- Broadcasting: 42.
- Postal: 13.

Caveat: some sub-rows in CA's table do not add up (e.g. data Billing 75 = 59 resolved + 2 in progress). Cite the headline figures, not the sub-rows.

Previous quarters: 563 (Q3), 362 (Q2). [VERIFIED-SECONDARY] https://eastleighvoice.co.ke/business/387499/telecom-complaints-top-ict-consumer-grievances-in-kenya-as-service-quality-concerns-persist ; https://capitalfm.africa/consumer-complaints-to-ca-rise-to-563-in-q3/

Note: CA's quarterly *Sector Statistics Report* Q4 2025/26 does not contain the complaints figures. They appear only in the separate Consumer Complaints report. Telecompaper dates its story "13 August 2025", which looks like a typo for 2026.

### Claim B: "The Ombudsman (CAJ) reported in 2026 that of 813 complaints received in 2025, 579 remained pending". **PARTLY CONFIRMED (secondary only); framing is misleading.**
- News coverage (Kahawatungu, 25 Aug 2026; Nation op-ed) says CAJ reported **813 complaints against 54 public institutions** for January–December 2025: **228 resolved (28%)** and **579 pending (72%)**. Nine institutions accounted for 630 complaints (77%), including Kenya Power, NTSA, Immigration, SHA and Pensions. https://kahawatungu.com/ombudsman-raises-alarm-over-delays-in-resolving-public-complaints/ ; https://nation.africa/kenya/blogs-opinion/blogs/resolution-of-citizens-complaints-is-a-right-5579360
- **I could not find the primary CAJ document** with the 813 figure on ombudsman.go.ke.
- The figures do not reconcile: 228 + 579 = 807, so 6 complaints are unaccounted for.
- **The 813 is not CAJ's total caseload.** CAJ's own *Annual Report 2024/25* gives **2,520 new complaints**, 993 resolved (39.4%), and **7,265 handled** including 4,745 brought forward. https://ombudsman.go.ke/sites/default/files/2026-07/CAJ%20Annual%20Report%202024-25.pdf
- Not relevant to telecom or mobile money: CAJ has no jurisdiction over Safaricom or Airtel. **Recommendation: do not use this statistic in the telecom playbook.** If it is used elsewhere, cite it as "complaints against 54 public institutions, CY2025 (as reported by Kahawatungu/Nation)".

---

## 7. Open items / not verified
- Exact CBK consumer-complaint email or portal for PSP appeals, and any CBK response timeline.
- The current Airtel Money reversal USSD code (*222# vs *334#) and any M-Pesa reversal time window. Operator pages blocked fetches.
- Full text of Safaricom's Complaint Handling Guideline PDF (403).
- A CA SMS short code for complaints (none found).
- The exact SIM-replacement clause in LN 163/2015, and whether new subscriber registration regulations (drafted 2022) have been gazetted.
- A CAK consumer complaint resolution timeline (the "90 days" figure is from a blog only).
