"""
Exception classes for accounts app
"""

from mercury.exceptions import MercuryException


class AccountsException(MercuryException):
    pass


class AccountsRedirect(AccountsException):
    def __init__(self, *args, **kwargs):
        try:
            self.url = kwargs["url"]
        except KeyError:
            raise AccountsException("AccountsRedirect requires a URL")
        super(AccountsRedirect, self).__init__(*args)


class ObjectNotFound(AccountsException):
    pass
