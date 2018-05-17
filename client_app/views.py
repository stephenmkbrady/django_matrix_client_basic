from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import HttpResponseForbidden

from .forms import NameForm, ChatForm
from .models import Session

from matrix_client.api import MatrixHttpApi, MatrixRequestError

from datetime import datetime
import pprint, re, sys
import simplejson as json

session = Session()
pp = pprint.PrettyPrinter(indent=4)
# Serializing and deserializing json to/from string when storing in the db
jsonDec = json.decoder.JSONDecoder()

def index(request):
	if request.method == 'POST':
		print("POST form")
		form = NameForm(request.POST)
		if form.is_valid():
			for s in list(Session.objects.all()):
				print(s.matrix_user_name)
			#Get username from db or create it, and fill out the information from the form
			#Add user_name to message to pass to chat view so it knows which session to open
			messages.add_message(request, messages.INFO, form.cleaned_data['your_name'])
			if not Session.objects.filter(matrix_user_name = form.cleaned_data['your_name']):
				print("CREATE SESSION")
				session = Session.objects.create( 
					matrix_user_name = form.cleaned_data['your_name'],
					matrix_room_name = form.cleaned_data['room'],
					matrix_server = form.cleaned_data['server'],
					message_count = form.cleaned_data['message_count'],
					show_images = form.cleaned_data['show_images']
				)
				session.save()
				sys.stdout.flush()
			else:
				print("OPEN SESSION")
				session = Session.objects.get(matrix_user_name = form.cleaned_data['your_name'])
				session.matrix_user_name = form.cleaned_data['your_name']
				session.matrix_room_name = form.cleaned_data['room']
				session.matrix_server = form.cleaned_data['server']
				session.message_count = form.cleaned_data['message_count']
				session.show_images = form.cleaned_data['show_images']
				session.save()
				sys.stdout.flush()
			try:
				print("LOGIN VARS")
				print("session.matrix_user_name ", session.matrix_user_name)
				print("form.cleaned_data['your_name'] ",form.cleaned_data['your_name'])
				print("session.matrix_room_name ",session.matrix_room_name )
				print("form.cleaned_data['room'] ",form.cleaned_data['room'])
				print("session.matrix_server ",session.matrix_server )
				print("form.cleaned_data['server'] ",form.cleaned_data['server'])
				print("session.message_count ",session.message_count )
				print("form.cleaned_data['message_count'] ",form.cleaned_data['message_count'])
				print("session.show_images ",session.show_images)
				print("form.cleaned_data['show_images'] ",form.cleaned_data['show_images'])

				print("Logging in to matrix")
				sys.stdout.flush()
				api = MatrixHttpApi(session.matrix_server, token=session.matrix_token)
				response = api.login('m.login.password',user=form.cleaned_data['your_name'], password=form.cleaned_data['your_pass'])
				session.matrix_token = response["access_token"]
        
				session.save()
				sys.stdout.flush()
			except MatrixRequestError as e:
				#return HttpResponseForbidden()
				return render(request, 'client_app/login.html', {'form': form, 'login_error':True, 'error_text': str(e)})
			else:
				return HttpResponseRedirect('/chat')
	else: #GET page returns form with initial values
		form = NameForm(initial={"room":"#cosmic_horror:matrix.org","server":"https://matrix.org", "message_count":1000})
	return render(request, 'client_app/login.html', {'form': form, 'login_error':False})

