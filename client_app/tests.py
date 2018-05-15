from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse

from .models import Session

class SessionTestCase(TestCase):
	def setUp(self):
		client = Client()

		Session.objects.create( 
			matrix_user_name = "a-b+c=d.e,f#g~h@i'j;k:l!mnopqrstuvwxyz_123456789",
			matrix_room_name = "#testing_room:matrix.org",
			matrix_server = "https://matrix.org",
			message_count = 9999,
			show_images = True,
			matrix_token = "QGV4YW1wbGU6bG9jYWxob3N0.AqdSzFmFYrLrTmteXc",
			matrix_sync_token = "t88-5678_5787_0578_56781_56781_56781"
		)
		Session.objects.create( 
			matrix_user_name = "cat",
			matrix_room_name = "#testing_room:other_server.co",
			matrix_server = "https://other_server.co",
			message_count = 0,
			show_images = False,
			matrix_token = "QGV4YW1wbGU6bG9jYWxob3N0.AqdSzFmFYrLrTmteXc",
			matrix_sync_token = "t8-8_7_0_1_1_1"
		)

	def test_session_model_basics(self):
		"""Happy path testing"""
		first_user = Session.objects.get(matrix_user_name = "a-b+c=d.e,f#g~h@i'j;k:l!mnopqrstuvwxyz_123456789")
		second_user = Session.objects.get(matrix_user_name="cat")
		self.assertEqual(first_user.matrix_user_name, "a-b+c=d.e,f#g~h@i'j;k:l!mnopqrstuvwxyz_123456789")
		self.assertEqual(second_user.message_count, 0)
		self.assertEqual(first_user.message_count, 9999)
		self.assertEqual(first_user.matrix_room_name, '#testing_room:matrix.org')
		self.assertEqual(first_user.matrix_server, "https://matrix.org")
		self.assertEqual(second_user.matrix_token, "QGV4YW1wbGU6bG9jYWxob3N0.AqdSzFmFYrLrTmteXc")
		self.assertEqual(first_user.matrix_sync_token, "t88-5678_5787_0578_56781_56781_56781")
		self.assertEqual(second_user.show_images, False)

	def test_no_questions(self):
		"""
		If not logged in, return to first page.
		"""
		response = self.client.get(reverse('chat'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['latest_question_list'], [])