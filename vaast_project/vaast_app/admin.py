from django.contrib import admin
from django import forms
from .models import Participant, Trial, Response, Word, Experiment
from django.urls import reverse
from django.utils.html import format_html

#Removes django references from admin portal
admin.site.site_header = "MAAT Experiment Dashboard"
admin.site.site_title = "MAAT Experiment"
admin.site.index_title = "Welcome to the MAAT Experiment Admin Dashboard"

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('subject_id','first_name', 'last_name', 'age')
    search_fields = ('subject_id', 'first_name')

class WordInlineForm(forms.ModelForm):
    response_y = forms.BooleanField(required=False, label='Y')
    response_n = forms.BooleanField(required=False, label='N')

    class Meta:
        model = Word
        fields = ['word', 'response_y', 'response_n']  # Include only necessary fields

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Set the expected_response based on the checkboxes
        if self.cleaned_data['response_y']:
            instance.expected_response = 'y'
        elif self.cleaned_data['response_n']:
            instance.expected_response = 'n'
        else:
            instance.expected_response = None  # Handle unselected checkboxes

        if commit:
            instance.save()
        return instance

class WordInline(admin.TabularInline):
    model = Word
    form = WordInlineForm
    extra = 1

class ResponseInline(admin.TabularInline):
    model = Response
    extra = 0  # To prevent any extra blank response forms

@admin.register(Trial)
class TrialAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'experiment', 'participant_id', 'trial_time')
    list_filter = ('experiment', 'trial_time')
    search_fields = ('uuid', 'participant_id')
    inlines = [ResponseInline]

class ExperimentAdmin(admin.ModelAdmin):
    inlines = [WordInline]
    list_display = ('id', 'name', 'link_to_experiment')

    def link_to_experiment(self, obj):
        link = reverse('experiment', args=[obj.id])
        return format_html('<a href="{}">Link to Experiment</a>', link)

    link_to_experiment.short_description = 'Experiment Link'

admin.site.register(Experiment, ExperimentAdmin)
