#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding: utf8
#
# Copyright 2019-2021 Denis Meyer
#
# This file is part of raspi-surveillance
#

"""A telegram bot - encapsulates calls to the telegram API"""

import logging

from sender.Bot import Bot


class TelegramBot(Bot):

    def __init__(self, settings):
        """Initialization

        :param settings: The settings
        """
        super().__init__(settings)

        logging.info('Initializing Telegram Bot')

        #import telegram
        self.telegram = __import__('telegram', globals(), locals(), [], 0)

        self.token = self.settings.get_sender('telegram', 'token')
        self.chat_id = self.settings.get_sender('telegram', 'chat_id')

        self.cleaned_up = True
        self.initialized = False
        self.started = False

        self.bot = None
        self.bot_info = []

    # @abstractmethod override
    def init(self):
        if self.initialized:
            logging.info('Already initialized')
            return

        logging.info('Initializing')

        try:
            self.bot = self.telegram.Bot(token=self.token)
            self.initialized = True
        except Exception as e:
            logging.error('Error initializing: "{}"'.format(e))
            self.initialized = False

        self.cleaned_up = False
        self.started = False

        return self.initialized

    # @abstractmethod override
    def is_finished(self):
        return True  # Not threaded

    # @abstractmethod override
    def start(self):
        if not self.initialized:
            logging.error('Not initialized')
            return False

        if self.started:
            logging.info('Already started')
            return True

        logging.info('Starting')

        try:
            self.bot_info = self.bot.get_me()
            logging.info('Bot info: {}'.format(self.bot_info))
            logging.info(
                'Sending messages to telegram chat[ID={}]'.format(self.chat_id))
            self.started = True
        except Exception as e:
            logging.error('Error starting: "{}"'.format(e))
            self.started = False

        return self.started

    # @abstractmethod override
    def stop(self):
        if not self.initialized:
            logging.error('Not initialized')
            return

        if not self.started:
            logging.info('Not started')
            return

        if self.cleaned_up:
            logging.info('Already cleaned up')
            return

        logging.info('Stopping')

        self.started = False
        self.initialized = False

        return not self.started

    # @abstractmethod override
    def cleanup(self):
        if self.initialized:
            logging.error('Initialized')
            return False

        if self.started:
            logging.error('Not stopped')
            return False

        if self.cleaned_up:
            logging.info('Already cleaned up')
            return True

        logging.info('Cleaning up')

        self.bot = None
        self.bot_info = []
        self.token = ''
        self.chat_id = ''

        self.cleaned_up = True

        return self.cleaned_up

    # @abstractmethod override
    def send_message(self, msg, subject=''):
        if not self.initialized:
            logging.error('Not initialized')
            return False

        if not self.started:
            logging.error('Not started')
            return False

        try:
            _msg = '{}{}'.format(self.settings.get_sender('telegram', 'prefix'), msg)
            logging.debug('Sending message {}@{}: "{}"'.format(
                self.bot_info['username'], self.chat_id, _msg))
            self.bot.send_message(chat_id=self.chat_id, text=_msg)
            return True
        except Exception as e:
            logging.error('Failed to send message: "{}"'.format(e))
            return False

    # @abstractmethod override
    def send_image(self, fullname, subfolder, name):
        """Sends an image

        :param fullname: The full name
        :param subfolder: The subfolder
        :param name: The name
        :return: True if sent, False else
        """
        if not self.initialized:
            logging.error('Not initialized')
            return

        if not self.started:
            logging.error('Not started')
            return

        try:
            logging.debug('Sending message {}@{}: "{}"'.format(
                self.bot_info['username'], self.chat_id, fullname))
            self.bot.send_photo(chat_id=self.chat_id,
                                photo=open(fullname, 'rb'))
            return True
        except Exception as e:
            logging.error('Failed to send image: "{}"'.format(e))
            return False

    # @abstractmethod override
    def send_video(self, fullname, subfolder, name):
        """Sends a video

        :param fullname: The full name
        :param subfolder: The subfolder
        :param name: The name
        :return: True if sent, False else
        """
        if not self.initialized:
            logging.error('Not initialized')
            return

        if not self.started:
            logging.error('Not started')
            return

        try:
            logging.debug('Sending message {}@{}: "{}"'.format(
                self.bot_info['username'], self.chat_id, fullname))
            self.bot.send_video(chat_id=self.chat_id,
                                video=open(fullname, 'rb'))
            return True
        except Exception as e:
            logging.error('Failed to send video: "{}"'.format(e))
            return False
