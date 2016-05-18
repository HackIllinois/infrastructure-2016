from www.libs import inflection
import json
from www import errors

def byteify(input):
    """
    Encodes a String as UTF-8, as described by the thread
    http://stackoverflow.com/a/13105359/996249
    :input the String to encode
    """
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def make_response(data):
    """
    Creates a 200-status JSON response with the provided data
    and returns it to the caller
    :data the data to include in the response
    """

    response = { "meta": { 'status': 200 }, "data": data }
    return response

def make_error(errors):
    """
    Creates a JSON response with the provided errors. The status
    is determined by the highest code in the provided list of errors.
    The response object is returned to the caller
    :errors a single error or list of errors
    """

    error_list = []
    if type(errors) is not list:
        errors = [errors]
    for error in errors:
        error_list.append(error.to_dict())

    status = max(error.status for error in errors)
    response = { "meta": { 'status': status }, "errors": error_list }
    return response

def make_validation_error(validation_exception):
    """
    Creates a JSON response with the provided exception
    converted into an InvalidParameterError, returning the response
    to the caller
    :validation_exception an exception of type ValidationException
    """

    message = validation_exception.message
    source = None
    if validation_exception.field:
        source = depythonize(validation_exception.field)

    return make_error(errors.InvalidParameterError(message, source))

def make_marshal_error(marshal_result):
    """
    Creates a JSON response if the provided marshal_result contains
    an error message by creating a MissingParameterError with that message.
    If no error message is present, then None is returned to the caller
    :marshal_result the tuple returned by marshal_request
    """

    error = None
    if marshal_result[1]:
        message = None
        source = marshal_result[1]
        error = make_error(errors.MissingParameterError(message, source))

    return error

def marshal_request(arguments, expected):
    """
    Extracts the required and allowed arguments from the
    arguments object. The caller will receive a tuple containing
    the marshalled arguments in position 0, and an error description
    in position 1 if the an argument was required, but not found.
    :arguments the request data received by the API
    :expected the dictionary containing the allowed and required parameters
    """

    arguments = byteify(json.loads(arguments))
    required = expected.get('required', [])
    allowed = expected.get('allowed', [])

    marshalled_arguments = {}
    for key, value in arguments.iteritems():
        if (key in required or key in allowed):
            marshalled_arguments[key] = value

    missing = list(set(required) - set(marshalled_arguments.keys()))
    return (marshalled_arguments, missing)

def pythonize(word):
    """
    Returns a word in underscore-form
    For example: someKey -> some_key
    """

    return inflection.underscore(word)

def pythonize_dict(dictionary):
    """
    Returns a new dictionary in which all keys have been pythonized
    """

    new_dictionary = {}
    for key, value in dictionary.iteritems():
        key = inflection.underscore(key)
        new_dictionary[key] = value

    return new_dictionary

def depythonize(word):
    """
    Returns a word in camelized form
    For example: some_key -> someKey
    """

    return inflection.camelize(word, False)

def depythonize_dict(dictionary):
    """
    Returns a new dictionary in which all keys have been depythonized
    """

    new_dictionary = {}
    for key, value in dictionary.iteritems():
        key = inflection.camelize(key, False)
        new_dictionary[key] = value

    return new_dictionary
