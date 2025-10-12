"""
Customer Portal Blueprint

Handles customer authentication, job submission, viewing, and editing.
"""

from flask import Blueprint

customer_portal_bp = Blueprint(
    "customer_portal",
    __name__,
    url_prefix="/customer",
    template_folder="../../templates/customer_portal",
    static_folder="../../static"
)

# Import modules that register routes on the blueprint
# Note: These modules will import customer_portal_bp from this module
from . import auth  # noqa: F401
from . import dashboard  # noqa: F401
from . import jobs  # noqa: F401
