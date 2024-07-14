from django.contrib.auth import get_user_model
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..models import OrganizerProfile
from .base import BaseTestCase

class RegistrationTest(BaseTestCase):

    def test_user_registration(self):
        self.fill_registration_form(
            email="testuser@example.com",
            name="Test User",
            password="P@ssw0rd!2024$Secure",
            instagram_account="https://instagram.com/testuser"
        )

        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )

        User = get_user_model()
        user = User.objects.get(email="testuser@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "Test User")

        organizer_profile = OrganizerProfile.objects.get(user=user)
        self.assertIsNotNone(organizer_profile)
        self.assertTrue(organizer_profile.gdpr_consented)
        print("User and organizer profile created and verified successfully.")
