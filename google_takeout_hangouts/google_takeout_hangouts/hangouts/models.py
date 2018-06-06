import os
import json
import datetime
from django.conf import settings


class HangoutReader():

    def __init__(self, src_path):
        self.data = json.loads(open(str(src_path)).read())
        self.data['conversations'] = sorted(self.data['conversations'],
            reverse=True,
            key=lambda x: x['conversation']['conversation']['self_conversation_state']['sort_timestamp'])

    @property
    def conversations(self):
        return list(map(lambda conversation: Conversation(conversation), self.data['conversations']))

    def conversation(self, id):
        for conversation in self.conversations:
            if conversation.id == id:
                return conversation
        return None


class Conversation():

    def __init__(self, conversation_data):
        self.data = conversation_data
        self.data['events'] = sorted(self.data['events'], key=lambda x: x['timestamp'])

    def __unicode__(self):
        return self.name

    @property
    def name(self):
        return ", ".join([
            participant.get('fallback_name', participant['id']['gaia_id'])
            for participant in self.participants
        ])

    @property
    def id(self):
        return self.data['conversation']['conversation_id']['id']

    @property
    def participants(self):
        return self.data['conversation']['conversation']['participant_data']

    def get_participant(self, id):
        for participant in self.participants:
            if participant['id']['gaia_id'] == id:
                return participant
        return None

    @property
    def messages(self):
        return [
            Message(event, self.get_participant(event['sender_id']['gaia_id']))
            for event in self.data['events']
        ]

    @property
    def last_message(self):
        return self.messages[-1]



class Message():

    def __init__(self, data, sender):
        self.data = data
        self.sender = sender

    @property
    def text(self):
        if 'segment' in self.data['chat_message']['message_content']:
            text = []
            for segment in self.data['chat_message']['message_content']['segment']:
                if segment['type'] == 'TEXT':
                    text.append(segment['text'])
                elif segment['type'] == 'LINK':
                    text.append('<a href="{}">{}</a>'.format(
                        segment['link_data']['link_target'],
                        segment['text'],
                    ))
                elif segment['type'] == 'LINE_BREAK':
                    text.append('<br />')
            return ' '.join(text)
        else:
            return 'Unsupported Media'

    @property
    def sender_name(self):
        try:
            return self.sender.get('fallback_name', self.sender['id']['gaia_id'])
        except AttributeError:
            return '<<None>>'

    @property
    def date(self):
        return datetime.datetime.utcfromtimestamp(
            int(self.data['timestamp'])  / 1000.0 / 1000.0
        ).strftime('%c')


hangout_reader = HangoutReader(os.path.join(str(settings.ROOT_DIR), '..', 'Takeout', 'Hangouts', 'Hangouts.json'))
