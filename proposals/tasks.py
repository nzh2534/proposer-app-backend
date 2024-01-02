# from __future__ import absolute_import, unicode_literals

# from celery import shared_task

# from proposals.compliance_tool_lp import compliance_tool, add_import

# # @shared_task
# # def add(x, y):
# #     return x + y

# @shared_task
# def compliance_fxn(file, pk):
#     return compliance_tool(file, pk)

# @shared_task
# def add(x, y):
#     return add_import(x,y)

# __all__ = [
#     compliance_fxn,
#     add,
# ]

from celery import shared_task

from .compliance_tool import compliance_tool

@shared_task
def add(x, y):
    return x + y

@shared_task
def compliance_task(nofo, pk, toc):
    from .models import Proposal
    proposal = Proposal.objects.get(pk=pk)
    compliance_tool(nofo, pk, toc, proposal)
    return "DONE"