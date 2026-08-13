from rest_framework.exceptions import Throttled, ValidationError
from rest_framework.views import exception_handler as drf_exception_handler


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    if isinstance(exc, ValidationError):
        code = 'validation_error'
        message = 'The submitted data is invalid.'
        details = response.data
    else:
        codes = exc.get_codes() if hasattr(exc, 'get_codes') else 'error'
        code = codes if isinstance(codes, str) else 'error'
        detail = response.data.get('detail') if isinstance(response.data, dict) else None
        message = str(detail or 'The request could not be completed.')
        details = {}

    response.data = {
        'error': {
            'code': code,
            'message': message,
            'details': details,
        }
    }

    if isinstance(exc, Throttled) and exc.wait is not None:
        response.data['error']['retry_after'] = int(exc.wait)

    return response
