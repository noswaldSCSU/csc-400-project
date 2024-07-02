from django.db import models
import uuid
from django.utils import timezone

class Participant(models.Model):
    subject_id = models.CharField(max_length=100, unique=True)
    extra_metadata = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Participant {self.subject_id}"

class Experiment(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Trial(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='trials')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    participant_id = models.CharField(max_length=100)  # Example of a participant ID field
    trial_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.uuid)

class Word(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='words')
    word = models.CharField(max_length=100)
    expected_response = models.BooleanField(default=False)

    def __str__(self):
        return self.word

class Response(models.Model):
    trial = models.ForeignKey(Trial, on_delete=models.CASCADE, related_name='responses')
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    response = models.CharField(max_length=1, null=False)  # 'y' or 'n'
    response_time = models.FloatField(null=False)  # Response time in milliseconds

    def __str__(self):
        return f'{self.word.word} - {self.response} - {self.response_time}ms'
