"""Custom exceptions of the shop project."""


class ShopError(Exception):
    """Base class for all shop errors."""


class ProductValidationError(ShopError, ValueError):
    """Raised when product data is invalid."""


class MalformedRecordError(ShopError):
    """Raised when a CSV record cannot be converted to a Product."""


class DuplicateProductError(ShopError):
    """Raised when a product with the same SKU already exists."""


class ProductNotFoundError(ShopError):
    """Raised when a product cannot be found."""


class ConfigurationError(ShopError):
    """Raised when configuration is invalid."""


class ExternalServiceError(ShopError):
    """Raised when an external dependency fails."""
