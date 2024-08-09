from django.db import models
from django.contrib.auth.models import User

class Experiment(models.Model):
    experiment_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    num_trials = models.IntegerField(default=0)
    background_color = models.CharField(max_length=7, default="#ffffff")
    background_image = models.ImageField(upload_to='backgrounds/', null=True, blank=True)
    text_size = models.IntegerField(default=100)
    text_increase_size = models.IntegerField(default=120)
    text_decrease_size = models.IntegerField(default=80)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Trial(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='trials')
    block_order = models.IntegerField()
    stimuli = models.CharField(max_length=255)
    valence = models.IntegerField()
    text_size = models.IntegerField(default=150)
    text_color = models.CharField(max_length=7, default="#000000")
    text_increase_size = models.IntegerField(default=300)
    text_decrease_size = models.IntegerField(default=75)
    # Ensure there is a block_name field if referenced in admin.py
    block_name = models.CharField(max_length=50, default='')  # Add this if it doesn't exist

    def __str__(self):
        return self.block_name

class Participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    subject_id = models.CharField(max_length=100, unique=True)
    experiments = models.ManyToManyField(Experiment, through='Participation')

    def __str__(self):
        return self.subject_id

class Participation(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)

class Response(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    trial = models.ForeignKey(Trial, on_delete=models.CASCADE)
    response_time = models.FloatField()
    accuracy = models.IntegerField()
    
class ImageUpload(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    
    def __str__(self):
        return self.title