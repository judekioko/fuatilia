import io
import shutil
import tempfile
import zipfile
from datetime import date, timedelta
from decimal import Decimal

from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from cases import services
from cases.letters import TEMPLATES, render_letter
from cases.models import Case, Evidence, Status, StepStatus
from cases.parsers import parse_message

TEMP_MEDIA = tempfile.mkdtemp()
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


def make_user(email="amina@example.com", **extra):
    return User.objects.create_user(email=email, password="Str0ng-pass-123", full_name="Amina Odhiambo", **extra)


def make_case(user, category="MOBILE_MONEY", **extra):
    fields = dict(
        title="Wrong deduction",
        category=category,
        opponent_name="Safaricom PLC",
        incident_date=timezone.localdate() - timedelta(days=3),
        description="KES 3,500 was deducted from my M-Pesa without my authority.",
        desired_outcome="Refund KES 3,500",
        amount_claimed=Decimal("3500"),
    )
    fields.update(extra)
    return services.open_case(user, **fields)


class ParserTests(TestCase):
    def test_reads_mpesa_send_money_message(self):
        text = (
            "TJ41P2Q3R4 Confirmed. Ksh3,500.00 sent to JOHN DOE 0712345678 on 21/9/26 at 10:15 AM. "
            "New M-PESA balance is Ksh1,200.00."
        )
        parsed = parse_message(text)
        self.assertEqual(parsed.code, "TJ41P2Q3R4")
        self.assertEqual(parsed.amount, Decimal("3500.00"))
        self.assertEqual(parsed.occurred_on, date(2026, 9, 21))
        self.assertEqual(parsed.direction, "sent")
        self.assertEqual(parsed.counterparty, "John Doe")

    def test_reads_received_message(self):
        parsed = parse_message("TK11AA22BB Confirmed. You have received Ksh500.00 from MARY NJERI 0722000000 on 2/10/26 at 9:00 AM")
        self.assertEqual(parsed.direction, "received")
        self.assertEqual(parsed.counterparty, "Mary Njeri")

    def test_plain_text_is_harmless(self):
        parsed = parse_message("hello there")
        self.assertIsNone(parsed.code)
        self.assertIsNone(parsed.amount)


class WorkflowTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_open_case_assigns_reference_playbook_and_steps(self):
        case = make_case(self.user)
        self.assertRegex(case.reference, r"^FT-\d{4}-00001$")
        self.assertEqual(case.playbook, "mobile_money")
        self.assertEqual(case.steps.count(), 4)
        self.assertEqual(case.next_follow_up, timezone.localdate())
        self.assertEqual(case.events.count(), 2)
        second = make_case(self.user)
        self.assertTrue(second.reference.endswith("00002"))

    def test_mobile_money_has_15_day_complaint_deadline(self):
        case = make_case(self.user)
        self.assertEqual(case.complaint_deadline, case.incident_date + timedelta(days=15))
        rent = make_case(self.user, category="RENT_DEPOSIT")
        general = make_case(self.user, category="BANK")
        self.assertIsNone(general.complaint_deadline)
        self.assertEqual(rent.playbook, "rent_deposit")

    def test_completing_a_step_schedules_the_next_one(self):
        case = make_case(self.user, category="RENT_DEPOSIT")
        steps = list(case.steps.all())
        services.complete_step(case, steps[0], timezone.localdate())
        services.complete_step(case, steps[1], timezone.localdate())
        case.refresh_from_db()
        demand = case.steps.get(key="final_demand")
        self.assertEqual(demand.available_on, timezone.localdate() + timedelta(days=14))
        self.assertEqual(case.next_follow_up, demand.available_on)
        self.assertEqual(case.status, Status.WAITING)

    def test_escalation_step_marks_case_escalated(self):
        case = make_case(self.user, category="TELECOM")
        for step in case.steps.all()[:3]:
            services.complete_step(case, step)
        case.refresh_from_db()
        self.assertEqual(case.status, Status.ESCALATED)

    def test_close_and_reopen(self):
        case = make_case(self.user)
        services.close_case(case, resolved=True, note="Refunded", amount_recovered=Decimal("3500"))
        case.refresh_from_db()
        self.assertEqual(case.status, Status.RESOLVED)
        self.assertIsNone(case.next_follow_up)
        services.reopen_case(case)
        case.refresh_from_db()
        self.assertEqual(case.status, Status.OPEN)
        self.assertIsNotNone(case.next_follow_up)


