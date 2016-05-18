import datetime

from www.libs import inflection

def to_epoch_seconds(dt):
    if dt and isinstance(dt, datetime.datetime):
        return (dt - datetime.datetime(1970,1,1)).total_seconds() * 1000
    return None

def pythonize(structure):
    result = [] if type(structure) == list else {}

    if type(structure) == list:
        for value in structure:
            result.append(inflection.underscore(str(value)))
    else:
        for key in structure:
            result[inflection.underscore(str(key))] = structure[key]
    return result

def depythonize(structure):
    result = [] if type(structure) == list else {}

    if type(structure) == list:
        for value in structure:
            result.append(inflection.camelize(str(value), uppercase_first_letter=False))
    else:
        for key in structure:
            result[inflection.camelize(str(key), uppercase_first_letter=False)] = structure[key]
    return result

def convert(dictionary, requirements):
    errors = {}
    for key in requirements:
        if key in dictionary:
            required_type = requirements[key]['type']
            try:
                if required_type == bool:
                    dictionary[key] = True if dictionary[key].lower() == 'true' else False
                elif required_type == list:
                    delimiter = requirements[key].get('delimiter', ',')
                    dictionary[key] = dictionary[key].split(delimiter)
                else:
                    dictionary[key] = required_type(dictionary[key])
            except ValueError:
                errors[key] = "This value must be a(n) %s" % required_type.__name__
    return errors
