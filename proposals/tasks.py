from celery import shared_task

from .compliance_tool import langchain_api, compliance_tool

@shared_task
def compliance_task(nofo, pk, start, end):

    from .models import Proposal
    proposal = Proposal.objects.get(pk=pk)

    print(f'Starting Compliance Tool for {pk}')

    if proposal.pages_ran <= (proposal.doc_end - proposal.doc_start):
        print(f'Pages ran {proposal.pages_ran}')
        print(f'Pages start {proposal.doc_start}')
        print(f'Pages end {proposal.doc_end}')

        start_orig = start
        if proposal.pages_ran > 0:
            start += proposal.pages_ran - 1
        compliance_tool(nofo, pk, start, end, start_orig)
        
    return "DONE"

@shared_task
def langchain_task(url, questions, pk):
    langchain_api(url, questions, pk)
    return "DONE"