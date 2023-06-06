from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Proposal

# def validate_title(value):
#     qs = Proposal.objects.filter(title_iexact=value)
#     if qs.exists():
#         raise serializers.ValidationError(f"{value} is already a proposal name.")
#     return value

def validate_title_no_hello(value):
    if "hello" in value.lower():
        raise serializers.ValidationError(f"Hello is not allowed")
    return value

unique_proposal_title = UniqueValidator(queryset=Proposal.objects.all())

