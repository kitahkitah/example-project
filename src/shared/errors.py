from fastapi import HTTPException


class ProjectError(Exception):
    """An exception structure for the project.

    code - a project number of the error;
    detail - a description.
    """

    code: int | None = None
    detail: str | None = None


class APIError(HTTPException):
    """An exception for raising in API endpoints."""

    def __init__(self, status_code: int, project_code: int | None = None, detail: str | None = None) -> None:
        super().__init__(status_code=status_code, detail={'code': project_code, 'detail': detail})


class NotFoundError(ProjectError):
    """Something wasn't found."""

    code = None
    detail = 'Not found'


class ForbiddenError(ProjectError):
    """The action is forbidden."""

    code = None
    detail = 'Forbidden'
