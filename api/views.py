from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response

from proposals.serializers import ProposalSerializer

@api_view(["POST"])
def api_home(request, *args, **kwargs):
    data = request.data #Take the json data being sent in
    serializer = ProposalSerializer(data=data)
    if serializer.is_valid(): #making sure that the data sent to the endpoint matches how this data is formatted
        data = serializer.save()
        print(data)
        data = serializer.data
        return Response(data)