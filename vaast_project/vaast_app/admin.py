from django.contrib import admin
from .models import Participant, Trial, Response, Word, Experiment

#Removes django references from admin portal
admin.site.site_header = "VAAST Experiment Dashboard"
admin.site.site_title = "VAAST Experiment"
admin.site.index_title = "Welcome to the VAAST Experiment Admin Dashboard"

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('subject_id', 'extra_metadata', 'created_at', 'updated_at')
    search_fields = ('subject_id',)

class WordInline(admin.TabularInline):
    model = Word
    extra = 1

class ExperimentAdmin(admin.ModelAdmin):
    inlines = [WordInline]

admin.site.register(Experiment, ExperimentAdmin)
