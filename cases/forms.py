from django import forms
from django.utils import timezone

from .letters import TEMPLATES
from .models import Case, Category, EventKind, Evidence, EvidenceKind, Letter, TimelineEvent
from .parsers import parse_message
from .uploads import ACCEPT_ATTR, validate_upload

DATE_WIDGET = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")

# Field labels that read better for some kinds of case.
CATEGORY_LABELS = {
    "RENT_DEPOSIT": {
        "opponent_name": "Landlord or agent",
        "account_reference": "Property and unit (e.g. Kileleshwa Court, House B4)",
        "incident_date": "Date you moved out",
        "amount_claimed": "Deposit amount (KES)",
    },
    "TELECOM": {
        "opponent_name": "Service provider (e.g. Safaricom, Airtel, your ISP)",
        "account_reference": "Your phone number or account number",
    },
    "MOBILE_MONEY": {
        "opponent_name": "Mobile money provider (e.g. Safaricom M-Pesa)",
        "account_reference": "Your mobile money number",
    },
}


class CategoryForm(forms.Form):
    category = forms.ChoiceField(choices=Category.choices, widget=forms.RadioSelect)


class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = [
            "title",
            "opponent_name",
            "opponent_contact",
            "account_reference",
            "opponent_reference",
            "incident_date",
            "amount_claimed",
            "description",
            "desired_outcome",
        ]
        labels = {"title": "Short title for this case"}
        help_texts = {
            "title": "For example: “Wrong KES 3,500 deduction on my line” or “Deposit not returned”.",
            "opponent_reference": "Ticket or complaint number they gave you, if any.",
            "description": "Explain it in your own words, in the order things happened.",
            "desired_outcome": "Be specific: refund KES 3,500, reverse the transaction, issue my transcript…",
        }
        widgets = {
            "incident_date": DATE_WIDGET,
            "description": forms.Textarea(attrs={"rows": 6}),
            "desired_outcome": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, category=None, **kwargs):
        super().__init__(*args, **kwargs)
        for field, label in CATEGORY_LABELS.get(category or getattr(self.instance, "category", ""), {}).items():
            self.fields[field].label = label

    def clean_incident_date(self):
        value = self.cleaned_data["incident_date"]
        if value > timezone.localdate():
            raise forms.ValidationError("This date is in the future.")
        return value

    def clean_amount_claimed(self):
        value = self.cleaned_data.get("amount_claimed")
        if value is not None and value < 0:
            raise forms.ValidationError("The amount cannot be negative.")
        return value


class EvidenceForm(forms.ModelForm):
    upload = forms.FileField(
        required=False,
        label="File (photo, screenshot, PDF…)",
        widget=forms.ClearableFileInput(attrs={"accept": ACCEPT_ATTR}),
    )

    class Meta:
        model = Evidence
        fields = ["kind", "title", "occurred_on", "text", "notes"]
        labels = {"text": "Or paste the message text (SMS, M-Pesa, WhatsApp, email)", "title": "What is it?"}
        widgets = {"occurred_on": DATE_WIDGET, "text": forms.Textarea(attrs={"rows": 4})}

    field_order = ["kind", "upload", "text", "title", "occurred_on", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].required = False
        self.upload_info = None
        self.parsed = None

    def clean(self):
        cleaned = super().clean()
        upload = cleaned.get("upload")
        text = (cleaned.get("text") or "").strip()
        if not upload and not text:
            raise forms.ValidationError("Attach a file or paste the message text.")
        if upload:
            try:
                self.upload_info = validate_upload(upload)
            except forms.ValidationError as error:
                self.add_error("upload", error)
        if text:
            self.parsed = parse_message(text)
            # Fill in what the message tells us when the user left it blank.
            if not cleaned.get("occurred_on") and self.parsed.occurred_on:
                cleaned["occurred_on"] = self.parsed.occurred_on
            if not cleaned.get("title") and (self.parsed.code or self.parsed.amount):
                cleaned["title"] = self.parsed.title
        if not cleaned.get("title"):
            cleaned["title"] = upload.name.rsplit(".", 1)[0][:140] if upload else text[:60]
        return cleaned

    def save_for(self, case: Case) -> Evidence:
        item = super().save(commit=False)
        item.case = case
        item.title = self.cleaned_data["title"]
        item.occurred_on = self.cleaned_data.get("occurred_on")
        upload = self.cleaned_data.get("upload")
        if upload and self.upload_info:
            _, content_type = self.upload_info
            item.original_filename = upload.name[:200]
            item.content_type = content_type
            item.size = upload.size
            item.file.save(upload.name, upload, save=False)
        item.save()
        return item


class EventForm(forms.ModelForm):
    class Meta:
        model = TimelineEvent
        fields = ["occurred_on", "kind", "title", "details", "evidence"]
        labels = {"title": "What happened", "evidence": "Related evidence"}
        widgets = {
            "occurred_on": DATE_WIDGET,
            "details": forms.Textarea(attrs={"rows": 3}),
            "evidence": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, case=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["kind"].choices = [c for c in EventKind.choices if c[0] not in {"RESOLVED", "CLOSED"}]
        self.fields["evidence"].queryset = case.evidence.all() if case else Evidence.objects.none()
        self.fields["evidence"].required = False
        self.fields["occurred_on"].initial = timezone.localdate()


class LetterForm(forms.ModelForm):
    class Meta:
        model = Letter
        fields = ["recipient", "subject", "body"]
        labels = {"recipient": "To"}
        widgets = {"body": forms.Textarea(attrs={"rows": 22, "class": "mono"})}


class LetterSentForm(forms.Form):
    sent_on = forms.DateField(widget=DATE_WIDGET, initial=timezone.localdate)
    sent_via = forms.ChoiceField(
        choices=[("Email", "Email"), ("WhatsApp", "WhatsApp"), ("Hand delivery", "Hand delivery"), ("Post", "Post"), ("Online portal", "Online portal")]
    )


class NewLetterForm(forms.Form):
    template = forms.ChoiceField(choices=[(k, t.name) for k, t in TEMPLATES.items()])


class StepDoneForm(forms.Form):
    done_on = forms.DateField(widget=DATE_WIDGET, initial=timezone.localdate)
    notes = forms.CharField(required=False, max_length=300, label="Notes (reference number, who you spoke to…)")


class FollowUpForm(forms.Form):
    next_follow_up = forms.DateField(widget=DATE_WIDGET, required=False, label="Remind me on")


class CloseCaseForm(forms.Form):
    outcome = forms.ChoiceField(choices=[("resolved", "Resolved"), ("closed", "Closed without resolution")], widget=forms.RadioSelect)
    amount_recovered = forms.DecimalField(required=False, min_value=0, max_digits=12, decimal_places=2, label="Amount recovered (KES)")
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}), label="What was the outcome?")


class EvidenceKindFilter(forms.Form):
    kind = forms.ChoiceField(choices=[("", "All")] + list(EvidenceKind.choices), required=False)
