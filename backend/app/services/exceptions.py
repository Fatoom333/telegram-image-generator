class ServiceError(Exception):
    """Base class for service-level errors."""


class UserNotFoundError(ServiceError):
    """Raised when user was not found."""


class UserBannedError(ServiceError):
    """Raised when user is banned."""


class NotEnoughCreditsError(ServiceError):
    """Raised when user has not enough credits."""


class EmptyPromptError(ServiceError):
    """Raised when generation prompt is empty."""


class TooManyInputImagesError(ServiceError):
    """Raised when user provided too many input images."""


class GenerationNotFoundError(ServiceError):
    """Raised when generation was not found."""


class PurchaseNotFoundError(ServiceError):
    """Raised when purchase was not found."""


class DuplicateUpdateError(ServiceError):
    """Raised when Telegram update was already processed."""


class AIProviderNotFoundError(ServiceError):
    """Raised when AI provider was not found."""


class AIModelNotFoundError(ServiceError):
    """Raised when AI model was not found or is not allowed."""


class AIProviderError(ServiceError):
    """Raised when AI provider failed."""


class PaymentProviderNotFoundError(ServiceError):
    """Raised when payment provider was not found."""


class PaymentTariffNotFoundError(ServiceError):
    """Raised when payment tariff was not found."""


class PaymentProviderError(ServiceError):
    """Raised when payment provider failed."""


class PurchaseAlreadyProcessedError(ServiceError):
    """Raised when purchase was already processed."""