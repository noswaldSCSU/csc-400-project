from django import forms
from django.forms import modelformset_factory
from .models import Experiment, Trial, Participant, ImageUpload

class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ['experiment_id', 'name', 'description', 'instructions', 'num_trials', 'background_color', 'background_image', 'text_size', 'text_increase_size', 'text_decrease_size']

class InstructionsForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ['instructions', 'num_trials', 'background_color', 'background_image']

class TrialForm(forms.ModelForm):
    class Meta:
        model = Trial
        fields = ['stimuli', 'valence', 'text_size', 'text_color', 'text_increase_size', 'text_decrease_size']

TrialsFormSet = modelformset_factory(Trial, form=TrialForm, extra=1)

class RegisterParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['subject_id']
        
class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageUpload
        fields = ['title', 'image']