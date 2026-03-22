class VibeCheckError(Exception):
    """Base error for scaffolded VibeCheck failures."""


class HookPayloadError(VibeCheckError):
    """Raised when the Claude hook payload is missing required data."""


class UnsupportedMutationError(VibeCheckError):
    """Raised when a tool call is not a supported mutation payload."""


class StateValidationError(VibeCheckError):
    """Raised when persisted state is malformed or incomplete."""
