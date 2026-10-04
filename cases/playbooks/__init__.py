from .base import Channel, Playbook, Step
from .general import GENERAL
from .rent_deposit import RENT_DEPOSIT
from .telecom import MOBILE_MONEY, TELECOM

# Sector playbooks are registered here; categories without one use the general playbook.
PLAYBOOKS: dict[str, Playbook] = {p.key: p for p in [GENERAL, RENT_DEPOSIT, TELECOM, MOBILE_MONEY]}


def register(playbook: Playbook) -> None:
    PLAYBOOKS[playbook.key] = playbook


def get_playbook(key: str) -> Playbook:
    return PLAYBOOKS.get(key, GENERAL)


def playbook_for_category(category: str) -> Playbook:
    for playbook in PLAYBOOKS.values():
        if playbook.key != GENERAL.key and category in playbook.categories:
            return playbook
    return GENERAL


__all__ = ["Channel", "Playbook", "Step", "PLAYBOOKS", "get_playbook", "playbook_for_category", "register"]
