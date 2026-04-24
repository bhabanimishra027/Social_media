import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.other_user_id = self.scope['url_route']['kwargs']['user_id']

        # create unique room
        self.room_name = f"chat_{min(self.user.id, self.other_user_id)}_{max(self.user.id, self.other_user_id)}"
        self.room_group_name = self.room_name

        # join room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # 🟢 SEND ONLINE STATUS
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "user": self.user.username,
                "online": True
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        message = data.get("message", None)
        typing = data.get("typing", False)
        post_id = data.get("post_id", None)

        # ⌨️ TYPING EVENT
        if typing:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "user": self.user.username,
                    "typing": True
                }
            )
            return

        # 💬 MESSAGE / POST EVENT
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "user": self.user.username,
                "message": message,
                "post_id": post_id,
                "typing": False
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "user": event.get("user"),
            "message": event.get("message"),
            "typing": event.get("typing", False),
            "post_id": event.get("post_id"),
            "online": event.get("online", False),
        }))