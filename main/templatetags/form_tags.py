from django import template
from main.models import Doctor, Branch

register = template.Library()

@register.simple_tag
def get_active_doctors():
    return Doctor.objects.filter(is_active=True).order_by('order')

@register.simple_tag
def get_active_branches():
    return Branch.objects.all().order_by('order')
