import json
import asyncio
import ffmpeg
import base64
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class StreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.stream_id = self.scope['url_route']['kwargs']['stream_id']
            logger.info(f"Attempting to connect to stream: {self.stream_id}")
            
            # Verify stream exists before accepting connection
            stream_url = await self.get_stream_url()
            if not stream_url:
                logger.error(f"Stream not found: {self.stream_id}")
                await self.close(code=4004)
                return

            self.room_group_name = f'stream_{self.stream_id}'
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info(f"WebSocket connection accepted for stream: {self.stream_id}")
            
            # Start streaming
            await self.start_streaming()
        except Exception as e:
            logger.error(f"Error in connect: {str(e)}")
            await self.close(code=1011)

    async def disconnect(self, close_code):
        logger.info(f"Disconnecting from stream {self.stream_id} with code: {close_code}")
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Stop streaming
        if hasattr(self, 'stream_process'):
            try:
                self.stream_process.terminate()
                logger.info(f"Stream process terminated for stream: {self.stream_id}")
            except Exception as e:
                logger.error(f"Error terminating stream process: {str(e)}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            
            if message == 'stop':
                if hasattr(self, 'stream_process'):
                    self.stream_process.terminate()
                    await self.close()
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")

    @sync_to_async
    def get_stream_url(self):
        from .models import StreamSession  # Move import here
        try:
            stream_session = StreamSession.objects.get(id=self.stream_id)
            if not stream_session.is_active:
                logger.warning(f"Stream {self.stream_id} is not active")
                return None
            return stream_session.rtsp_url
        except StreamSession.DoesNotExist:
            logger.error(f"Stream session not found: {self.stream_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting stream URL: {str(e)}")
            return None

    async def start_streaming(self):
        rtsp_url = await self.get_stream_url()
        if not rtsp_url:
            await self.send(text_data=json.dumps({
                'error': 'Stream not found or inactive'
            }))
            await self.close(code=4004)
            return

        try:
            logger.info(f"Starting FFmpeg process for stream: {self.stream_id}")
            # FFmpeg command to convert RTSP to MJPEG
            process = (
                ffmpeg
                .input(rtsp_url, rtsp_transport='tcp')  # Use TCP for better reliability
                .output('pipe:', format='mjpeg', vcodec='mjpeg', q=2)
                .overwrite_output()
                .run_async(pipe_stdout=True)
            )
            
            self.stream_process = process
            logger.info(f"FFmpeg process started for stream: {self.stream_id}")
            
            while True:
                # Read frame data
                frame_data = process.stdout.read(1024 * 1024)  # Read 1MB chunks
                if not frame_data:
                    logger.warning(f"No frame data received for stream: {self.stream_id}")
                    break
                
                # Convert to base64
                frame_base64 = base64.b64encode(frame_data).decode('utf-8')
                
                # Send frame to WebSocket
                await self.send(text_data=json.dumps({
                    'frame': frame_base64
                }))
                
                # Small delay to control frame rate
                await asyncio.sleep(0.033)  # ~30 FPS
                
        except ffmpeg.Error as e:
            error_message = f"FFmpeg error: {str(e.stderr.decode()) if e.stderr else str(e)}"
            logger.error(error_message)
            await self.send(text_data=json.dumps({
                'error': error_message
            }))
        except Exception as e:
            logger.error(f"Error in streaming: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))
        finally:
            if hasattr(self, 'stream_process'):
                try:
                    self.stream_process.terminate()
                    logger.info(f"Stream process terminated for stream: {self.stream_id}")
                except Exception as e:
                    logger.error(f"Error terminating stream process: {str(e)}")
            await self.close(code=1000) 