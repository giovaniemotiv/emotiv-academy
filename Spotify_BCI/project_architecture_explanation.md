# Spotify BCI Project Architecture

This document explains the architecture, workflow, and key components of the Spotify Brain-Computer Interface (BCI) project. This application connects an Emotiv EEG headset to the Spotify API, allowing users to control music playback (Pause/Resume) using their brainwaves (Mental Commands) and Facial Expressions.

---

## 🏗️ System Overview

At a high level, the application acts as a bridge between two cloud services/APIs:
1. **Emotiv Cortex API:** Receives raw brain data from the EEG headset and translates it into recognizable "commands" or "expressions."
2. **Spotify Web API:** Receives HTTP requests to control the user's active music playback.

The system is built using **Python 3** and the **Flask** web framework, which provides a local web server to host the configuration UI and handle backend logic.

### Directory Structure
- `spotify_bci.py` - The main application file containing the Flask server and core logic linking Emotiv events to Spotify actions.
- `cortex.py` - A wrapper class for interacting with the Emotiv Cortex API via WebSockets.
- `templates/index.html` - The frontend web UI for configuring the application.
- `credentials.config` - An auto-generated JSON file that persists user settings.
- `requirements.txt` - A list of Python package dependencies.
- `windows_setup_and_run.bat` & `macOS_Linux_setup_and_run.sh` - Automated cross-platform launchers.

---

## 🔄 The User Workflow

1. **Launch**: The user runs the launcher script for their OS. The script verifies Python, installs dependencies, and boots the Flask server (`spotify_bci.py`).
2. **Configuration UI**: A browser window opens to `http://127.0.0.1:5000/`. The user fills out their API keys, headset settings, and maps their desired mental/facial commands to Pause and Resume actions.
3. **Save & Spotify Login**: Upon clicking "Start", the app saves these settings to `credentials.config`. It then redirects the user to Spotify's authorization page to grant the app permission to control their music.
4. **Emotiv Connection**: After successfully authenticating with Spotify, the app initializes the `Cortex` class. It connects to the Emotiv app running in the background, requests access, finds the headset, activates the user's trained profile, and subscribes to the designated data streams (Mental Commands and/or Facial Expressions).
5. **Real-time Control**: As the user generates brain patterns or facial expressions, the Emotiv headset pushes data to `spotify_bci.py`. If a command exceeds the user-defined threshold, a request is sent to Spotify to Pause or Resume the track.

---

## 💻 Deep Dive into Key Components

### 1. `spotify_bci.py` (The Heart of the App)
This file holds everything together. It has three main responsibilities:
- **Web Server & UI:** It uses Flask (`@app.route`) to serve the `index.html` page and handle the form submission.
- **Spotify REST API:** It handles the OAuth 2.0 flow to get a Spotify Access Token, and contains helper functions (`pause()`, `resume()`) that send HTTP POST/PUT requests to Spotify's playback endpoints.
- **Emotiv Event Listeners:** It instantiates the `Cortex` object and binds (listens) to events emitted by the Emotiv headset.

**Key Functions:**
- `on_new_com_data()`: Triggered whenever a new Mental Command (e.g., "Push", "Pull", "Neutral") is detected. It checks the command's *power* (confidence score from 0.0 to 1.0). If the power exceeds the user's chosen threshold, it triggers Spotify.
- `on_new_fe_data()`: Triggered whenever a new Facial Expression (e.g., "Smile", "Clench") is detected. It evaluates the expression and its corresponding power against the configured thresholds.

### 2. `cortex.py` (Emotiv WebSocket Protocol)
Emotiv's Cortex API is a WebSocket server running locally on the user's machine (handled by the Emotiv Launcher app). `cortex.py` is a client that connects to this WebSocket (`wss://localhost:6868`).

- **Asynchronous Communication:** WebSockets require sending a JSON request and waiting for an asynchronous JSON response.
- **Event Dispatching:** `cortex.py` uses the `PyDispatcher` library. When the WebSocket receives a message from the headset indicating a mental command occurred, `cortex.py` catches it and "dispatches" an event. `spotify_bci.py` listens for this event without having to constantly loop or poll the headset.

### 3. `templates/index.html` (The Frontend)
A simple, dynamic HTML form styled with CSS. All settings inputted here are captured by Flask when the user clicks submit. Jinja templating is used (`{{ variable_name }}`) to automatically inject the user's previously saved settings from `credentials.config` into the input boxes so they don't have to type them every time.

### 4. Debouncing and Rate Limiting
Because brain data streams are continuous, a user might hold a "Push" command for 3 seconds. The headset will fire the `on_new_com_data` event dozens of times during those 3 seconds. 

To prevent the application from spamming Spotify with 50 "Resume" requests in a row, a critical `last_spotify_action` state variable is used. It tracks whether the music is currently paused or playing. If the app detects a "Pause" command but the music is already paused, it silently ignores the command, effectively "debouncing" the requests and protecting the Spotify API limits.
