from django.shortcuts import render, get_object_or_404, redirect
from .forms import RegisterParticipantForm
from .models import Participant, Trial, Response, Experiment, Response, Word
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
import random
import json

# Start Experiment View
def start_experiment(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    trials = list(Trial.objects.all())
    random.shuffle(trials)

    request.session['participant_id'] = participant.id
    request.session['trials'] = [trial.id for trial in trials]
    request.session['current_trial_index'] = 0

    return redirect('run_trial')

# Save Response View
@csrf_exempt
def save_response(request):
    if request.method == 'POST':
        participant = get_object_or_404(Participant, id=request.session['participant_id'])
        current_trial_index = request.session['current_trial_index']
        trial_ids = request.session['trials']
        trial = get_object_or_404(Trial, id=trial_ids[current_trial_index])
        
        response_time = float(request.POST['response_time'])
        response_key = request.POST['response_key']

        correct_response = 'Y' if trial.valence == 1 else 'N'
        accuracy = 1 if response_key == correct_response else 0

        Response.objects.create(
            participant=participant,
            trial=trial,
            response_time=response_time,
            accuracy=accuracy
        )
        
        request.session['current_trial_index'] += 1

        return redirect('run_trial')

def start_trial(request):
    if request.method == 'POST':
        experiment_id = request.POST.get('experiment_id')
        experiment = Experiment.objects.get(id=experiment_id)
        trial = Trial.objects.create(
            experiment=experiment,
            participant_id='Participant001',  # Replace with actual participant ID
            trial_time=timezone.now()  # Replace with the actual time of the trial
        )
        return JsonResponse({'trial_uuid': trial.uuid})

    return JsonResponse({'status': 'error'}, status=400)

def save_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        trial_uuid = data.get('trial_uuid')
        word_id = data.get('word_id')
        response = data.get('response')
        response_time = data.get('response_time')

        trial = Trial.objects.get(uuid=trial_uuid)
        word = Word.objects.get(id=word_id)

        Response.objects.create(
            trial=trial,
            word=word,
            response=response,
            response_time=response_time
        )

        return JsonResponse({'status': 'ok'})

    return JsonResponse({'status': 'error'}, status=400)

def experiment_view(request, experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    words = list(experiment.words.values_list('word', flat=True))
    return render(request, 'experiment.html', {'words': words})

# Experiment Complete View
def experiment_complete(request):
    return render(request, 'experiment_complete.html')
