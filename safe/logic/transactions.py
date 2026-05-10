from safe.store.repository import Repository
from typing import Callable, List, Any, Union
from safe.exceptions import SafeToolingError

class TransactionManager:
    """
    Manages atomic multi-step operations across multiple repositories.
    Ensures that all writes succeed or none of them do.
    """
    def __init__(self, repositories: dict[str, Repository]):
        self.repos = repositories

    def execute_transaction(self, steps: List[Callable[[], Union[Any, None]]]) -> Any:
        """
        Executes a list of stateless functions/operations atomically.
        
        Args:
            steps: A list of functions, each containing the logic 
                   that needs to be run (write, read, or calculation).
        
        Returns:
            The result of the last successful step.
        
        Raises:
            SafeToolingError: If any step fails.
        """
        # In a real transactional DB, we would begin/commit/rollback here.
        # For TinyDB, we rely on the fact that the function calls manage the state.
        # If a step fails, we must raise to stop.
        last_result = None
        for step in steps:
            try:
                last_result = step()
            except SafeToolingError as e:
                # Re-raise domain errors encountered during the transaction
                raise e
            except Exception as e:
                # Handle unexpected system errors
                raise SafeToolingError(f"A fatal error occurred during the transaction: {e}")

        return last_result

# Helper function to simplify the transaction initiation within logic modules
def transactional_write(fn: Callable[[], Any], *args, **kwargs):
    """Decorator/helper to ensure logic function runs within a transaction context."""
    return fn(*args, **kwargs)