def chat(request, update=""):
	user_name = None
	storage = get_messages(request)
	for message in storage:
		user_name = message
		print("MESSAGE : ", message)

	if user_name != None:
		print("username: ", user_name)
		session = Session.objects.get(matrix_user_name = user_name.message)
		print("LOGIN VARS")
		print("session.matrix_user_name ", session.matrix_user_name)
		print("session.matrix_room_name ",session.matrix_room_name )
		print("session.matrix_server ",session.matrix_server )
		print("session.message_count ",session.message_count )
		print("session.show_images ",session.show_images)
		sys.stdout.flush()
		api = MatrixHttpApi(session.matrix_server, token=session.matrix_token)
	else:
		return HttpResponseRedirect('/')

	if request.method == 'POST': #If the user hit send button
		try:
			print("Posting chat")
			sys.stdout.flush()
			chat_form = ChatForm(request.POST)
			if chat_form.is_valid():
				response = api.send_message(api.get_room_id(session.matrix_room_name), chat_form.cleaned_data['text_entered'])
				chat_form = ChatForm()
				room_topic =  api.get_room_topic(api.get_room_id(session.matrix_room_name))['topic']
				messages.add_message(request, messages.INFO, session.matrix_user_name)
				synced = _get_messages(request, sync_token="end", direction='f')
				session.messages = json.dumps( synced['chunk'] + jsonDec.decode(session.messages))
				session.save()
				return render(request, 'client_app/chat.html', 
					{'chat_form': chat_form, 'name':session.matrix_user_name, 'messages':jsonDec.decode(session.messages), 'room':session.matrix_room_name, 'topic':room_topic, 'show_images':session.show_images })

		except MatrixRequestError as e:
			print(str(e))
			sys.stdout.flush()
			form = NameForm(request.POST)
			return render(request, 'client_app/login.html', {'form': form, 'login_error':True, 'error_text': str(e)})
		else:
			return render(request, 'client_app/chat.html', 
				{'chat_form': chat_form, 'name':session.matrix_user_name, 'messages':jsonDec.decode(session.messages), 'room':session.matrix_room_name, 'topic':room_topic, 'show_images':session.show_images })
	if update == "": #If not asking for an update, get first sync to server
		try:
			chat_form = ChatForm()
			synced = api.sync()
			room_topic =  api.get_room_topic(api.get_room_id(session.matrix_room_name))['topic']
			session.matrix_sync_token = synced["next_batch"]
			messages.add_message(request, messages.INFO, session.matrix_user_name)
			synced = _get_messages(request, sync_token="start", direction='b')
			session.messages = json.dumps(synced['chunk'])
			session.save()

		except MatrixRequestError as e:
			print(str(e))
			sys.stdout.flush()
			form = NameForm(request.POST)
			return render(request, 'client_app/login.html', {'form': form, 'login_error':True})
		else:
			return render(request, 'client_app/chat.html', 
				{'chat_form': chat_form, 'name':session.matrix_user_name, 'messages':jsonDec.decode(session.messages), 'room':session.matrix_room_name, 'topic':room_topic, 'show_images':session.show_images })
	else: # update is requested so return next messages using sync token from initial sync
		chat_form = ChatForm()
		room_topic =  api.get_room_topic(api.get_room_id(session.matrix_room_name))['topic']
		messages.add_message(request, messages.INFO, session.matrix_user_name)
		synced = _get_messages(request, sync_token="end", direction='f')
		session.messages = json.dumps( synced['chunk'] + jsonDec.decode(session.messages))
		session.save()
		return render(request, 'client_app/chat.html', 
			{'chat_form': chat_form, 'name':session.matrix_user_name, 'messages':jsonDec.decode(session.messages), 'room':session.matrix_room_name, 'topic':room_topic, 'show_images':session.show_images })

def _get_messages(request, sync_token, direction):
	storage = get_messages(request)
	for message in storage:
		user_name = message
		print("MESSAGE : ", message)

	print("_get_message username: ", user_name, " : ", direction)	
	messages.add_message(request, messages.INFO, user_name)
	sys.stdout.flush()
	session = Session.objects.get(matrix_user_name = user_name.message)
	api = MatrixHttpApi(session.matrix_server, token=session.matrix_token)
	synced = api.get_room_messages(api.get_room_id(session.matrix_room_name), session.matrix_sync_token, direction, limit=session.message_count)
	session.matrix_sync_token = synced[sync_token]
	session.save()
	room_topic =  api.get_room_topic(api.get_room_id(session.matrix_room_name))['topic']
	synced['chunk'] = _parse_messages(synced['chunk'])
	return synced

def _parse_messages(input):
	# Message clean up: 
	# - Format the time from millisecond to formatted datetime
	# - Add anchor tags to url's 
	# - Fixes urls from rssbot pulled from lainchan.org
	# - Converts mxc url's to http url's
	URL_REGEX = re.compile(r'''((?:mailto:|ftp://|http://|https://)([^ <>'"{}|\\^`[\]]*))''')
	LAIN_REGEX = re.compile(r'''(\/[a-z]+\/res/[0-9]+.html)''') #lain urls from lainchan rss feed are not full urls
	for m in input:
		if 'origin_server_ts' in m:
			m['origin_server_ts'] = datetime.fromtimestamp(m['origin_server_ts']/1000.0).strftime("%Y-%m-%d %H:%M:%S")
		if 'content' in m:
			if 'formatted_body' in m['content']:
				m['content']['formatted_body'] = URL_REGEX.sub(r'<a href="\1">\1</a>', m['content']['formatted_body'])
				m['content']['formatted_body'] = LAIN_REGEX.sub(r'<a href="https://lainchan.org/\1">\1</a>', m['content']['formatted_body'])
				print(m['origin_server_ts'])
				pp.pprint(m)
				sys.stdout.flush()
			if 'msgtype' in m['content']:
				if m['content']['msgtype'] == "m.image":
					m['content']['info']['thumbnail_url'] = "http://matrix.org/_matrix/media/v1/download/" + m['content']['info']['thumbnail_url'][6:]
					m['content']['url'] = "http://matrix.org/_matrix/media/v1/download/" + m['content']['url'][6:]
				elif m['content']['msgtype'] == "m.text":
					m['content']['body'] = URL_REGEX.sub(r'<a href="\1">\1</a>', m['content']['body'])
					m['content']['body'] = LAIN_REGEX.sub(r'<a href="https://lainchan.org/\1">\1</a>', m['content']['body'])
	return input

def error(request):
	return render(request,'client_app/404.html', content_type='text/html; charset=utf-8', status=404)