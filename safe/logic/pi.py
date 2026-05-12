from safe.exceptions import IllegalPITransitionError
from safe.models.pi import PI, PIStatus

_VALID_TRANSITIONS: set[tuple[PIStatus, PIStatus]] = {
    (PIStatus.PLANNING, PIStatus.ACTIVE),
    (PIStatus.ACTIVE, PIStatus.CLOSED),
}


def validate_pi_transition(pi: PI, target_status: PIStatus) -> None:
    """Raise IllegalPITransitionError if the transition is not permitted."""
    if (pi.status, target_status) not in _VALID_TRANSITIONS:
        raise IllegalPITransitionError(
            "Invalid PI status transition",
            pi.status.value,
            target_status.value,
        )
