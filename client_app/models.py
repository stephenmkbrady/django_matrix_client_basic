from django.db import models

class Session(models.Model):
	matrix_server = models.CharField(max_length = 100)
	matrix_client = models.CharField(max_length = 100)
	matrix_user_name = models.CharField(max_length = 100, primary_key=True)
	matrix_room_name = models.CharField(max_length = 100, default="")
	message_count = models.IntegerField(default= 1)
	show_images = models.BooleanField(default = False)
	# matrix session token
	matrix_token = models.CharField(max_length = 1000)
	# matrix "time" token, stored with every request
	matrix_sync_token = models.CharField(max_length = 200)
	messages = models.TextField(null=True)
