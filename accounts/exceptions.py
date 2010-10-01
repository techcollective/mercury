"""
Exception classes for accounts app
"""

from mercury.exceptions import MercuryException


class AccountsException(MercuryException):
    """
    Base class for exceptions in the accounts app
    """
    pass


class AccountsRedirect(AccountsException):
    """
    An exception that contains a URL that the current request
    should be redirected to.
    """
    def __init__(self, *args, **kwargs):
        try:
            self.url = kwargs["url"]
        except KeyError:
            raise AccountsException("%s requires a URL keyword" %
                                    self.__class__.__name__)
        super(AccountsRedirect, self).__init__(*args)


class ObjectNotFound(AccountsException):
    pass


class DepositedPaymentsException(AccountsRedirect):
    """
    Raised when attempting to edit or delete a payment that has been
    deposited. In general the URL will be set to a changelist page
    of the deposited payments.
    """
