from cortex import Cortex

import requests
import urllib.parse

from flask import Flask, redirect, request, jsonify, session
import sys
import threading
import webbrowser
import os
import json

'''
Pause Spotify music during "push" mental command using an Emotiv EEG headset.

Inputs to Update:
    -"emotiv_app_client_id" and "emotiv_app_client_secret": Emotiv credentials
    -"spotify_client_id" and "spotify_client_secret": Spotify credentials
    -"profile_name_load": The trained profile name from EmotivBCI
'''

app = Flask(__name__)
app.secret_key = ''

CONFIG_FILE = 'credentials.config'

# --- REQUIRED CONFIGURATION ---
# Default Form Values (will be replaced by values in credentials.config if it exists)
spotify_client_id = ''
spotify_client_secret = ''
emotiv_app_client_id = ''
emotiv_app_client_secret = ''

profile_name_load = ''
headset_Id = ''

# Toggles & Thresholds
enable_com = True
enable_fac = True
pause_command = 'push'
resume_command = 'pull'
pause_threshold = 0.5
resume_threshold = 0.5

def load_config():
    global spotify_client_id, spotify_client_secret, emotiv_app_client_id, emotiv_app_client_secret
    global profile_name_load, headset_Id, enable_com, enable_fac
    global pause_command, resume_command, pause_threshold, resume_threshold
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                
            spotify_client_id = config.get('spotify_client_id', '')
            spotify_client_secret = config.get('spotify_client_secret', '')
            emotiv_app_client_id = config.get('emotiv_app_client_id', '')
            emotiv_app_client_secret = config.get('emotiv_app_client_secret', '')
            profile_name_load = config.get('profile_name_load', '')
            headset_Id = config.get('headset_Id', '')
            
            enable_com = config.get('enable_com', True)
            enable_fac = config.get('enable_fac', True)
            pause_command = config.get('pause_command', 'push')
            resume_command = config.get('resume_command', 'pull')
            pause_threshold = config.get('pause_threshold', 0.7)
            resume_threshold = config.get('resume_threshold', 0.7)
        except Exception as e:
            print(f"[CONFIG WARNING] Failed to parse {CONFIG_FILE}: {e}")

load_config()

# --- Runtime Setup ---
REDIRECT_URI = 'http://127.0.0.1:5000/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'
loaded_profile = False
last_spotify_action = None

def run_emotiv():
    s = Subscribe(emotiv_app_client_id, emotiv_app_client_secret)
    streams = []
    if enable_com:
        streams.append('com')
    if enable_fac:
        streams.append('fac')
    s.start(streams, headset_Id)

