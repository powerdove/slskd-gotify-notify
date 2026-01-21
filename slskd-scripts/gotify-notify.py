#!/usr/bin/env python3
import os
import requests
import json
import sys

GOTIFY_URL = "http://GOTIFYURL:8000/message"
GOTIFY_TOKEN = "YOURTOKEN"

def main():
    event_json = os.getenv('SLSKD_SCRIPT_DATA')

    if not event_json:
        print("Error: SLSKD_SCRIPT_DATA environment variable not set", file=sys.stderr)
        return 1

    try:
        event_data = json.loads(event_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing event data: {e}", file=sys.stderr)
        print(f"Received data: {event_json}", file=sys.stderr)
        return 1

    if "localDirectoryName" in event_data and "remoteDirectoryName" in event_data:
        title = "Soulseek Download Complete"
        local_dir = event_data.get("localDirectoryName", "Unknown")
        remote_dir = event_data.get("remoteDirectoryName", "Unknown")
        username = event_data.get("username", "Unknown")
        album = os.path.basename(local_dir)
        remote_dir_normalized = remote_dir.replace('\\', '/')
        artist = os.path.basename(os.path.dirname(remote_dir_normalized))

        if artist and album:
            message = f"Artist: {artist}\nAlbum: {album}\nFrom: {username}"
        else:
            message = f"Directory: {local_dir}\nFrom: {username}"
        priority = 7

    elif "filename" in event_data and ("state" in event_data or "error" in event_data):
        state = event_data.get("state", "")
        error = event_data.get("error", "")

        if state == "Errored" or error:
            title = "Soulseek Download Failed"
            filename = event_data.get("filename", "Unknown")
            username = event_data.get("username", "Unknown")
            filename_normalized = filename.replace('\\', '/')
            parts = filename_normalized.split('/')
            artist = None
            album = None
            if len(parts) >= 3:
                artist = parts[-3]
                album = parts[-2]

            if artist and album:
                message = f"Artist: {artist}\nAlbum: {album}\nFrom: {username}"
                if error:
                    message += f"\nError: {error}"
            else:
                message = f"File: {os.path.basename(filename)}\nFrom: {username}"
                if error:
                    message += f"\nError: {error}"
            priority = 8
        else:
            title = "Soulseek Event"
            message = json.dumps(event_data, indent=2)
            priority = 5

    elif "username" in event_data and "message" in event_data:
        title = "Soulseek Private Message"
        username = event_data.get("username", "Unknown")
        msg_text = event_data.get("message", "")
        message = f"From: {username}\n{msg_text}"
        priority = 8
    else:
        title = "Soulseek Event"
        message = json.dumps(event_data, indent=2)
        priority = 5

    payload = {"title": title, "message": message, "priority": priority}

    try:
        url = f"{GOTIFY_URL}?token={GOTIFY_TOKEN}"
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return 0
    except Exception as e:
        print(f"Gotify notification failed: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
