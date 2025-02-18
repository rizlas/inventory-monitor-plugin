from django import template

register = template.Library()


@register.filter
def get_status(obj, status_type):
    """
    Gets the status for the given object and status type
    Example: {{ record|get_status:'warranty' }} calls record.get_warranty_status()
    """
    method_name = f"get_{status_type}_status"
    if hasattr(obj, method_name):
        return getattr(obj, method_name)()
    return None
