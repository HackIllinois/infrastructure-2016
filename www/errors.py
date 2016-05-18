from www import utils

class Serializable(object):
    """
    Provides an interface for basic object serialization.
    Implementers should extend this class and override
    __public__ with the fields that should be included in
    serialization
    """

    __public__ = None

    def to_dict(self):
        """
        Creates a dictionary containing the keys specified
        in __public__ and their associated values
        """

        dict = {}
        for public_key in self.__public__:
            value = getattr(self, public_key)
            dict[public_key] = value
        return dict

class _BaseError(Serializable):
    """
    The abstract object from which all other errors are
    created. As such, this object should not be instantiated
    directly
    """

    __public__ = ['type', 'message', 'code', 'source']

    def __init__(self, type, message, status, code, source):
        """
        Initializes a new error
        :type the String-valued error type (e.g. 'ApiError')
        :message the String-valued message explaining what went wrong
        :status the HTTP status code associated with the error
        :code the API-specific code associated with the error
        :source the request key or keys that caused the error (which may be None)
        """

        if source and not isinstance(source, list):
            source = [source]

        self.acknowledgable = True
        self.type = type
        self.message = message
        self.status = status
        self.code = code
        self.source = source

class InvalidParameterError(_BaseError):
    """
    An error indicating that the client provided one or more
    parameters that were invalid
    """

    def __init__(self, message, source):
        type = 'InvalidParameterError'
        if not message:
            message = 'One or more parameters in the request were invalid'
        status = 400
        code = 102

        super(InvalidParameterError, self).__init__(type, message, status, code, source)

class MissingParameterError(_BaseError):
    """
    An error indicating that the client did not provide one or
    more required parameters
    """

    def __init__(self, message, source):
        type = 'MissingParameterError'
        if not message:
            message = 'One or more parameters were missing from the request'
        status = 400
        code = 101

        super(MissingParameterError, self).__init__(type, message, status, code, source)

class InvalidHeaderError(_BaseError):
    """
    An error indicating that the client provided one or more
    headers that were invalid
    """

    def __init__(self, message, source):
        type = 'InvalidHeaderError'
        if not message:
            message = 'One or more headers in the request were invalid'
        status = 400
        code = 103

        super(InvalidHeaderError, self).__init__(type, message, status, code, source)

class MissingHeaderError(_BaseError):
    """
    An error indicating that the client did not provide one or
    more required headers
    """

    def __init__(self, message, source):
        type = 'MissingHeaderError'
        if not message:
            message = 'One or more headers were missing from the request'
        status = 400
        code = 104

        super(MissingHeaderError, self).__init__(type, message, status, code, source)

class UnauthenticatedRequestError(_BaseError):
    """
    An error indicating that the client provided a request
    that could not be authenticated
    """

    def __init__(self, message, source):
        type = 'UnauthenticatedRequestError'
        if not message:
            message = 'This resource cannot be accessed with the provided credentials'
        status = 400
        code = 106

        super(UnauthenticatedRequestError, self).__init__(type, message, status, code, source)

class UnauthorizedRequestError(_BaseError):
    """
    An error indicating that the client provided a request
    that could not be authenticated
    """

    def __init__(self, message, source):
        type = 'UnauthorizedRequestError'
        if not message:
            message = 'You are not authorized to access this resource'
        status = 401
        code = 107

        super(UnauthorizedRequestError, self).__init__(type, message, status, code, source)


class ApiError(_BaseError):
    """
    An error indicating that something went wrong, but the exact
    reason cannot be described. Typically, this appears when an
    error goes unhandled
    """

    def __init__(self):
        type = 'ApiError'
        message = 'Something went wrong while processing that request'
        status = 500
        code = 100

        super(ApiError, self).__init__(type, message, status, code, None)

class NotFoundError(_BaseError):
    """
    An error indicating that the requested resource could
    not be found
    """

    def __init__(self, message, source):
        type = 'MissingUserError'
        if not message:
            message = 'The requested resource could not be found'
        status = 404
        code = 105

        super(NotFoundError, self).__init__(type, message, status, code, source)
