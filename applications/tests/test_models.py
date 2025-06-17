from django.test import TestCase
from applications.models import Application
from users.models import CustomUser
from jobs.models import Job


class ApplicationModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
        # Create a test job
        self.job = Job.objects.create(
            title="Test Job",
            description="This is a test job",
            company="Test Company"
        )
        
        # Create a test application
        self.application = Application.objects.create(
            user=self.user,
            job=self.job,
            status="Pending"
        )
    
    def test_application_str(self):
        """Test that the __str__ method returns the expected string"""
        expected_string = f"{self.user.username} - {self.job.title} ({self.application.status})"
        self.assertEqual(str(self.application), expected_string)
        
        # Test with None user
        app = Application(job=self.job, status="Pending")
        self.assertEqual(str(app), "Unknown User - Test Job (Pending)")
        
        # Test with None job
        app = Application(user=self.user, status="Pending")
        self.assertEqual(str(app), "testuser - No Job (Pending)")
        
        # Test with None id
        app = Application(status="Pending")
        self.assertEqual(str(app), "Unknown User - No Job (Pending)")
