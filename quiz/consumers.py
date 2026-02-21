from channels.generic.websocket import AsyncWebsocketConsumer

class GuidedQuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.public_id = self.scope['url_route']['kwargs']['public_id']
        self.group_name = f"guided_{self.public_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass
