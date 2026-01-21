# slskd-gotify-notify

A Docker-based integration that bridges [slskd](https://github.com/slskd/slskd) event notifications to [Gotify](https://gotify.net/) push notifications, enabling real-time mobile alerts for Soulseek download events and private messages.

## Features

- **Download Complete Notifications**: Get notified when downloads finish with artist, album, and username details
- **Download Failed Notifications**: Receive alerts when downloads fail with error information
- **Private Message Notifications**: Instant push notifications for Soulseek private messages
- **Smart Message Formatting**: Automatically extracts and formats artist/album metadata from directory structures
- **Priority Levels**: Different notification priorities for various event types
- **Docker Integration**: Python and dependencies installed directly in the slskd container

## Prerequisites

- Docker and Docker Compose
- [Gotify](https://gotify.net/) server with an application token
- Basic understanding of Docker volumes and networking

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/powerdove/slskd-gotify-notify.git
cd slskd-gotify-notify
```

### 2. Configure Environment Variables

Edit the `compose.yml` file or rename `.env.example` to `.env` & adjust your Gotify variables (for initial configuration):

```env
GOTIFY_USER=YourUsername
GOTIFY_PASS=YourPassword
```

### 3. Configure Python Script

Navigate to `slskd-scripts` & edit the variables in gotify-notify.py to point to your Gotify server address & token:

```bash
cd slskd-scripts
nano gotify-notify.py
```

```
GOTIFY_URL = "http://GOTIFYURL:8000/message"
GOTIFY_TOKEN = "YOURTOKEN"
```

### 4. Build and Deploy

The included `Dockerfile.slskd` extends the official slskd image and installs Python and required dependencies:

```bash
docker compose up -d
```

This will:
- Build a custom slskd image with Python and the `requests` library
- Copy the notification script into the container
- Configure slskd to use the script for event notifications

## Configuration

### slskd Event Integration

Edit the `Integration` section of your `slskd.yml` configuration file to include the script paths for event triggers:

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

### Rebuilding After Updates

Rebuild when SLSKD releases updates
```
docker compose build --no-cache slskd

docker compose up -d slskd
```

Or pull new base image first
```
docker pull slskd/slskd:latest

docker compose build slskd

docker compose up -d slskd
```

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

## Project Structure

```
slskd-gotify-notify/
├── Dockerfile.slskd           # Custom slskd image with Python
├── example-compose.yml        # Docker Compose configuration
├── .env.example               # Environment variable configuration
├── slskd-scripts/
│   └──	gotify-notify.py       # Notification script
└── README.md                  # This file
```

## How It Works

1. The custom Dockerfile extends the official slskd image and installs Python 3 and the `requests` library
2. The notification script is mounted into the container at `/app/scripts/`
3. slskd's event bus triggers the script when downloads complete/fail or private messages arrive
4. The script reads event data from the `SLSKD_SCRIPT_DATA` environment variable
5. Event information is parsed, formatted, and sent to your Gotify server via REST API

## Troubleshooting

### Script Not Executing

- Check Docker logs: `docker logs slskd`
- Verify the script has execute permissions in the container
- Ensure the script path in `slskd.yml` matches the container path

### No Notifications Received

- Verify your Gotify server is accessible from the Docker network
- Test the Gotify API manually:
```bash
curl "http://your-gotify-server/message?token=YOUR_TOKEN" \
  -F "title=Test" \
  -F "message=Test message" \
  -F "priority=5"
```
- Check slskd logs for script execution errors: `docker logs slskd`

### Python Dependencies Missing

- Rebuild the Docker image: `docker compose build --no-cache`
- Verify the Dockerfile installs `python3` and `python3-requests`

### Incorrect Message Formatting

- The script attempts to extract artist/album from directory structures
- Expected directory format: `.../artist/album/files`
- If extraction fails, it falls back to showing the full directory or filename

## Customization

### Adjust Priority Levels

Modify the `priority` variable for each event type in `/slskd-scripts/gotify-notify.py`:

```python
priority = 7  # Values 0-10, higher = more urgent
```

### Custom Message Formats

Edit the message formatting logic in the event handling sections to customize output format.

### Add Additional Dependencies

Update `Dockerfile.slskd` to include additional Python packages:

```dockerfile
RUN apk add --no-cache python3 py3-pip && \
    pip3 install requests <additional-package>
```

## Docker Compose Example

The below `compose.yml` file is configured to use docker volumes, but you can also bind local directories to the container for persistent configurations.

```yaml
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
