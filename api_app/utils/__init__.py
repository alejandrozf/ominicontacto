from enum import Enum


class HttpResponseStatus(str, Enum):
    SUCCESS: str = 'SUCCESS'
    ERROR: str = 'ERROR'


def get_response_data(status=HttpResponseStatus.ERROR, data=None, message=None, errors=None):
    return {
        'status': status,
        'data': data,
        'message': message,
        'errors': errors
    }
