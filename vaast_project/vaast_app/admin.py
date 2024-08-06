from django.contrib import admin
from django import forms
import csv
from django.http import HttpResponse
from .models import Participant, Trial, Response, Word, Experiment
from django.urls import reverse
from django.utils.html import format_html

#Removes django references from admin portal
admin.site.site_header = "MAAT Experiment Dashboard"
admin.site.site_title = "MAAT Experiment"
admin.site.index_title = "Welcome to the MAAT Experiment Admin Dashboard"

def export_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=trials_with_responses.csv'

    writer = csv.writer(response)
    
    # Write the header row
    writer.writerow([
        'Trial UUID', 'Experiment ID', 'Participant ID', 'Trial Time',
        'Word 1', 'Response 1', 'Response Time 1',
        'Word 2', 'Response 2', 'Response Time 2',
        # Add more columns if you expect more words/responses
    ])

    for trial in queryset:
        # Get all responses for the current trial
        responses = trial.responses.all()
        
        # Prepare the row data
        row = [
            trial.uuid,
            trial.experiment.id if trial.experiment else '',
            trial.participant_id,
            trial.trial_time
        ]
        
        # Add responses to the row, limit to a maximum of 10 responses for this example
        max_responses = 10
        for i in range(max_responses):
            if i < len(responses):
                response = responses[i]
                row.extend([
                    response.word.word if response.word else '',
                    response.response,
                    response.response_time
                ])
            else:
                # Fill in empty fields if there are fewer responses than max_responses
                row.extend(['', '', ''])
        
        writer.writerow(row)
    print(response)
    return response

export_as_csv.short_description = 'Export selected trials and responses as CSV'

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
    actions = [export_as_csv]  # Add the export action

class ExperimentAdmin(admin.ModelAdmin):
    inlines = [WordInline]
    list_display = ('name', 
        'instructions', 
        'font_size', 
        'font_size_change', 
        'image', 
        'is_remote')  # Add display_image here
    fields = ('name', 
        'instructions', 
        'font_size', 
        'font_size_change', 
        'image', 
        'is_remote')  # Include the image field in the admin form

    def link_to_experiment(self, obj):
        link = reverse('experiment', args=[obj.id])
        return format_html('<a href="{}">Link to Experiment</a>', link)

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "No image"

    link_to_experiment.short_description = 'Experiment Link'
    display_image.short_description = 'Image'

admin.site.register(Experiment, ExperimentAdmin)
