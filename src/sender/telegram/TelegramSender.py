#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding: utf8
#
# Copyright 2019-2021 Denis Meyer
#
# This file is part of raspi-surveillance
#

"""A Telegram Sender"""

import logging
import time

from sender.Sender import Sender
from sender.telegram.TelegramBot import TelegramBot


class TelegramSender(Sender):

    def __init__(self, settings):
        """Initialization"""
        super().__init__(settings)

        self.last_sent_time_msg = None

        self.telegram_bot = TelegramBot(self.settings)

    # @abstractmethod override
    def is_initialized(self):
        return super().is_initialized()

    # @abstractmethod override
    def is_started(self):
        return super().is_started()

    # @abstractmethod override
    def is_finished(self):
        return self.telegram_bot.is_finished()

    # @abstractmethod override
    def get_name(self):
        return 'Telegram'

    # @abstractmethod override
    def init(self):
        logging.debug('Initializing')
        self.initialized = self.telegram_bot.init()
        return self.initialized

    # @abstractmethod override
    def start(self):
        logging.debug('Starting')
        self.started = self.telegram_bot.start()
        return self.started

    # @abstractmethod override
    def stop(self):
        logging.debug('Stopping')
        self.telegram_bot.stop()
        self.started = False

    # @abstractmethod override
    def cleanup(self):
        logging.debug('Cleaning up')
        self.telegram_bot.cleanup()
        self.initialized = False

    # @abstractmethod override
    def can_send_msg(self):
        return self.settings.get_sender('telegram', 'send_messages')

    # @abstractmethod override
    def can_send_img(self):
        return self.settings.get_sender('telegram', 'send_images')

    # @abstractmethod override
    def can_send_video(self):
        return self.settings.get_sender('telegram', 'send_videos')

    # @abstractmethod override
    def send_msg(self, msg, subject='', force_send=False):
        if not self.can_send_msg():
            logging.debug(
                'This sender cannot send messages or is configured not to send messages')
            return True

        if not self.is_initialized() or not self.is_started():
            logging.debug('Not sending telegram message')
            return False

        if force_send or self._is_time_to_send():
            logging.debug('Sending telegram message')
            logging.debug('Telegram message "{}"'.format(msg))
            return self.telegram_bot.send_message(msg, subject)
        else:
            logging.debug(
                'Time interval since last message is too small, not sending telegram message')
            return False

    # @abstractmethod override
    def send_image(self, fullname, subfolder, name):
        if not self.can_send_img():
            logging.debug(
                'This sender cannot send images or is configured not to send images')
            return True

        if not self.is_initialized() or not self.is_started():
            logging.debug('Not sending telegram image')
            return False

        logging.debug('Sending telegram image')
        return self.telegram_bot.send_image(fullname, subfolder, name)

    # @abstractmethod override
    def send_video(self, fullname, subfolder, name):
        if not self.can_send_video():
            logging.debug(
                'This sender cannot send videos or is configured not to send videos')
            return True

        if not self.is_initialized() or not self.is_started():
            logging.debug('Not sending telegram video')
            return False

        logging.debug('Sending telegram video')
        return self.telegram_bot.send_video(fullname, subfolder, name)

    def _is_time_to_send(self):
        """Checks whether to send a telegram message

        :return: True if it is time to send, False else
        """
        if not self.can_send_msg():
            return False

        curr_time = time.time()

        if not self.last_sent_time_msg:
            self.last_sent_time_msg = curr_time
            return True

        if (curr_time - self.last_sent_time_msg) > self.settings.get_sender('telegram', 'interval_messages_send_sec'):
            self.last_sent_time_msg = curr_time
            return True

        return False
