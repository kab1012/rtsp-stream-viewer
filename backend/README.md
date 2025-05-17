# RTSP Stream Viewer Backend

This is the backend service for the RTSP Stream Viewer application. It handles RTSP stream processing and WebSocket streaming to the frontend.

## Prerequisites

- Python 3.8+
- Redis server
- FFmpeg installed on your system

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Redis:
- On macOS: `brew install redis`
- On Ubuntu: `sudo apt-get install redis-server`
- On Windows: Download from https://github.com/microsoftarchive/redis/releases

4. Install FFmpeg:
- On macOS: `brew install ffmpeg`
- On Ubuntu: `sudo apt-get install ffmpeg`
- On Windows: Download from https://ffmpeg.org/download.html

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Start Redis server:
```bash
redis-server
```

7. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

- `POST /api/streams/` - Create a new stream session
  - Body: `{"rtsp_url": "rtsp://your-stream-url"}`
  - Returns: Stream session details including ID

- `GET /api/streams/` - List all stream sessions
- `GET /api/streams/{id}/` - Get stream session details
- `POST /api/streams/{id}/stop/` - Stop a stream session

## WebSocket Endpoints

- `ws://localhost:8000/ws/stream/{stream_id}/` - WebSocket endpoint for video streaming

## Environment Variables

Create a `.env` file in the backend directory with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
```

## Notes

- The backend uses Django Channels for WebSocket support
- FFmpeg is used to process RTSP streams and convert them to MJPEG format
- Redis is used as the channel layer backend for WebSocket communication
- Make sure to configure CORS and security settings appropriately for production use 