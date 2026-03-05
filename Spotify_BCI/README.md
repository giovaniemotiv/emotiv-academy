# Brain-Computer Interface Controlled Spotify Player

Developed by Emotiv Academy.  
Control Spotify playback—pause and resume music—using your brain with an Emotiv EEG headset.

## Overview

This project enables real-time Spotify playback control using mental commands or facial expressions detected by the Emotiv headset. The system maps "push" or "clench" to pause, and "pull" or "smile" to resume music. It uses a lightweight Flask server, integrates with the Spotify Web API, and provides visual feedback for command recognition.

A step-by-step tutorial video is available [here](https://www.youtube.com/watch?v=-mUKNqEfIxo).

## Features

- **Spotify Web API integration**: Play/pause music with your brain.
- **Real-time BCI control**: Use mental commands or facial expressions for hands-free operation.
- **Smart Debouncing**: Automatically prevents sending redundant back-to-back requests to the Spotify API when continuous mental commands are detected.
- **Detailed Error Logging**: Console output for authentication failures and REST API exceptions directly in the terminal to assist with debugging.
- **Auto-Browser Login**: Automatically opens the Spotify authentication flow in your default browser on startup.
- **Educational Codebase**: Simple Python + Flask code, ideal for learning BCI-Web API integration.
- **Cortex API integration**: Robust connection for EEG streaming and command detection.
- **Customizable mapping**: Easily change which commands trigger which Spotify actions.

## Requirements

- Python 3.8+ (recommended: Python 3.9)
- Emotiv headset ([purchase here](https://www.emotiv.com/))
- [Cortex Service](https://www.emotiv.com/developer/) (Windows/macOS only)
- Flask: `pip install flask`
- requests: `pip install requests`
- websocket-client: `pip install websocket-client`
- python-dispatch: `pip install python-dispatch`

## Getting Started

1. **Clone this repository:**
    ```bash
    git clone https://github.com/Emotiv/emotiv-academy.git
    cd emotiv-academy/Spotify_BCI
    ```

2. **Install dependencies:**
    ```bash
    pip install flask requests websocket-client python-dispatch
    ```

3. **Create applications:**
    - **Spotify App**: [Create one here](https://developer.spotify.com/dashboard). **Note:** You must have a Spotify Premium account to create an app. Additionally, you must add your full name and email address in the "User Management" tab on the app dashboard. Once created, note your client ID/secret.
    - **Emotiv Cortex App**: [Register here](https://account.emotiv.com/my-account/cortex-apps/).

4. **Setup hardware and software:**
    - Get an Emotiv headset.
    - Download and install Cortex service.
    - Log in and accept EMOTIV policies via the Launcher.
    - Train "push" and "pull" (or facial expressions) in EmotivBCI until accuracy is sufficient.

5. **Run the app:**
    ```bash
    python spotify_bci.py
    ```

6. **Configure settings:**
    The application will automatically open `http://127.0.0.1:5000/` in your default browser roughly 1 second after starting. (If it doesn't open automatically, manually navigate to the link.)
    
    Here, you will use the visual configuration interface to set your:
    - Spotify and Emotiv App Credentials
    - Trained Emotiv profile name (optional)
    - Specific Headset ID (optional)
    - Input modality toggles (Mental commands and/or Facial expressions)
    - Mental command mapping & thresholds (e.g., mapping "push" to pause and "pull" to resume)
    
    *Note: Your settings will be automatically saved to a local `credentials.config` file on your machine. The next time you run `spotify_bci.py`, the form will be pre-filled with these settings. If you want to wipe or reset your saved settings, simply delete `credentials.config`.*

7. **Authorize Spotify:**
    Click **Start Application and Login to Spotify** at the bottom of the configuration page to authorize access and launch the BCI integration.

## Project Structure

- `spotify_bci.py`: Main application entry point.
- `cortex.py`: Cortex API wrapper for EEG data and command recognition.
- `templates/`: (If present) Flask HTML templates for visual feedback.

## Troubleshooting

- **Connection issues:** Ensure Cortex service is running and you are logged in via the EMOTIV Launcher.
- **No command detected:** Retrain your profile in EmotivBCI for better accuracy.
- **Spotify login problems:** Double-check your Spotify app credentials and redirect URIs.

## Resources

- [Cortex API Data Subscription Documentation](https://emotiv.gitbook.io/cortex-api/data-subscription)
- [EMOTIV Developer Portal](https://www.emotiv.com/developer/)
- [YouTube Tutorial](https://www.youtube.com/watch?v=-mUKNqEfIxo)

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss.

---

If you need additional help, consult the [EMOTIV support site](https://www.emotiv.com/pages/contact) or open a GitHub issue.
