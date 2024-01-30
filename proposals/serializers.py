from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import Proposal, Event, ComplianceImages, Template
from . import validators

from .compliance_tool import splitter_tool, merge_tool
from django.conf import settings

import json

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['proposal','title', 'start', 'end']

class ComplianceImagesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = ComplianceImages
        fields = ['id','proposal','title','content','title_text','content_text', 'page_number', 'flagged']

    def create(self, validated_data):
        if self.__dict__['initial_data']['process'] == "split":
            obj = ComplianceImages.objects.filter(proposal=validated_data['proposal'], id=validated_data['id']).first()

            new_obj = splitter_tool(
                boxes= json.loads(self.__dict__['initial_data']['boxes']),
                obj = obj,
                ComplianceImages=ComplianceImages,
                Proposal=Proposal,
                baseId = str(self.__dict__['initial_data']['baseId'])
            )

            validated_data['title'] = new_obj['title']
            validated_data['title_text'] = new_obj['title_text']
            validated_data['content'] = new_obj['content']
            validated_data['content_text'] = new_obj['content_text']
            validated_data['page_number'] = obj.__dict__['page_number']

            obj.delete()

            instance = super().create(validated_data)

            return instance
        
        if self.__dict__['initial_data']['process'] == "merge":
            obj_child = ComplianceImages.objects.filter(proposal=validated_data['proposal'], id=validated_data['id']).first()
            obj_parent = ComplianceImages.objects.filter(proposal=validated_data['proposal'], id=self.__dict__['initial_data']['parent_id']).first()

            merge_tool(str(obj_parent.content.file), str(obj_child.content.file), self.__dict__['initial_data']['hierarchy'], self.__dict__['initial_data']['proposal'])

            obj_child.delete()

            return obj_parent

class ProposalSerializer(serializers.ModelSerializer):
    event_set = EventSerializer(many=True, read_only=True)
    complianceimages_set = ComplianceImagesSerializer(many=True, read_only=True) #note: needs exact name for set in serializer
    edit_url = serializers.SerializerMethodField(read_only=True)
    # ---Hyperlinked Identity Field only works on a Model Serializer
    url = serializers.HyperlinkedIdentityField(
        view_name='proposal-detail',
        lookup_field='pk'    )

    title = serializers.CharField(validators=[
        validators.validate_title_no_hello,
        validators.unique_proposal_title
    ])
    class Meta:
        model = Proposal
        fields = [
            'url',
            'edit_url',
            'pk',
            'title',
            'description',
            'donor',
            'priority',
            'assigned',
            'compliance_sections',
            'event_set',
            'complianceimages_set',
            'nofo',
            'proposal_link',
            'proposal_id',
            'checklist',
            'doc_start',
            'doc_end',
            'pages_ran',
            'loading',
            'loading_checklist'
        ]

    def get_edit_url(self, obj):
        # --- this is needed as serializers don't always have the request
        request = self.context.get('request') # self.request
        if request is None:
            return None

        return reverse("proposal-edit", kwargs={"pk": obj.pk}, request=request)
    
    def create(self, validated_data):
        print("create\n\n")
        try:
            events_data = validated_data.pop('event_set')
            # complianceimages_data = validated_data.pop('complianceimages_set')
            proposal = Proposal.objects.create(**validated_data)
            for event_data in events_data:
                Event.objects.create(proposal=proposal, **event_data)
            # for complianceimage_data in complianceimages_data:
            #     ComplianceImages.objects.create(proposal=proposal, **complianceimage_data)
            # return proposal
        except:
            proposal = Proposal.objects.create(**validated_data)
            return proposal

    #Need to add in update fxn https://django.cowhite.com/blog/create-and-update-django-rest-framework-nested-serializers/
        
class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = [
            'name',
            'checklist'
            'id'
        ]