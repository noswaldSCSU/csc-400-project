from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .models import Experiment, Trial, Participant, ImageUpload, Response as ParticipantResponse
from .forms import ExperimentForm, InstructionsForm, TrialsFormSet, RegisterParticipantForm, TrialForm, modelformset_factory, ImageUploadForm
import random
import csv
from django.http import HttpResponse

TrialsFormSet = modelformset_factory(Trial, form=TrialForm, extra=0)

# Researcher Login View
class ResearcherLoginView(LoginView):
    template_name = 'maat_app/researcher_login.html'

# Data Export
@login_required
def list_completed_experiments(request):
    # Filter or determine which experiments are "completed"
    experiments = Experiment.objects.all()  # Example: change as per "completed" criteria
    return render(request, 'maat_app/list_completed_experiments.html', {'experiments': experiments})

@login_required
def export_experiment_csv(request, experiment_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    responses = ParticipantResponse.objects.filter(trial__experiment=experiment).select_related('participant', 'trial')

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{experiment.name}_responses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Participant ID', 'Trial ID', 'Stimuli', 'Valence', 'Block Name', 'Response Time (ms)', 'Accuracy (1=Correct, 0=Incorrect)', 'Date and Time'])

    for res in responses:
        writer.writerow([
            res.participant.subject_id,
            res.trial.id,
            res.trial.stimuli,
            res.trial.valence,
            res.trial.block_order,
            res.response_time,
            res.accuracy,
            res.trial.experiment.date_created.strftime('%Y-%m-%d %H:%M:%S')  # Format date
        ])

    return response

@login_required
def export_participant_csv(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    responses = ParticipantResponse.objects.filter(participant=participant).select_related('trial', 'trial__experiment')

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="participant_{participant.subject_id}_responses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Experiment ID', 'Experiment Name', 'Trial ID', 'Stimuli', 'Valence', 'Block Name', 'Response Time (ms)', 'Accuracy (1=Correct, 0=Incorrect)', 'Date and Time'])

    for res in responses:
        writer.writerow([
            res.trial.experiment.experiment_id,
            res.trial.experiment.name,
            res.trial.id,
            res.trial.stimuli,
            res.trial.valence,
            res.trial.block_order,
            res.response_time,
            res.accuracy,
            res.trial.experiment.date_created.strftime('%Y-%m-%d %H:%M:%S')  # Format date
        ])

    return response

# Home View
def home(request):
    return render(request, 'maat_app/home.html')

# Participant Login View
def participant_login(request):
    if request.method == 'POST':
        participant_id = request.POST.get('participant_id')
        experiment_id = request.POST.get('experiment_id')
        try:
            participant = Participant.objects.get(subject_id=participant_id)
            experiment = Experiment.objects.get(experiment_id=experiment_id)
            return redirect('show_instructions', participant_id=participant.id, experiment_id=experiment.id)
        except Participant.DoesNotExist:
            return render(request, 'maat_app/participant_login.html', {'error': 'Invalid Participant ID'})
        except Experiment.DoesNotExist:
            return render(request, 'maat_app/participant_login.html', {'error': 'Invalid Experiment ID'})
    return render(request, 'maat_app/participant_login.html')

# Instruction View
def show_instructions(request, participant_id, experiment_id):
    participant = get_object_or_404(Participant, id=participant_id)
    experiment = get_object_or_404(Experiment, id=experiment_id)
    if request.method == 'POST':
        return redirect('start_experiment', participant_id=participant_id, experiment_id=experiment_id)
    return render(request, 'maat_app/instructions.html', {'participant': participant, 'experiment': experiment, 'instructions': experiment.instructions})

# Experiment Start View
def start_experiment(request, participant_id, experiment_id):
    participant = get_object_or_404(Participant, id=participant_id)
    experiment = get_object_or_404(Experiment, id=experiment_id)
    trials = list(Trial.objects.filter(experiment=experiment))

    if not trials:
        return redirect('experiment_complete')

    random.shuffle(trials)
    request.session['participant_id'] = participant.id
    request.session['experiment_id'] = experiment.id
    request.session['trials'] = [trial.id for trial in trials]
    request.session['current_trial_index'] = 0
    request.session['experiment_params'] = {
        'background_color': experiment.background_color,
        'background_image_url': experiment.background_image.url if experiment.background_image else '',
        'text_size': experiment.text_size,
        'text_increase_size': experiment.text_increase_size,
        'text_decrease_size': experiment.text_decrease_size,
        'random_fixation': experiment.random_fixation if hasattr(experiment, 'random_fixation') else 1000,
    }
    return redirect('run_trial')

# Display Trial View
def run_trial(request):
    if 'current_trial_index' not in request.session:
        return redirect('participant_login')
    
    current_trial_index = request.session['current_trial_index']
    trial_ids = request.session['trials']

    if current_trial_index >= len(trial_ids):
        return redirect('experiment_complete')

    trial = get_object_or_404(Trial, id=trial_ids[current_trial_index])
    params = request.session['experiment_params']
    return render(request, 'maat_app/experiment.html', {
        'stimulus': trial.stimuli,
        'trial_id': trial.id,
        'params': params,
    })

# Capture Response View
@csrf_exempt
def save_response(request):
    if request.method == 'POST':
        participant = get_object_or_404(Participant, id=request.session['participant_id'])
        current_trial_index = request.session['current_trial_index']
        trial_ids = request.session['trials']
        trial = get_object_or_404(Trial, id=trial_ids[current_trial_index])
        
        response_time = request.POST.get('response_time')
        response_key = request.POST.get('response_key')
        
        if not response_time or not response_key:
            return HttpResponse("Invalid Response", status=400)

        correct_response = 'Y' if trial.valence == 1 else 'N'
        accuracy = 1 if response_key.upper() == correct_response else 0

        ParticipantResponse.objects.create(
            participant=participant,
            trial=trial,
            response_time=response_time,
            accuracy=accuracy
        )

        request.session['current_trial_index'] += 1
        return redirect('run_trial')

# Experiment Completion View - Save results to CSV
def experiment_complete(request):
    participant_id = request.session.get('participant_id')

    if not participant_id:
        return redirect('participant_login')

    participant = get_object_or_404(Participant, id=participant_id)
    return render(request, 'maat_app/experiment_complete.html')

# CSV Export View - Download All Results as Zip
@login_required
def download_responses_csv(request):
    results_dir = os.path.join(settings.BASE_DIR, 'experiment_results')
    files = os.listdir(results_dir)
    zip_filename = "all_responses.zip"

    with zipfile.ZipFile(os.path.join(results_dir, zip_filename), 'w') as zipf:
        for file in files:
            zipf.write(os.path.join(results_dir, file), file)

    zip_path = os.path.join(results_dir, zip_filename)
    with open(zip_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type="application/zip")
        response['Content-Disposition'] = f'attachment; filename={zip_filename}'
        return response

# List of Experiments View
@login_required
def list_experiments(request):
    experiments = Experiment.objects.all()
    return render(request, 'maat_app/list_experiments.html', {'experiments': experiments})

# Configure Experiment View
@login_required
def configure_experiment(request, experiment_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    if request.method == 'POST':
        form = ExperimentForm(request.POST, request.FILES, instance=experiment)
        if form.is_valid():
            form.save()
            return redirect('list_experiments')
    else:
        form = ExperimentForm(instance=experiment)
    return render(request, 'maat_app/configure_experiment.html', {'form': form, 'experiment': experiment})

@login_required
def create_experiment_with_image(request, image_id):
    selected_image = ImageUpload.objects.get(id=image_id)
    if request.method == 'POST':
        # Handle form submission and save experiment with the selected image
        pass
    return render(request, 'maat_app/create_experiment.html', {'selected_image': selected_image})

# Create Experiment View (Step 1)
@login_required
def create_experiment_step1(request):
    if request.method == 'POST':
        form = ExperimentForm(request.POST, request.FILES)
        if form.is_valid():
            experiment = form.save()
            return redirect('create_experiment_step2', experiment_id=experiment.id)
    else:
        form = ExperimentForm()
    return render(request, 'maat_app/create_experiment_step1.html', {'form': form})

@login_required
def create_experiment_step2(request, experiment_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    if request.method == 'POST':
        form = InstructionsForm(request.POST, request.FILES, instance=experiment)  # Include request.FILES
        if form.is_valid():
            form.save()
            return redirect('create_experiment_step3', experiment_id=experiment.id)
    else:
        form = InstructionsForm(instance=experiment)
    return render(request, 'maat_app/create_experiment_step2.html', {'form': form, 'experiment': experiment})

# Define Trials for the Experiment (Step 3)
@login_required
def create_experiment_step3(request, experiment_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    num_trials = experiment.num_trials
    TrialFormSet = modelformset_factory(Trial, form=TrialForm, extra=num_trials)

    if request.method == 'POST':
        formset = TrialFormSet(request.POST, queryset=Trial.objects.none())
        if formset.is_valid():
            trials = formset.save(commit=False)
            block_order = 1
            for trial in trials:
                trial.experiment = experiment
                trial.block_order = block_order
                block_order += 1
                trial.save()
            return redirect('list_experiments')
    else:
        formset = TrialFormSet(queryset=Trial.objects.none())
    return render(request, 'maat_app/create_experiment_step3.html', {'formset': formset, 'experiment': experiment})

# Edit Experiment View
@login_required
def edit_experiment(request, experiment_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    if request.method == 'POST':
        form = ExperimentForm(request.POST, request.FILES, instance=experiment)  # Include request.FILES
        if form.is_valid():
            form.save()
            return redirect('list_experiments')
    else:
        form = ExperimentForm(instance=experiment)
    return render(request, 'maat_app/edit_experiment.html', {'form': form, 'experiment': experiment})

# Delete Experiment View
@login_required
def delete_experiment(request, experiment_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    if request.method == 'POST':
        experiment.delete()
        return redirect('list_experiments')
    return render(request, 'maat_app/delete_experiment.html', {'experiment': experiment})

# Researcher Dashboard View
@login_required
def researcher_dashboard(request):
    experiments = Experiment.objects.all()
    participants = Participant.objects.all()
    return render(request, 'maat_app/researcher_dashboard.html', {'experiments': experiments, 'participants': participants})

# Manage Participants View
@login_required
def manage_participants(request):
    participants = Participant.objects.all()
    return render(request, 'maat_app/manage_participants.html', {'participants': participants})

# Register Participant View
@login_required
def register_participant(request):
    if request.method == 'POST':
        form = RegisterParticipantForm(request.POST)
        if form.is_valid():
            try:
                participant = form.save(commit=False)
                participant.save()  # Save participant without assigning a user if user linkage is unnecessary
                return redirect('manage_participants')
            except IntegrityError:
                form.add_error(None, 'A participant with this subject ID already exists.')
    else:
        form = RegisterParticipantForm()
    return render(request, 'maat_app/register_participant.html', {'form': form})

# Edit Participant View
@login_required
def edit_participant(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    if request.method == 'POST':
        form = RegisterParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            return redirect('manage_participants')
    else:
        form = RegisterParticipantForm(instance=participant)
    return render(request, 'maat_app/edit_participant.html', {'form': form})

# Delete Participant View
@login_required
def delete_participant(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    if request.method == 'POST':
        participant.delete()
        return redirect('manage_participants')
    return render(request, 'maat_app/delete_participant.html', {'participant': participant})

# Create Trial View
@login_required
def create_trial(request):
    experiment_id = request.GET.get('experiment')
    if not experiment_id:
        return HttpResponse("Experiment ID is required", status=400)
    
    experiment = get_object_or_404(Experiment, id=experiment_id)

    if request.method == 'POST':
        form = TrialForm(request.POST, request.FILES)
        if form.is_valid():
            trial = form.save(commit=False)
            trial.experiment = experiment
            trial.block_order = Trial.objects.filter(experiment=experiment).count() + 1  # Add the trial at the end
            trial.save()
            return redirect('researcher_dashboard')
    else:
        form = TrialForm()
    return render(request, 'maat_app/create_trial.html', {'form': form, 'experiment': experiment})

# Edit Trial View
@login_required
def edit_trial(request, trial_id):
    trial = get_object_or_404(Trial, id=trial_id)
    if request.method == 'POST':
        form = TrialForm(request.POST, request.FILES, instance=trial)
        if form.is_valid():
            form.save()
            return redirect('researcher_dashboard')
    else:
        form = TrialForm(instance=trial)
    return render(request, 'maat_app/edit_trial.html', {'form': form})

# Delete Trial View
@login_required
def delete_trial(request, trial_id):
    trial = get_object_or_404(Trial, id=trial_id)
    if request.method == 'POST':
        trial.delete()
        return redirect('researcher_dashboard')
    return render(request, 'maat_app/delete_trial.html', {'trial': trial})

# Image Upload
@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('list_images')  # Redirect to the list of uploaded images
    else:
        form = ImageUploadForm()
    return render(request, 'maat_app/upload_image.html', {'form': form})

def list_images(request):
    images = ImageUpload.objects.all()
    return render(request, 'maat_app/list_images.html', {'images': images})

def upload_success(request):
    return render(request, 'maat_app/upload_success.html')

def select_image(request):
    images = ImageUpload.objects.all()
    return render(request, 'maat_app/select_image.html', {'images': images})

def apply_image_selection(request):
    if request.method == "POST":
        selected_image_id = request.POST.get('selected_image')
        selected_image = ImageUpload.objects.get(id=selected_image_id)
        # You can now use `selected_image` as needed (e.g., save to the experiment or redirect)
        # For example, redirect to create experiment page with the selected image
        return redirect('create_experiment_with_image', image_id=selected_image_id)
    return redirect('select_image')

@login_required
def export_csv(request, experiment_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    responses = ParticipantResponse.objects.filter(trial__experiment=experiment).select_related('participant', 'trial')

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{experiment.name}_responses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Participant ID', 'Trial ID', 'Stimuli', 'Valence', 'Block Name', 'Response Time (ms)', 'Accuracy (1=Correct, 0=Incorrect)', 'Date and Time'])

    for res in responses:
        writer.writerow([
            res.participant.subject_id,
            res.trial.id,
            res.trial.stimuli,
            res.trial.valence,
            res.trial.block_order,
            res.response_time,
            res.accuracy,
            res.trial.experiment.date_created.strftime('%Y-%m-%d %H:%M:%S')  # Format date
        ])

    return response