class SafeToolingError(Exception):
    """Base exception for all SAFe Tooling domain errors."""

    pass


class IllegalStateError(SafeToolingError):
    """Raised when an entity is in an illegal state for the requested action."""

    def __init__(self, message: str, current_state: str, required_state: str):
        self.current_state = current_state
        self.required_state = required_state
        super().__init__(f"{message}. Current state: {current_state}, Requires: {required_state}")


class IllegalPITransitionError(SafeToolingError):
    """Raised when attempting an invalid state transition on a PI."""

    def __init__(self, message: str, current_status: str, target_status: str):
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(f"{message}. Cannot move from {current_status} to {target_status}.")


class InvalidCapacityError(SafeToolingError):
    """Raised when capacity plans violate business logic (e.g., negative capacity)."""

    pass


class DomainValidationError(SafeToolingError):
    """Generic exception for core business logic failures."""

    pass