@app.route('/', methods=['GET', 'POST'])
def index():
    global spotify_client_id, spotify_client_secret
    global emotiv_app_client_id, emotiv_app_client_secret, profile_name_load, headset_Id
    global enable_com, enable_fac, pause_command, resume_command, pause_threshold, resume_threshold
    
    if request.method == 'POST':
        spotify_client_id = request.form.get('spotify_client_id', '').strip()
        spotify_client_secret = request.form.get('spotify_client_secret', '').strip()
        emotiv_app_client_id = request.form.get('emotiv_app_client_id', '').strip()
        emotiv_app_client_secret = request.form.get('emotiv_app_client_secret', '').strip()
        profile_name_load = request.form.get('profile_name_load', '').strip()
        headset_Id = request.form.get('headset_Id', '').strip()
        
        enable_com = 'enable_com' in request.form
        enable_fac = 'enable_fac' in request.form
        pause_command = request.form.get('pause_command', 'push')
        resume_command = request.form.get('resume_command', 'pull')
        pause_threshold = float(request.form.get('pause_threshold', 0.7))
        resume_threshold = float(request.form.get('resume_threshold', 0.7))
        
        # Save credentials to config file
        config_data = {
            'spotify_client_id': spotify_client_id,
            'spotify_client_secret': spotify_client_secret,
            'emotiv_app_client_id': emotiv_app_client_id,
            'emotiv_app_client_secret': emotiv_app_client_secret,
            'profile_name_load': profile_name_load,
            'headset_Id': headset_Id,
            'enable_com': enable_com,
            'enable_fac': enable_fac,
            'pause_command': pause_command,
            'resume_command': resume_command,
            'pause_threshold': pause_threshold,
            'resume_threshold': resume_threshold
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            print(f"[CONFIG ERROR] Failed to save {CONFIG_FILE}: {e}")
            
        return redirect('/login')

    from flask import render_template
    return render_template('index.html', 
        spotify_client_id=spotify_client_id, spotify_client_secret=spotify_client_secret,
        emotiv_app_client_id=emotiv_app_client_id, emotiv_app_client_secret=emotiv_app_client_secret,
        profile_name_load=profile_name_load, headset_Id=headset_Id,
        enable_com=enable_com, enable_fac=enable_fac,
        pause_command=pause_command, resume_command=resume_command,
        pause_threshold=pause_threshold, resume_threshold=resume_threshold
    )

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email user-modify-playback-state user-read-playback-state'
    params = {
        'client_id': spotify_client_id,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        print(f"[SPOTIFY ERROR] Authentication failed: {request.args['error']}")
        return jsonify({"error": request.args['error']})

    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': spotify_client_id,
            'client_secret': spotify_client_secret
        }
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()
        
        if response.status_code != 200 or 'error' in token_info:
            print(f"[SPOTIFY ERROR] Token exchange failed ({response.status_code}): {token_info}")
            return jsonify(token_info), response.status_code
            
        global access_token_global
        access_token_global = token_info.get('access_token')
        print("[SUCCESS] Spotify authenticated successfully!")
        
        try:
            run_emotiv()
        except Exception as e:
            print(f"[EMOTIV ERROR] Failed to run Emotiv: {e}")
            
        return redirect('/')

@app.route('/pause')
def pause():
    global last_spotify_action
    if last_spotify_action == 'pause':
        print("[SKIP] Already paused, ignoring command")
        return "Already paused"

    print('STARTING SPOTIFY PAUSE')
    headers = {'Authorization': f"Bearer {access_token_global}"}
    url = f"{API_BASE_URL}me/player/pause"
    response = requests.put(url, headers=headers)
    if response.status_code in (200, 204):
        print("[SUCCESS] Spotify playback paused")
        last_spotify_action = 'pause'
        return "Playback paused successfully!"
    else:
        try:
            error_data = response.json()
        except Exception:
            error_data = response.text
        print(f"[SPOTIFY ERROR] /pause failed with status {response.status_code}: {error_data}")
        return jsonify(error_data), response.status_code

@app.route('/resume')
def resume():
    global last_spotify_action
    if last_spotify_action == 'resume':
        print("[SKIP] Already playing, ignoring command")
        return "Already playing"

    print('STARTING SPOTIFY RESUME')
    headers = {'Authorization': f"Bearer {access_token_global}"}
    url = f"{API_BASE_URL}me/player/play"
    response = requests.put(url, headers=headers)
    if response.status_code in (200, 204):
        print("[SUCCESS] Spotify playback resumed")
        last_spotify_action = 'resume'
        return "Playback resumed successfully!"
    else:
        try:
            error_data = response.json()
        except Exception:
            error_data = response.text
        print(f"[SPOTIFY ERROR] /resume failed with status {response.status_code}: {error_data}")
        return jsonify(error_data), response.status_code

@app.route('/devices')
def devices():
    if 'access_token' not in session:
        return redirect('/login')
    headers = {'Authorization': f'Bearer {session["access_token"]}'}
    response = requests.get(API_BASE_URL + 'me/player/devices', headers=headers)
    devices = response.json()
    return jsonify(devices)

class Subscribe():
    """
    A class to subscribe data stream.

    Attributes
    ----------
    c : Cortex
        Cortex communicate with Emotiv Cortex Service

    Methods
    -------
    start():
        start data subscribing process.
    sub(streams):
        To subscribe to one or more data streams.
    on_new_data_labels(*args, **kwargs):
        To handle data labels of subscribed data 
        To handle mental command emitted from Cortex
    """
    def __init__(self, app_client_id, app_client_secret, **kwargs):
        """
        Constructs cortex client and bind a function to handle subscribed data streams
        If you do not want to log request and response message , set debug_mode = False. The default is True
        """
        print("Subscribe __init__")
        self.c = Cortex(app_client_id, app_client_secret, debug_mode=False, **kwargs)

        #associate events from Cortex with handler functions in class
        self.c.bind(create_session_done=self.on_create_session_done)
        self.c.bind(new_data_labels=self.on_new_data_labels)
        self.c.bind(new_com_data=self.on_new_com_data)
        self.c.bind(new_fe_data=self.on_new_fe_data)
        self.c.bind(inform_error=self.on_inform_error)

    def start(self, streams, headsetId=''):
        """
        To start data subscribing process as below workflow
        (1)check access right -> authorize -> connect headset->create session
        (2) subscribe streams data

        'com' : Mental Command

    
        Parameters
        ----------
        streams : list, required
            list of streams. For example, ['eeg', 'mot']
        headsetId: string , optional
             id of wanted headet which you want to work with it.
             If the headsetId is empty, the first headset in list will be set as wanted headset
        Returns
        -------
        None
        """

        self.streams = streams
        if headsetId != '':
            self.c.set_wanted_headset(headsetId)
        self.c.open()

    def sub(self, streams):
        """
        To subscribe to one or more data streams
        'eeg': EEG
        'mot' : Motion
        'dev' : Device information
        'met' : Performance metric
        'pow' : Band power
        'com' : Mental Command

        Parameters
        ----------
        streams : list, required
            list of streams. For example, ['eeg', 'mot', 'com']

        Returns
        -------
        None
        """
        self.c.sub_request(streams)

    def unsub(self, streams):
        """
        To unsubscribe to one or more data streams
        'eeg': EEG
        'mot' : Motion
        'dev' : Device information
        'met' : Performance metric
        'pow' : Band power

        Parameters
        ----------
        streams : list, required
            list of streams. For example, ['eeg', 'mot']

        Returns
        -------
        None
        """
        self.c.unsub_request(streams)

    def on_new_data_labels(self, *args, **kwargs):
        """
        To handle data labels of subscribed data 
        Returns
        -------
        data: list  
              array of data labels
        name: stream name
        For example:
            eeg: ["COUNTER","INTERPOLATED", "AF3", "T7", "Pz", "T8", "AF4", "RAW_CQ", "MARKER_HARDWARE"]
            motion: ['COUNTER_MEMS', 'INTERPOLATED_MEMS', 'Q0', 'Q1', 'Q2', 'Q3', 'ACCX', 'ACCY', 'ACCZ', 'MAGX', 'MAGY', 'MAGZ']
            dev: ['AF3', 'T7', 'Pz', 'T8', 'AF4', 'OVERALL']
            met : ['eng.isActive', 'eng', 'exc.isActive', 'exc', 'lex', 'str.isActive', 'str', 'rel.isActive', 'rel', 'int.isActive', 'int', 'foc.isActive', 'foc']
            pow: ['AF3/theta', 'AF3/alpha', 'AF3/betaL', 'AF3/betaH', 'AF3/gamma', 'T7/theta', 'T7/alpha', 'T7/betaL', 'T7/betaH', 'T7/gamma', 'Pz/theta', 'Pz/alpha', 'Pz/betaL', 'Pz/betaH', 'Pz/gamma', 'T8/theta', 'T8/alpha', 'T8/betaL', 'T8/betaH', 'T8/gamma', 'AF4/theta', 'AF4/alpha', 'AF4/betaL', 'AF4/betaH', 'AF4/gamma']
        """
        data = kwargs.get('data')
        stream_name = data['streamName']
        stream_labels = data['labels']

    def on_new_com_data(self, *args, **kwargs):
        """
        To handle mental command data emitted from Cortex

        Returns
        -------
        data: dictionary
             The values in the array pow match the labels in the array labels return at on_new_com_data_labels
        """
        global loaded_profile
        if not loaded_profile:
            status_load = "load"
            self.profile_name = profile_name_load
            self.c.set_wanted_profile(profile_name_load)
            self.c.setup_profile(profile_name_load, status_load)
            loaded_profile = True

        active_actions = [cmd for cmd in (pause_command, resume_command) if cmd != 'neutral']
        if active_actions:
            self.c.set_mental_command_active_action(list(set(active_actions)))
            
        data = kwargs.get('data')
        action = data.get('action')
        power = data.get('power')
        time = data.get('time')
        print(f'Command Data - Action: {action}, Power: {power}, Time: {time}')
        
        if action == pause_command and (action == 'neutral' or power > pause_threshold):
            with app.test_request_context():
                pause()
        elif action == resume_command and (action == 'neutral' or power > resume_threshold):
            with app.test_request_context():
                resume()

    def on_new_fe_data(self, *args, **kwargs):
        data = kwargs.get('data')
        eye_action = data.get('eyeAct')
        upper_action = data.get('uAct')
        upper_power = data.get('uPow')
        lower_action = data.get('lAct')
        lower_power = data.get('lPow')
        time = data.get('time')
        print(f'Facial Expr Data - Eye: {eye_action}, Upper: {upper_action} ({upper_power}), Lower: {lower_action} ({lower_power}), Time: {time}')

        if lower_action and lower_action.strip().lower() == 'clench' and lower_power > 0.7:
            with app.test_request_context():
                pause()
        elif lower_action and lower_action.strip().lower() == 'smile' and lower_power > 0.7:
            with app.test_request_context():
                resume()

    def on_create_session_done(self, *args, **kwargs):
        print('on_create_session_done')
        self.sub(self.streams)

    def on_inform_error(self, *args, **kwargs):
        error_data = kwargs.get('error_data')
        print(error_data)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        threading.Timer(1.25, open_browser).start()
    app.run(host='127.0.0.1', debug=True)
