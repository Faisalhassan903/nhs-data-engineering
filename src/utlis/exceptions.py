class PipeLineError(Exception):
    """Base exception for nhs data pipeline errors"""
class DataValidationError(PipeLineError):
     """Raised when NHS data fails validation."""