from django.test import TestCase
from django.db import connection
from django.utils import timezone
import uuid
from vaast_app.models import Trial, Experiment  # Import your Trial and Experiment models

class TrialModelTestCase(TestCase):
    
    def setUp(self):
        # Create an Experiment instance
        experiment = Experiment.objects.create(name="Test Experiment")

        # Create a Trial instance
        Trial.objects.create(
            experiment=experiment,
            uuid=uuid.uuid4(),  # Ensure you import uuid module: `import uuid`
            participant_id="123456",
            trial_time=timezone.now()
        )

    def test_sql_queries(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM vaast_app_trial")
            rows = cursor.fetchall()
            print(rows)  # Check if `experiment_id` is referenced, adjust as needed
