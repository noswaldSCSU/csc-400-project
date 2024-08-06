from django.shortcuts import render, get_object_or_404, redirect
from .forms import RegisterParticipantForm
from .models import Participant, Trial, Response, Experiment, Response, Word
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def create_trial_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            experiment = data.get('experiment')
            participant_id = data.get('participant_id')
            responses = data.get('responses')
            trial = create_trial(experiment, participant_id, responses)
            
            return JsonResponse({'status': 'success', 'trial_id': str(trial.uuid)})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def create_trial(experiment, participant_id, responses):
    # Find the experiment
    try:
        experiment = Experiment.objects.get(id=experiment)
    except Experiment.DoesNotExist:
        raise ValueError("Experiment does not exist.")

    # Create a new trial
    trial = Trial.objects.create(
        experiment=experiment,
        participant_id=participant_id,
        trial_time=timezone.now(),
    )

    # Create responses for the trial
    for response in responses:
        word_id = response['word']
        user_response = response['key']
        response_time = response['reaction_time']
        
        try:
            word = Word.objects.get(id=word_id, experiment=experiment)
        except Word.DoesNotExist:
            raise ValueError(f"Word with id {word_id} does not exist in experiment {experiment}.")

        Response.objects.create(
            trial=trial,
            word=word,
            response=user_response,
            response_time=response_time
        )

    return trial

def experiment_view(request, experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    words = list(experiment.words.values_list('word', flat=True))
    word_ids = list(experiment.words.values_list('id', flat=True))
    instructions = experiment.instructions
    font_size = experiment.font_size
    font_size_change = experiment.font_size_change
    font_size_small = font_size * (1 - font_size_change)
    font_size_big = font_size * (1 + font_size_change)

    return render(request, 'experiment.html',{'experiment': experiment,'words': words, 'word_ids': word_ids, 'instructions': instructions, 'font_size': font_size, 'font_size_small': font_size_small, 'font_size_big': font_size_big})

# Experiment Complete View
def experiment_complete(request):
    return render(request, 'experiment_complete.html')
