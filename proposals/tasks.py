from celery import shared_task

from .compliance_tool import compliance_tool

@shared_task
def compliance_task(nofo, pk, toc):
    #Proposals was imported here as celery cannot be passed anything not JSON serializable
    from .models import Proposal
    proposal = Proposal.objects.get(pk=pk)
    compliance_tool(nofo, pk, toc, proposal)
    return "DONE"