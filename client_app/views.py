from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from .forms import NameForm, ChatForm
from .models import Session

from matrix_client.client import MatrixClient, MatrixRequestError
from matrix_client.api import MatrixHttpApi

from datetime import datetime
import pprint
import re
import simplejson as json

session = Session()
pp = pprint.PrettyPrinter(indent=4)
# Serializing and deserializing json to/from string when storing in the db
jsonDec = json.decoder.JSONDecoder()

def index(request):
	if request.method == 'POST':
		form = NameForm(request.POST)
		if form.is_valid():
			session.matrix_user_name = form.cleaned_data['your_name']
			session.matrix_room_name = form.cleaned_data['room']
			session.matrix_server = form.cleaned_data['server']
			client = MatrixClient(session.matrix_server)
			session.message_count = form.cleaned_data['message_count']
			session.show_images = form.cleaned_data['show_images']
			try:
				session.matrix_token = client.login_with_password(session.matrix_user_name, password=form.cleaned_data['your_pass'])

			except MatrixRequestError as e:
				return render(request, 'client_app/login.html', {'form': form, 'login_error':True, 'error_text': str(e)})
			else:
				return HttpResponseRedirect('/chat')
	else:
		form = NameForm(initial={"your_name":session.matrix_user_name, "room":"#cosmic_horror:matrix.org","server":"https://matrix.org", "message_count":1000})
	return render(request, 'client_app/login.html', {'form': form, 'login_error':False})

def chat(request, update=""):
	api = MatrixHttpApi(session.matrix_server, token=session.matrix_token)

	if request.method == 'POST': #If the user hit send button
		try:
			chat_form = ChatForm(request.POST)
			if chat_form.is_valid():
				response = api.send_message(api.get_room_id(session.matrix_room_name), chat_form.cleaned_data['text_entered'])
				chat_form = ChatForm()
				room_topic =  api.get_room_topic(api.get_room_id(session.matrix_room_name))['topic']
				synced = _get_messages(sync_token="end", direction='f')
				session.messages = json.dumps( synced['chunk'] + jsonDec.decode(session.messages))
				return render(request, 'client_app/chat.html', 
					{'chat_form': chat_form, 'name':session.matrix_user_name, 'messages':jsonDec.decode(session.messages), 'room':session.matrix_room_name, 'topic':room_topic, 'show_images':session.show_images })

		except MatrixRequestError as e:
			print(str(e))
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
			synced = _get_messages(sync_token="start", direction='b')
			session.messages = json.dumps(synced['chunk'])

		except MatrixRequestError as e:
			print(str(e))
			form = NameForm(request.POST)
			return render(request, 'client_app/login.html', {'form': form, 'login_error':True})
		else:
			return render(request, 'client_app/chat.html', 
				{'chat_form': chat_form, 'name':session.matrix_user_name, 'messages':jsonDec.decode(session.messages), 'room':session.matrix_room_name, 'topic':room_topic, 'show_images':session.show_images })
	else: # update is requested so return next messages using sync token from initial sync
		chat_form = ChatForm()
		room_topic =  api.get_room_topic(api.get_room_id(session.matrix_room_name))['topic']
		synced = _get_messages(sync_token="end", direction='f')
		session.messages = json.dumps( synced['chunk'] + jsonDec.decode(session.messages))
		return render(request, 'client_app/chat.html', 
			{'chat_form': chat_form, 'name':session.matrix_user_name, 'messages':jsonDec.decode(session.messages), 'room':session.matrix_room_name, 'topic':room_topic, 'show_images':session.show_images })

def _get_messages(sync_token, direction):
	api = MatrixHttpApi(session.matrix_server, token=session.matrix_token)
	synced = api.get_room_messages(api.get_room_id(session.matrix_room_name), session.matrix_sync_token, direction, limit=session.message_count)
	session.matrix_sync_token = synced[sync_token]
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
			if 'msgtype' in m['content']:
				if m['content']['msgtype'] == "m.image":
					m['content']['info']['thumbnail_url'] = "http://matrix.org/_matrix/media/v1/download/" + m['content']['info']['thumbnail_url'][6:]
					m['content']['url'] = "http://matrix.org/_matrix/media/v1/download/" + m['content']['url'][6:]
				elif m['content']['msgtype'] == "m.text":
					m['content']['body'] = URL_REGEX.sub(r'<a href="\1">\1</a>', m['content']['body'])
					m['content']['body'] = LAIN_REGEX.sub(r'<a href="https://lainchan.org/\1">\1</a>', m['content']['body'])
	return input