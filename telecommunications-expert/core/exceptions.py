"""Shared domain exceptions for the telecommunications toolkit."""


class TelecomError(Exception):
    """Base exception for all telecommunications toolkit errors."""


class ConfigurationError(TelecomError):
    """Raised when configuration files are missing or malformed."""


class ElementNotFoundError(TelecomError):
    """Raised when a network element does not exist."""


class SubscriberNotFoundError(TelecomError):
    """Raised when a subscriber does not exist."""


class SNMPError(TelecomError):
    """Raised when an SNMP operation fails or the pysnmp library is unavailable."""
