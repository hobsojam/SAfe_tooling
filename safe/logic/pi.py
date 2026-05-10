from safe.models.pi import PI, PIStatus
from safe.models.base import SAFeBaseModel
from safe.exceptions import IllegalPITransitionError
from typing import TYPE_CHECKING

# Type checking stubs for type hinting compatibility
if TYPE_CHECKING:
    from safe.models.pi import PIStatus

def validate_pi_transition(pi: PI, target_status: 'PIStatus' = None) -> None:
    """
    Validates if a PI is allowed to transition to the target status based on business rules.

    Raises IllegalPITransitionError if the transition is not permitted.
    """
    current_status = pi.status

    # Rule 1: PI must start in PLANNING state
    if current_status == PIStatus.DRAFT:
        # Draft PIs can only move to PLANNING
        if target_status and target_status != PIStatus.PLANNING:
            raise IllegalPITransitionError(
                "Cannot transition out of DRAFT status directly.", 
                current_status.value, 
                PIStatus.PLANNING.value
            )
        # No need to raise, the flow dictates the next step

    # Rule 2: Transition to PLANNING
    if current_status == PIStatus.DRAFT and target_status == PIStatus.PLANNING:
        # Allowed: Draft -> Planning
        pass

    # Rule 3: Planning to Active
    elif current_status == PIStatus.PLANNING and target_status == PIStatus.ACTIVE:
        # Additional validation for activation (e.g., no other PI active for same ART)
        # This logic should live here if necessary, but keep it simple for now.
        pass

    # Rule 4: Active to Progress (Example)
    elif current_status == PIStatus.ACTIVE and target_status == PIStatus.PROGRESS:
        # Business checks for PRD readiness, etc.
        pass
        
    # Rule 5: Illegal Transitions Check
    elif target_status:
        if not is_valid_transition(current_status, target_status):
            raise IllegalPITransitionError(
                "Invalid status transition attempted.", 
                current_status.value, 
                target_status.value
            )
    
    # Rule 6: Final States are immutable
    elif current_status in [PIStatus.CLOSED, PIStatus.ARCHIVED]:
        raise IllegalPITransitionError(
            "State is final and cannot be modified.", 
            current_status.value, 
            "None"
        )

def is_valid_transition(current: 'PIStatus', target: 'PIStatus') -> bool:
    """Internal helper to check if a transition pair is broadly valid."""
    # Simple model of allowed transitions (non-exhaustive but restrictive)
    transitions = {
        (PIStatus.DRAFT, PIStatus.PLANNING): True,
        (PIStatus.PLANNING, PIStatus.ACTIVE): True,
        (PIStatus.ACTIVE, PIStatus.PROGRESS): True,
        (PIStatus.PROGRESS, PIStatus.CLOSED): True,
    }
    return (current, target) in transitions

# Note: The 'pi_predictability' validation would also be added here.
