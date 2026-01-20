from django import template

register = template.Library()

@register.filter
def can_edit(submission, user):
    return submission.can_user_edit(user)
