from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse

from .models import Session
import pprint, os, random

class SessionTestCase(TestCase):	
	pp = pprint.PrettyPrinter(indent=4)
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

	# Testing views
	# Happy path tests		
	def test_chat_update(self):
		pass

	def test_not_logged_in(self):
		"""
		If not logged in, return to first page.
		This will happen if there is no token in the session.
		"""
		response = self.client.get(reverse('chat'))
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, "/")

	def test_fourohfour_source(self):
		"""
		Test that the 404 is returned and that it's the correct 404 and not the debug 404
		"""
		response = self.client.get("/test")
		self.assertEqual(response.status_code, 404)
		self.assertEqual(response.content.decode('utf-8'), ('\n'
 '<head>\n'
 '  <link rel="stylesheet" type="text/css" '
 'href="/static/client_app/text_page.57c227b8a5d3.css" />\n'
 '\t<meta name="viewport" content="width=device-width, initial-scale=1">\n'
 '</head>\n'
 '<body class="crt">\n'
 '<center>\n'
 '██╗  ██╗ ██████╗ ██╗  ██╗\n'
 '██║  ██║██╔═████╗██║  ██║\n'
 '███████║██║██╔██║███████║\n'
 '╚════██║████╔╝██║╚════██║\n'
 '     ██║╚██████╔╝     ██║\n'
 '     ╚═╝ ╚═════╝      ╚═╝\n'
 '     <div class="txt crt">File not Found\n'
 '     \n'
 ' (\\_/)\n'
 " (='.'=)\n"
 "('')('')\n"
 ' </div>\n'
 '     <div class="quote">\n'
 '     On this the White Rabbit blew three blasts on the trumpet, \n'
 '     and then unrolled the parchment scroll, and read as follows:\n'
 '\n'
 '   <i>‘The Queen of Hearts, she made some tarts,\n'
 '      All on a summer day:\n'
 '    The Knave of Hearts, he stole those tarts,\n'
 '      And took them quite away!’ \n'
 '      </i>\n'
 "      <cite> Alice's Adventures in Wonderland, Lewis Carroll</cite>\n"
 '</div>\n'
 '</center>\n'
 '</body>'))

	def test_form_incorrect_login_handled_correctly(self):
		response = self.client.post('/', {'your_name':'zxczcasdasd', 'your_pass':'sdsdsd','room':'#cosmic_horror:matrix.org', 'server':'https://matrix.org', 'message_count':'100', 'show_images':True})
		self.assertEqual(response.status_code, 200)
		# self.pp.pprint(response.content.decode('ascii'))
		self.assertContains(response, '''<div class="header marquee"><h2> Login Error: 403:''', count=1)

	def test_login_and_send_chat(self):
		'''
		export TEST_USER="your_test_user_name_registered_with_matrix_server"
		export TEST_PASS="your_test_user_names_pass"
		export TEST_ROOM='#your_room:matrix.org'
		Send a test message
		This also tests login works correctly
		Choose your own room to test in, don't test in any room without permission
		Sending a "random" number with string and verifying it got there.
		'''
		random_int = random.randint(0,1000)
		user = os.environ.get('TEST_USER')
		password = os.environ.get('TEST_PASS') 
		room = os.environ.get('TEST_ROOM') 
		server = 'https://matrix.org'
		message_count = 4
		show_images = False
		response = self.client.post('/', {'your_name':user, 'your_pass':password,'room':room, 'server':server, 'message_count':message_count, 'show_images':show_images})
		response = self.client.get('/chat', follow=True)
		response = self.client.post('/chat/', {'text_entered':'testing from test run'+str(random_int)}, follow=True)
		self.assertContains(response, 'testing from test run'+ str(random_int), count=1)
		'''
		Testing the page update here, 
		it's not a great test as it just checks the last message is there. 
		TODO: Will have to think of some better way to test this
		'''
		response = self.client.get('/chat/true', follow=True)
		self.assertContains(response, 'testing from test run'+ str(random_int), count=1)

	
	def test_login_and_chat_page_source(self):
		'''
		export TEST_USER="your_test_user_name_registered_with_matrix_server"
		export TEST_PASS="your_test_user_names_pass"
		export TEST_ROOM='#your_room:matrix.org'
		Send a test message
		This also tests login works correctly
		Choose your own room to test in, don't test in any room without permission
		'''
		user = os.environ.get('TEST_USER')
		password = os.environ.get('TEST_PASS') 
		room = os.environ.get('TEST_ROOM') 
		server = 'https://matrix.org'
		message_count = 1 
		show_images = False
		response = self.client.post('/', {'your_name':user, 'your_pass':password,'room':room, 'server':server, 'message_count':message_count, 'show_images':show_images})
		response = self.client.get('/chat', follow=True)
		self.assertContains(response, '''<div class="header marquee"><h3>Handle:''', count=1)
		self.assertContains(response, '''<div class="padding">  </div>\n\t<div id="bottom"></div>''', count=1)
		self.assertContains(response, '''"Enter text here" maxlength="300" required id="id_text_entered">''', count=1)
		