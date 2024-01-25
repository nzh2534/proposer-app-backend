from django.contrib import admin
from .models import Proposal, Event, ComplianceImages, Template

class EventAdminInline(admin.TabularInline):
    model = Event

class ComplianceAdminInline(admin.TabularInline):
    model = ComplianceImages

class ProposalAdmin(admin.ModelAdmin):
    inlines = [EventAdminInline, ComplianceAdminInline]

# Register your models here.
admin.site.register(Proposal, ProposalAdmin)
admin.site.register(Template)