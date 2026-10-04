"""Playbooks: the escalation route for each kind of problem.

A playbook is an ordered list of steps. Each step tells the user what to do, may offer a letter to generate,
and may only become available some days after the previous step (e.g. waiting for a reply to a demand letter).
Playbooks are plain data so they can be reviewed by someone who knows the law without reading the app code.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Channel:
    label: str
    value: str
    # "url", "email", "phone", "address" or "text"
    kind: str = "text"


@dataclass(frozen=True)
class Step:
    key: str
    title: str
    guidance: list[str]
    # Letter template to offer at this step (see cases/letters.py), if any.
    letter: str | None = None
    # Days to wait after the previous step is done before this step becomes available.
    wait_days: int = 0
    # Where to send things at this step.
    channels: list[Channel] = field(default_factory=list)
    # Marks the step that hands the case to a regulator, tribunal or court.
    escalation: bool = False


@dataclass(frozen=True)
class Playbook:
    key: str
    name: str
    summary: str
    categories: list[str]
    evidence_checklist: list[str]
    steps: list[Step]
    # Sources the steps are based on, shown to the user.
    sources: list[Channel] = field(default_factory=list)
    reviewed_on: str = ""
    # Some routes have a hard limit for the first complaint (e.g. 15 days for mobile money).
    complaint_deadline_days: int | None = None
    complaint_deadline_label: str = ""
    # The step that satisfies the deadline; the warning shows until it is done.
    complaint_step: str = ""

    def step(self, key: str) -> Step | None:
        return next((s for s in self.steps if s.key == key), None)
