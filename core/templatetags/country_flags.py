from django import template
register = template.Library()
@register.filter
def flag_emoji(country_code):
    if not country_code:
        return ''
    return ''.join(chr(127397 + ord(c.upper())) for c in country_code if c.isalpha())
