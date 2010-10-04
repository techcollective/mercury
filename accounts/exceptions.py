"""
Exception classes for accounts app
"""

from mercury.exceptions import MercuryException, RedirectException


class AccountsException(MercuryException):
    """
    Base class for exceptions in the accounts app
    """
    pass


class AccountsRedirect(RedirectException, AccountsException):
    """
    An exception that contains a URL that the current request
    should be redirected to.
    """


class ObjectNotFound(AccountsException):
    pass


class DepositedPaymentsException(AccountsRedirect):
    """
    Raised when attempting to edit or delete a payment that has been
    deposited. In general the URL will be set to a changelist page
    of the deposited payments.
    """
