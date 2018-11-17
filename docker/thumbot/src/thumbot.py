import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient


class Thumbot:

    def __init__(self, chat=None, message=None):
        if not chat or not message:
           return

        client = MongoClient('mongo', 27017, username=os.environ['ADMIN_USER'],
                                password=os.environ['ADMIN_PASS'], authSource='admin')
        self.db = client.thumbot

        self.chat = chat
        self.message = message
        self.check_ups_downs()
        self.ups = None
        self.downs = None

    def check_ups_downs(self):
        # I'm sure that there is a better way to do this function
        message = self.db.messages.find_one({
            'chat': self.chat,
            'message': self.message,
        })

        if not message:
            object_id = self.db.messages.insert_one({
                'chat': self.chat,
                'message': self.message,
                'ups': [],
                'downs': [],
            }).inserted_id

            message = self.db.messages.find_one({'_id': object_id})

        self.ups = message['ups']
        self.downs = message['downs']

    def _create_button(self, label, callback):
        return InlineKeyboardButton(label, callback_data=callback)

    def _create_keyboard(self, *buttons):
        keyboard = InlineKeyboardMarkup()

        return keyboard.row(*buttons)

    @classmethod
    def empty_keyboard(cls):
        t = cls()
        up_button = t._create_button('👍', 'thumb_up')
        down_button = t._create_button('👎', 'thumb_down')
        return t._create_keyboard(up_button, down_button)

    def label(self, icon, counter=None):
        if counter:
            return '{} {}'.format(icon, counter)

        return icon

    def keyboard(self):
        up_label = self.label('👍', len(self.ups))
        down_label = self.label('👎', len(self.downs))

        up_button = self._create_button(up_label, 'thumb_up')
        down_button = self._create_button(down_label, 'thumb_down')

        return self._create_keyboard(up_button, down_button)

    def update(self):
        self.db.messages.update_one(
            {
                'chat': self.chat,
                'message': self.message,
            },
            {
                '$set': {
                    'ups': self.ups,
                    'downs': self.downs
                }
            }
        )

    def up(self, user):
        if user in self.ups:
            return False

        self.ups.append(user)
        if user in self.downs:
            self.downs.remove(user)

        self.update()
        return True

    def down(self, user):
        if user in self.downs:
            return False

        self.downs.append(user)
        if user in self.ups:
            self.ups.remove(user)
        self.update()

        return True

