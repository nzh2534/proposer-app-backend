from django.db import models
from django.urls import reverse

from django.conf import settings

from django.dispatch import receiver
from django.db.models.signals import(
    pre_save
)

from proposals.compliance_tool_lp import compliance_tool


import json

DONOR_CHOICES = (
    ('USAID','USAID'),
    ('USDOS', 'USDOS'),
    ('KOICA','KOICA'),
)

PRIORITY_CHOICES = (
    ('Low','Low'),
    ('Normal', 'Normal'),
    ('High','High'),
    ('Critical','Critical'),
)

STATUS_CHOICES = (
    ('Pre-Color Review','Pre-Color Review'),
    ('Blue Review','Blue Review'),
    ('Pink Review', 'Pink Review'),
    ('Red Review','Red Review'),
    ('Green Review','Green Review'),
    ('Gold Review','Gold Review'),
    ('White Review','White Review'),
)

COUNTRY_CHOICES = (
    ('Bangladesh','Bangladesh'),
    ('Bolivia','Bolivia'),
    ('Burundi', 'Burundi'),
    ('Cambodia','Cambodia'),
    ('Congo (Kinshasa)','Congo (Kinshasa)'),
    ('Dominican Republic','Dominican Republic'),
    ('Ethiopia','Ethiopia'),
    ('Guatemala','Guatemala'),
    ('Haiti','Haiti'),
    ('Indonesia','Indonesia'),
    ('Kenya','Kenya'),
    ('Mozambique','Mozambique'),
    ('Nicaragua','Nicaragua'),
    ('Peru','Peru'),
    ('Philippines','Philippines'),
    ('Rwanda','Rwanda'),
    ('South Sudan','South Sudan'),
    ('Uganda','Uganda'),
)

ASSIGNED_CHOICES = (
    ('Shallin','Shallin'),
    ('Claude','Claude'),
)

COLOR_CHOICES = (
    ('white','white'),
    ('#F8F8F8','#F8F8F8'),
    ('#AEBC37','#AEBC37'),
    ('red','red'),

)

class Proposal(models.Model):
    #id = pk #by default "primary key"
    title = models.CharField(max_length=200)
    donor = models.CharField(max_length=200, choices=DONOR_CHOICES, null=True)
    description = models.TextField(null=True)
    priority = models.CharField(max_length=200, choices=PRIORITY_CHOICES, default="Normal")
    status = models.CharField(max_length=200, choices=STATUS_CHOICES, default="Pre-Color Review")
    nofo = models.FileField(blank=True, null=True, default="")
    country = models.CharField(max_length=200, blank=True, null=True, choices=COUNTRY_CHOICES)
    assigned = models.CharField(max_length=200, choices=ASSIGNED_CHOICES, null=True)
    compliance_sections = models.JSONField(blank=True, null=True, default=dict)
    proposal_link = models.CharField(max_length=500, null=True, blank=True, default="")
    proposal_id = models.CharField(max_length=500, null=True, blank=True, default="")
    # word_analysis = models.JSONField(blank=True, null=True, default=dict)

    def get_absolute_url(self):
        return reverse("proposals:proposals-detail", kwargs={"pk": self.pk})

    # def set_compliance(self, x):
    #     self.compliance = json.dumps(x)

    # def get_compliance(self):
    #     return json.loads(self.compliance)

class Event(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    title = models.CharField(blank=False, max_length=30)
    start = models.DateField(blank=False)
    end = models.DateField(blank=False)

    def get_absolute_url(self):
        return reverse("proposals:proposals-detail", kwargs={"pk": self.pk})

class ComplianceImages(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    title = models.ImageField(upload_to='.', null=True, blank=True)
    content = models.ImageField(upload_to='.', null=True, blank=True)
    title_text = models.TextField(null=True, blank=True)
    content_text = models.TextField(null=True, blank=True)
    page_number = models.IntegerField(null=True, blank=True)
    flagged = models.CharField(max_length=200, choices=COLOR_CHOICES, default="white")

    def get_absolute_url(self):
        return reverse("proposals:proposals-detail", kwargs={"pk": self.pk})

# @receiver(pre_save, sender=Proposal)
# def user_created_handler(sender, instance, *args, **kwargs):
#     if instance.nofo != '':
#         if len(list(instance.complianceimages_set.all())) == 0:
#             result = compliance_tool(instance.nofo, instance.pk)
#             index = 0
#             proposal = Proposal.objects.get(pk=instance.pk)
#             for i in result[0]:
#                 new_ci = ComplianceImages(
#                     proposal=proposal,title=(settings.MEDIA_ROOT + i),
#                     content=(settings.MEDIA_ROOT + result[1][index]),
#                     title_text=result[2][index],
#                     content_text=result[3][index],
#                     page_number=result[4][index]
#                     )
#                 new_ci.save()
#                 index += 1
        # instance.compliance = result[0]
        # instance.word_analysis = result[1]
