from __future__ import absolute_import, unicode_literals

from celery import shared_task

from proposals.compliance_tool_lp import compliance_tool, add_import

# @shared_task
# def add(x, y):
#     return x + y

@shared_task
def compliance_fxn(file, pk):
    return compliance_tool(file, pk)

@shared_task
def add(x, y):
    return add_import(x,y)

__all__ = [
    compliance_fxn,
    add,
]