# django_matrix_client_basic
### Django matrix client app with absolutely no javascript. 
#### Description
The current matrix clients available are many and varied. 
The web version looks good but is frontend heavy and not designed for older devices or even newer devices with limited resources.
Some of the lighter native clients are great but are locked to win, mac or linux. 
This client just needs a very basic browser and internet access.

#### Features
- It's simply HTML4/5, and CSS3 in your browser. 
- It's responsive so will fit all screens. 
- Smooth deploy directly to heroku.
- It runs on everything (within reason): feature phone browsers, text based browsers, iexplore, chrome based, firefox based
- Displays text with urls only or thumbnailed images with urls.
- Tested
- Toaster compatible

### Live demo version
https://peaceful-sea-58238.herokuapp.com/
(First load might be slow as you wake the heroku hobby dyno up.)

### TODO
#### Major Tasks in order of priority
- Tests are still being written and finding bugs.
- Another branch will be created with lightweight JS for async, make it behave like irc client.
#### Minor Tasks
- Add a little extra CSS to add better styling for medium to extra large screens.
- Find and add css minfier to heroku release script

