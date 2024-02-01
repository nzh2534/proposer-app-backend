from celery import shared_task

from .compliance_tool import compliance_tool, langchain_api

@shared_task
def compliance_task(nofo, pk, start, end):

    from .models import Proposal
    proposal = Proposal.objects.get(pk=pk)

    print(f'Starting Compliance Tool for {pk}')

    if proposal.pages_ran <= (proposal.doc_end - proposal.doc_start):
        print(f'Pages ran {proposal.pages_ran}')
        print(f'Pages start {proposal.doc_start}')
        print(f'Pages ran {proposal.doc_end}')

        if proposal.pages_ran > 0:
            start += proposal.pages_ran - 1
        compliance_tool(nofo, pk, start, end)
        
    return "DONE"

@shared_task
def langchain_task(url, questions, pk):
    langchain_api(url, questions, pk)
    return "DONE"