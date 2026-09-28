"""Structured validation errors exposed by the Meta-Kernel model."""

from collections.abc import Mapping
from typing import Any


class KernelValidationError(ValueError):
    """Base class for deterministic, machine-readable validation failures."""

    def __init__(
        self,
        code: str,
        message: str,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.details = dict(details or {})
        super().__init__(message)


class InvalidIdError(KernelValidationError):
    """Raised when an opaque runtime identifier is malformed."""


class InvalidScalarValueError(KernelValidationError):
    """Raised when a scalar value is outside the P0 value model."""


class InvalidRelationSchemaError(KernelValidationError):
    """Raised when a relation schema is malformed."""


class MalformedPropositionError(KernelValidationError):
    """Raised when a relation is applied to invalid arguments."""


class InvalidSupportError(KernelValidationError):
    """Raised when a support or support-status query is malformed."""


class InvalidVariableError(KernelValidationError):
    """Raised when a pattern variable is malformed."""


class InvalidPatternError(KernelValidationError):
    """Raised when a proposition or support pattern is malformed."""


class InvalidRuleError(KernelValidationError):
    """Raised when a DERIVE rule is malformed."""


class DerivationLimitError(RuntimeError):
    """Raised when DERIVE closure exceeds its configured iteration limit."""


class PatchValidationError(KernelValidationError):
    """Raised when a WorldPatch cannot be atomically committed."""
