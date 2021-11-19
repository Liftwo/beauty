from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
import logging
from asgiref.sync import async_to_sync
from redis import Redis
from random import randint
from time import sleep

logger = logging.getLogger('django')


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'ops_coffee'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print(self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message
            }
        )

    async def chat_message(self, event):
        message = 'talk_talk:' + event['message']
        await self.send(text_data=json.dumps({
            'message':message
        }))


class TrackConsumer(AsyncWebsocketConsumer):
    db = Redis(host='127.0.0.1', port=6379, db=0)

    async def connect(self):
        self.room_group_name = 'me'
        self.username = "me"
        self.accept()
    async def



class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        for i in range(1000):
            self.send(json.dumps({'message': randint(1, 100)}))
            sleep(1)








