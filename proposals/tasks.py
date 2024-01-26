from celery import shared_task

from .compliance_tool import compliance_tool, langchain_api

@shared_task
def compliance_task(nofo, pk, start, end):
    compliance_tool(nofo, pk, start, end)
    return "DONE"

@shared_task
def langchain_task(url, questions, pk):
    langchain_api(url, questions, pk)
    return "DONE"