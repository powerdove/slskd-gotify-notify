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
- Python 3.6 or higher
- `requests` library

## Installation

1. Clone this repository:
```bash
git clone https://github.com/powerdove/slskd-gotify-notify.git
cd slskd-gotify-notify
```

2. Install required Python dependencies:
```bash
pip install requests
```

3. Make the script executable:
```bash
chmod +x slskd-gotify-notify.py
```

## Configuration

### 1. Update Script Variables

Edit the script and configure your Gotify server details:

```python
GOTIFY_URL = "http://your-gotify-server:port/message"
GOTIFY_TOKEN = "your-gotify-app-token"
```

### 2. Configure slskd Event Bus

Add the script to your slskd configuration file (typically `slskd.yml`):

```yaml
integration:
  scripts:
    directory_download_completed: "/path/to/slskd-gotify-notify.py"
    directory_download_errored: "/path/to/slskd-gotify-notify.py"
    private_message_received: "/path/to/slskd-gotify-notify.py"
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
