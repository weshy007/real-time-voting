import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Sum
from django.shortcuts import get_object_or_404

from .models import Poll, Choice


class PollConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.poll_id = self.scope['url_route']['kwargs']['poll_id']
        self.poll_group_name = f'poll_{self.poll_id}'

        await self.channel_layer.group_add(
            self.poll_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, Close_code):
        await self.channel_layer.group_discard(
            self.poll_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        choice_id = text_data_json['choice_id']
        message_type = text_data_json['type']

        if message_type =='vote_cast':
            # Cast the vote
            choice_id, votes, total_votes = await self.cast_vote(choice_id)

            # Send a message with the updated vote count to WebSocket clients
            await self.send_vote_update(choice_id, votes, total_votes)

    async def send_vote_update(self, choice_id, votes, total_votes):
        message = {
            'type': 'vote_update',
            'choice_id': choice_id,
            'votes': votes,
            'total_votes': total_votes
        }

        await self.channel_layer.group_send(
            self.poll_group_name,
            {
                'type': 'send.message',
                'message': message
            }
        )

    async def send_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

    @sync_to_async
    def cast_vote(self, choice_id):
        choice = get_object_or_404(Choice, pk=choice_id)
        poll = get_object_or_404(Poll, pk=choice.poll_id)
        total_votes = poll.change_set.aggregate(Sum('votes'))['votes__sum']

        # Perform the update in an asynchronous context
        choice.votes += 1
        choice.save()

        total_votes += 1
        return choice.id, choice.votes, total_votes