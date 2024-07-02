from django.contrib import admin
from .models import Participant, Trial, Response, Word, Experiment
from django.urls import reverse
from django.utils.html import format_html

#Removes django references from admin portal
admin.site.site_header = "VAAST Experiment Dashboard"
admin.site.site_title = "VAAST Experiment"
admin.site.index_title = "Welcome to the VAAST Experiment Admin Dashboard"

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('subject_id','first_name', 'last_name', 'age')
    search_fields = ('subject_id', 'first_name')

class ResponseInline(admin.TabularInline):
    model = Response
    extra = 0  # To prevent any extra blank response forms

@admin.register(Trial)
class TrialAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'experiment', 'participant_id', 'trial_time')
    list_filter = ('experiment', 'trial_time')
    search_fields = ('uuid', 'participant_id')
    list_display = ('uuid', 'experiment', 'participant_id', 'trial_time')
    inlines = [ResponseInline]

class WordInline(admin.TabularInline):
    model = Word
    extra = 1

class ExperimentAdmin(admin.ModelAdmin):
    inlines = [WordInline]
    list_display = ('id', 'name', 'link_to_experiment')

    def link_to_experiment(self, obj):
        link = reverse('experiment', args=[obj.id])
        return format_html('<a href="{}">Link to Experiment</a>', link)

    link_to_experiment.short_description = 'Experiment Link'
admin.site.register(Experiment, ExperimentAdmin)

