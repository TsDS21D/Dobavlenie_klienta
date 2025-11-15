import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ClickCounter

class CounterConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'counter'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        count = await self.get_current_count()
        await self.send(text_data=json.dumps({
            'count': count
        }))
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'increment':
            new_count = await self.increment_counter()
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'counter_update',
                    'count': new_count
                }
            )
    
    async def counter_update(self, event):
        count = event['count']
        
        await self.send(text_data=json.dumps({
            'count': count
        }))
    
    @database_sync_to_async
    def get_current_count(self):
        return ClickCounter.get_current_count()
    
    @database_sync_to_async
    def increment_counter(self):
        return ClickCounter.increment()
