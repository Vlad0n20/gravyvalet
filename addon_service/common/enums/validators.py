from django.core.exceptions import ValidationError

from addon_service.addon_imp.known import get_imp_by_number
from addon_service.common.invocation import InvocationStatus
from addon_toolkit import AddonCapabilities


# helper for enum-based validators
def _validate_enum_value(enum_cls, value):
    try:
        enum_cls(value)
    except ValueError:
        raise ValidationError(f'no value "{value}" in {enum_cls}')


###
# validators


def validate_addon_capability(value):
    _validate_enum_value(AddonCapabilities, value)


def validate_invocation_status(value):
    _validate_enum_value(InvocationStatus, value)


def validate_imp_number(value):
    try:
        get_imp_by_number(value)
    except KeyError:
        raise ValidationError(f"invalid imp number: {value}")