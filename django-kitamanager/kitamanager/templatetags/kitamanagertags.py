from importlib.metadata import version, PackageNotFoundError
from django import template
from kitamanager.models import Employee, ChildContract, Person

register = template.Library()


try:
    _django_kitamanager_version = version("django-kitamanager")
except PackageNotFoundError:
    _django_kitamanager_version = "unknown"


@register.filter("pay_level_next")
def pay_level_next(obj, date):
    if not isinstance(obj, Employee):
        raise Exception('"pay_level_next" template filter expects a "Employee" object')
    return obj.pay_level_next(date)


@register.filter("salary")
def salary(obj, date):
    if not isinstance(obj, Employee):
        raise Exception('"salary" template filter expects a "Employee" object')
    return obj.salary(date)


@register.filter("payment")
def payment(obj, date):
    if not isinstance(obj, ChildContract):
        raise Exception(f'"payment" template filter expects a "ChildContract" object but got {obj.__class__}')
    return obj.payment(date)


@register.filter("requirement")
def requirement(obj, date):
    if not isinstance(obj, ChildContract):
        raise Exception(f'"requirement" template filter expects a "ChildContract" object but got {obj.__class__}')
    return obj.requirement(date)


@register.filter("age")
def age(obj, date):
    if not isinstance(obj, Person):
        raise Exception(f'"age" template filter expects a "Person" object but got {obj.__class__}')
    return obj.age(date)


@register.simple_tag
def django_kitamanager_version():
    return _django_kitamanager_version
