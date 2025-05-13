from shared.errors import ProjectError


class AgeRestrictionError(ProjectError):
    """User age validation error."""

    code = 1
    detail = 'Minimal age is 18'


class EmailConfirmationCodeError(ProjectError):
    """Confirmation code error."""

    code = 2
    detail = 'A confirmation code is invalid or expired'


class EmailIsUsedError(ProjectError):
    """Email uniqueness error."""

    code = 3
    detail = 'Email is already used'
