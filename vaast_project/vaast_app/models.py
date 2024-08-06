from django.db import models
import uuid
from django.utils import timezone

class Participant(models.Model):
    subject_id = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    age = models.IntegerField(null=True)
    gender = models.CharField(max_length=10, null=True)
    extra_metadata = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Participant {self.subject_id}"

class Experiment(models.Model):
    name = models.CharField(max_length=100)
    instructions = models.TextField(max_length=3000, null=True)
    font_size = models.IntegerField(default=100)
    font_size_change = models.FloatField(default=.6)
    image = models.ImageField(upload_to='experiment_images/', blank=True, null=True)  # Add this line
    is_remote = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Trial(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='trials')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    participant_id = models.CharField(null=False, max_length=100)  # Example of a participant ID field
    trial_time = models.DateTimeField(default=timezone.now)
    csv_data = models.TextField(blank=True, null=True)  # New field to store CSV data

    def __str__(self):
        return str(self.uuid)

class Word(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='words')
    word = models.CharField(max_length=100)
    expected_response = models.CharField(
        max_length=1,
        choices=[('y','Yes'), ('n','No')],
        null=True,
        blank=False  # Allow it to be blank if desired
    )
    def __str__(self):
        return self.word

class Response(models.Model):
    trial = models.ForeignKey(Trial, on_delete=models.CASCADE, related_name='responses')
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    response = models.CharField(max_length=1, null=False)  # 'y' or 'n'
    response_time = models.FloatField(null=False)  # Response time in milliseconds

    def __str__(self):
        return f'{self.word.word} - {self.response} - {self.response_time}ms'
