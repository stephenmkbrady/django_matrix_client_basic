from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your Matrix Name', max_length=100)
    your_pass = forms.CharField(label='Your Matrix Password', max_length=100, widget=forms.PasswordInput)
    room = forms.CharField(label='Matrix Room', max_length=100)
    server = forms.CharField(label='Matrix Server', max_length=100)
    message_count = forms.IntegerField(label='Max Number Of Messages To Retrieve')
    show_images = forms.CharField(required=False, label='Show Images', widget=forms.CheckboxInput)

class ChatForm(forms.Form):
	text_entered = forms.CharField(label='', max_length = 300, widget=forms.Textarea(attrs={'placeholder': 'Enter text here', 'rows':3}))