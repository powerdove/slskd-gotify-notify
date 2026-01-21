# slskd-gotify-notify

A Python script that bridges [slskd](https://github.com/slskd/slskd) event notifications to [Gotify](https://gotify.net/) push notifications, enabling real-time mobile alerts for Soulseek download events and private messages.

## Features

- **Download Complete Notifications**: Get notified when downloads finish with artist, album, and username details
- **Download Failed Notifications**: Receive alerts when downloads fail with error information
- **Private Message Notifications**: Instant push notifications for Soulseek private messages
- **Smart Message Formatting**: Automatically extracts and formats artist/album metadata from directory structures
- **Priority Levels**: Different notification priorities for various event types

## Prerequisites

- [slskd](https://github.com/slskd/slskd) instance (configured and running)
- [Gotify](https://gotify.net/) server with an application token
- Docker

## Installation

1. Clone this repository:
```bash
git clone https://github.com/powerdove/slskd-gotify-notify.git
cd slskd-gotify-notify
```

2. Rename example-compose.yml to compose.yml & configure it, per your requirement:
```yml
---
name: media-stack
services:
  slskd:
    build:
      context: .
      dockerfile: Dockerfile.slskd
    container_name: slskd
    user: 1000:1000
    cap_add:
      - NET_ADMIN
    environment:
      - SLSKD_REMOTE_CONFIGURATION=true
      - "SLSKD_SHARED_DIR=/music;/ebooks"
    volumes:
      - slskd-data:/app
      - ./slskd-scripts:/app/scripts
      - /your/download/directory:/data/Soulseek Downloads
      - /your/music/directory:/music
      - /your/ebook/directory:/ebooks
    restart: "unless-stopped"

  gotify:
    image: gotify/server:latest
    container_name: gotify
    hostname: gotify
    ports:
      - 8000:80
    environment:
      - GOTIFY_DEFAULTUSER_NAME=${GOTIFY_USER}
      - GOTIFY_DEFAULTUSER_PASS=${GOTIFY_PASS}
      - TZ=Your/Timezone
    volumes:
      - gotify-data:/app/data
      - gotify-config:/etc/gotify
    restart: "unless-stopped"

volumes:
  slskd-data:
  gotify-config:
  gotify-data:
```

3. Rename .env.example to .env & adjust the environment variables, per your requirement:
```
GOTIFY_USER=YourUsername
GOTIFY_PASS=YourPassword
```

4. Make the script executable:
```bash
cd slskd-scripts
chmod +x gotify-notify.py
```

## Configuration

### 1. Update Script Variables

Edit slskd-scripts/gotify-notify.py and configure your Gotify server details:

```python
GOTIFY_URL = "http://your-gotify-server:port/message"
GOTIFY_TOKEN = "your-gotify-app-token"
```

### 2. Configure slskd Event Bus

Add the script to your slskd configuration file (typically `slskd.yml`):

```yaml
integration:
  webhooks: {}
  scripts:
    downloadcompletenotification:
      on:
        - DownloadDirectoryComplete
      run:
        command: null
        executable: /usr/bin/python3
        args: null
        arglist:
          - /app/scripts/gotify-notify.py
    privatemessagenotification:
      on:
        - PrivateMessageReceived
      run:
        command: null
        executable: /usr/bin/python3
        args: null
        arglist:
          - /app/scripts/gotify-notify.py
```

Alternatively, you can configure it via environment variables or command-line arguments according to the [slskd configuration documentation](https://github.com/slskd/slskd/blob/master/docs/config.md).

## Notification Types

### Download Complete
- **Priority**: 7
- **Format**: `Artist: {artist}\nAlbum: {album}\nFrom: {username}`
- **Fallback**: Shows directory path if artist/album cannot be extracted

### Download Failed
- **Priority**: 8
- **Format**: `Artist: {artist}\nAlbum: {album}\nFrom: {username}\nError: {error}`
- **Fallback**: Shows filename if artist/album cannot be extracted

### Private Messages
- **Priority**: 8
- **Format**: `From: {username}\n{message}`

## How It Works

The script reads event data from the `SLSKD_SCRIPT_DATA` environment variable, which slskd populates with JSON event information. It then:

1. Parses the JSON event data
2. Identifies the event type (download complete, download failed, or private message)
3. Extracts relevant information (artist, album, username, error messages)
4. Formats the notification message according to the event type
5. Sends the notification to your Gotify server via REST API

## Troubleshooting

### Script Not Executing

- Ensure the script has execute permissions (`chmod +x`)
- Verify the script path in your slskd configuration is absolute
- Check slskd logs for script execution errors

### No Notifications Received

- Verify your Gotify server URL and token are correct
- Test the Gotify API manually:
```bash
curl "http://your-gotify-server/message?token=YOUR_TOKEN" \
  -F "title=Test" \
  -F "message=Test message" \
  -F "priority=5"
```
- Check the script's stderr output in slskd logs

### Incorrect Message Formatting

- The script attempts to extract artist/album from directory structures
- Directory format should follow: `.../artist/album/files`
- If extraction fails, it falls back to showing the full directory or filename

## Customization

### Adjust Priority Levels

Modify the `priority` variable for each event type in the script:

```python
priority = 7  # Values 0-10, higher = more urgent
```

### Custom Message Formats

Edit the message formatting logic in the event handling sections to customize output format.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - feel free to use and modify as needed.

## Related Projects

- [slskd](https://github.com/slskd/slskd) - Modern client-server application for Soulseek
- [Gotify](https://gotify.net/) - Self-hosted push notification server
- [slskd-python-api](https://github.com/bigoulours/slskd-python-api) - Comprehensive Python API for slskd

## Acknowledgments

Built for the slskd and Gotify communities to enhance the Soulseek experience with real-time mobile notifications.
