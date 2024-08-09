from django.contrib import admin
from .models import Experiment, Trial

class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('experiment_id', 'name', 'description', 'num_trials', 'date_created')
    list_filter = ('date_created',)

class TrialAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'stimuli', 'block_name', 'valence', 'block_order')
    list_filter = ('valence',)

admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Trial, TrialAdmin)