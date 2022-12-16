class ValidationError(ValueError):
    pass

class RequestedEndDateAfterBundleEndDate(ValidationError):
    pass
