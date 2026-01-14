"""
Backend routers package
"""
from . import auth
from . import loan_details
from . import applicants
from . import predictions

__all__ = ['auth', 'loan_details', 'applicants', 'predictions']