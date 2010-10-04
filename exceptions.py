"""
Base exceptions for mercury apps
"""


class MercuryException(Exception):
    pass


class RedirectException(MercuryException):
    """
    Used when an exception should also redirect the current request
    to a new URL.
    """
    def __init__(self, *args, **kwargs):
        try:
            self.url = kwargs["url"]
        except KeyError:
            raise MercuryException("%s requires a \"url\" keyword argument" %
                                    self.__class__.__name__)
        super(RedirectException, self).__init__(*args)
