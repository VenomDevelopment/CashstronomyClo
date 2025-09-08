from django import template

register = template.Library()

@register.filter(name='display_name')
def display_name(user):
    """
    Returns a display name for a user object.
    - Tries full name, then first name.
    - Falls back to a sanitized version of the username (email).
    - Returns 'Anonymous' for non-logged-in users.
    """
    if not user or not user.is_authenticated:
        return 'Anonymous'
    
    if user.get_full_name():
        return user.get_full_name()
    
    if user.first_name:
        return user.first_name
    
    # Fallback to username (which is the email) and sanitize it
    return user.username.split('@')[0].capitalize()