class LetterTests(TestCase):
    def test_every_template_renders_without_html_escaping(self):
        user = make_user()
        case = make_case(user, description="The agent's \"promise\" was broken & ignored.")
        for key in TEMPLATES:
            subject, body = render_letter(case, key)
            self.assertNotIn("&#x27;", body, key)
            self.assertNotIn("&amp;", body, key)
            self.assertIn(user.full_name, body, key)

    def test_complaint_quotes_facts_and_deadline(self):
        case = make_case(make_user())
        _, body = render_letter(case, "complaint")
        self.assertIn("KES 3,500.00", body)
        self.assertIn(case.reference, body)
        deadline = timezone.localdate() + timedelta(days=14)
        self.assertIn(f"{deadline.day} {deadline:%B %Y}", body)


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class SecurityTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.owner = make_user()
        self.other = make_user("someone@example.com")
        self.case = make_case(self.owner)

    def test_other_users_cannot_see_a_case_or_its_files(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("evidence_add", args=[self.case.reference]),
            {"kind": "SCREENSHOT", "title": "Screenshot", "upload": SimpleUploadedFile("shot.png", PNG, "image/png")},
        )
        self.assertEqual(response.status_code, 302)
        item = self.case.evidence.get()

        self.client.force_login(self.other)
        for name, args in [
            ("case_detail", [self.case.reference]),
            ("evidence_file", [self.case.reference, item.pk]),
            ("bundle_zip", [self.case.reference]),
            ("bundle_view", [self.case.reference]),
        ]:
            self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 404, name)
        self.assertEqual(self.client.post(reverse("case_delete", args=[self.case.reference])).status_code, 404)
        self.assertTrue(Case.objects.filter(pk=self.case.pk).exists())

    def test_files_are_encrypted_on_disk_and_decrypted_for_the_owner(self):
        self.client.force_login(self.owner)
        self.client.post(
            reverse("evidence_add", args=[self.case.reference]),
            {"kind": "SCREENSHOT", "title": "Screenshot", "upload": SimpleUploadedFile("shot.png", PNG, "image/png")},
        )
        item = self.case.evidence.get()
        with open(item.file.path, "rb") as raw:
            self.assertNotIn(b"PNG", raw.read())
        response = self.client.get(reverse("evidence_file", args=[self.case.reference, item.pk]))
        self.assertEqual(b"".join(response.streaming_content), PNG)
        self.assertEqual(response["Content-Type"], "image/png")

    def test_disguised_or_unknown_files_are_rejected(self):
        self.client.force_login(self.owner)
        for upload in [
            SimpleUploadedFile("evil.png", b"<html><script>alert(1)</script></html>", "image/png"),
            SimpleUploadedFile("page.html", b"<html></html>", "text/html"),
            SimpleUploadedFile("tool.exe", b"MZ\x90\x00", "application/octet-stream"),
        ]:
            response = self.client.post(
                reverse("evidence_add", args=[self.case.reference]), {"kind": "OTHER", "upload": upload}
            )
            self.assertEqual(response.status_code, 200, upload.name)
        self.assertEqual(Evidence.objects.count(), 0)

    def test_pasted_mpesa_message_fills_title_and_date(self):
        self.client.force_login(self.owner)
        self.client.post(
            reverse("evidence_add", args=[self.case.reference]),
            {"kind": "MESSAGE", "text": "TJ41P2Q3R4 Confirmed. Ksh3,500.00 sent to JOHN DOE 0712345678 on 21/9/26 at 10:15 AM."},
        )
        item = self.case.evidence.get()
        self.assertEqual(item.occurred_on, date(2026, 9, 21))
        self.assertIn("TJ41P2Q3R4", item.title)

    def test_letters_are_only_created_by_post(self):
        self.client.force_login(self.owner)
        url = reverse("letter_new", args=[self.case.reference])
        self.assertEqual(self.client.get(url + "?template=complaint").status_code, 405)
        self.client.post(url, {"template": "complaint"})
        self.assertEqual(self.case.letters.count(), 1)

    def test_bundle_zip_contains_chronology_and_exhibits(self):
        self.client.force_login(self.owner)
        self.client.post(
            reverse("evidence_add", args=[self.case.reference]),
            {"kind": "SCREENSHOT", "title": "Balance screenshot", "upload": SimpleUploadedFile("shot.png", PNG, "image/png")},
        )
        response = self.client.get(reverse("bundle_zip", args=[self.case.reference]))
        names = zipfile.ZipFile(io.BytesIO(response.content)).namelist()
        self.assertIn("01-chronology.txt", names)
        self.assertTrue(any(n.startswith("exhibits/E01-") and n.endswith(".png") for n in names))

    def test_account_deletion_removes_cases_and_files(self):
        self.client.force_login(self.owner)
        self.client.post(
            reverse("evidence_add", args=[self.case.reference]),
            {"kind": "SCREENSHOT", "title": "x", "upload": SimpleUploadedFile("shot.png", PNG, "image/png")},
        )
        path = self.case.evidence.get().file.path
        self.client.post(reverse("account_delete"), {"confirm": "DELETE"})
        self.assertFalse(User.objects.filter(email="amina@example.com").exists())
        self.assertFalse(Case.objects.exists())
        import os

        self.assertFalse(os.path.exists(path))


class AccountTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_signup_requires_consent_and_records_it(self):
        data = {"full_name": "Brian Kip", "email": "Brian@Example.com", "phone": "", "password": "Long-enough-pass-9"}
        response = self.client.post(reverse("signup"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())
        self.client.post(reverse("signup"), {**data, "consent": "on"})
        user = User.objects.get()
        self.assertEqual(user.email, "brian@example.com")
        self.assertIsNotNone(user.consented_at)

    def test_login_locks_after_repeated_failures(self):
        make_user()
        for _ in range(5):
            self.client.post(reverse("login"), {"email": "amina@example.com", "password": "wrong"})
        response = self.client.post(reverse("login"), {"email": "amina@example.com", "password": "Str0ng-pass-123"})
        self.assertContains(response, "Too many failed attempts")

    def test_login_ignores_offsite_next(self):
        make_user()
        response = self.client.post(
            reverse("login"), {"email": "amina@example.com", "password": "Str0ng-pass-123", "next": "https://evil.example"}
        )
        self.assertRedirects(response, reverse("dashboard"), fetch_redirect_response=False)


class CommandTests(TestCase):
    def test_reminders_email_once_per_day(self):
        user = make_user()
        case = make_case(user)
        services.set_follow_up(case, timezone.localdate() - timedelta(days=1))
        call_command("send_reminders", base_url="https://fuatilia.example", stdout=io.StringIO())
        call_command("send_reminders", stdout=io.StringIO())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(case.reference, mail.outbox[0].body)

    def test_purge_deletes_only_old_closed_cases(self):
        user = make_user()
        old = make_case(user)
        services.close_case(old, resolved=False)
        Case.objects.filter(pk=old.pk).update(closed_at=timezone.now() - timedelta(days=800))
        recent = make_case(user)
        services.close_case(recent, resolved=True)
        active = make_case(user)
        call_command("purge_closed_cases", stdout=io.StringIO())
        self.assertEqual(set(Case.objects.values_list("pk", flat=True)), {recent.pk, active.pk})

    def test_steps_start_pending(self):
        case = make_case(make_user())
        self.assertTrue(all(s.status == StepStatus.PENDING for s in case.steps.all()))


class DeadlineBannerTests(TestCase):
    def test_deadline_warning_stays_until_the_complaint_step_is_done(self):
        case = make_case(make_user())
        self.assertTrue(case.complaint_deadline_pending)
        services.complete_step(case, case.steps.get(key="reversal"))
        case.refresh_from_db()
        self.assertTrue(case.complaint_deadline_pending)
        services.complete_step(case, case.steps.get(key="written_complaint"))
        case.refresh_from_db()
        self.assertFalse(case.complaint_deadline_pending)
