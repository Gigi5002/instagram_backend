# from rest_framework.views import exception_handler
#
#
# def custom_exception_handler(exc, context):
#     handlers = {
#         'ValidationError': _handle_generic_error,
#         'Http404': _handle_generic_error,
#         'PermissionDenied': _handle_generic_error,
#         'NotAuthenticated': _handle_generic_error,
#     }
#     response = exception_handler(exc, context)
#     exception_class = exc.__class__.__name__
#
#     if exception_class in handlers:
#         return handlers[exception_class](exc, context, response)
#     return response
#
#
# def _handle_authentication_error(exc, context, response):
#     response.data = {
#         'error': 'Please login to proceed.'
#     }
#     return response
#
#
# def _handle_generic_error(exc, context, response):
#     return response