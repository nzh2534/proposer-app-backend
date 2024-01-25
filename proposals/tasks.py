from celery import shared_task

from .compliance_tool import compliance_tool

@shared_task
def compliance_task(nofo, pk, start, end):
    compliance_tool(nofo, pk, start, end)
    return "DONE"