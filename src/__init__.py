from pydantic import BaseModel


class InvalidExtractionError(Exception):
    """Raised when Claude fails to extract investors from minuta."""
    pass