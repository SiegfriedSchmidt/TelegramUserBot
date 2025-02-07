import traceback


def get_exception(ex: Exception):
    exception = traceback.format_exception(type(ex), ex, ex.__traceback__)[1:]
    exception[0] = exception[0].strip() + '\n'
    return ''.join(exception)
