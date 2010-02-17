from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from survey.models import Question


#TODO: Finish tests
class SimpleTest(TestCase):
    def test_visible(self):
        """Test to make sure main page works as expected"""
        response = self.client.get('/survey/visible/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response, 'Survey Example')
        self.assertEqual(response.template[0].name, 'survey/survey_list.html')

    def test_editable(self):
        """We haven't logged in yet so this should be the login page"""
        response = self.client.get('/survey/editable/')
        self.assertEqual(response.template[0].name, 'admin/login.html')
