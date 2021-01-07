#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding: utf8
#
# Copyright 2019-2021 Denis Meyer
#
# This file is part of raspi-surveillance
#

"""A Dropbox Sender"""

import logging

from sender.Sender import Sender
from sender.dropbox.DropboxBot import DropboxBot


class DropboxSender(Sender):

    def __init__(self, settings):
        """Initialization"""
        super().__init__(settings)

        self.dropbox_bot = DropboxBot(self.settings)

    # @abstractmethod override
    def is_initialized(self):
        return super().is_initialized()

    # @abstractmethod override
    def is_started(self):
        return super().is_started()

    # @abstractmethod override
    def is_finished(self):
        return self.dropbox_bot.is_finished()

    # @abstractmethod override
    def get_name(self):
        return 'Dropbox'

    # @abstractmethod override
    def init(self):
        logging.debug('Initializing')
        self.initialized = self.dropbox_bot.init()
        return self.initialized

    # @abstractmethod override
    def start(self):
        logging.debug('Starting')
        self.started = self.dropbox_bot.start()
        return self.started

    # @abstractmethod override
    def stop(self):
        logging.debug('Stopping')
        self.started = self.dropbox_bot.stop()
        self.started = False

    # @abstractmethod override
    def cleanup(self):
        logging.debug('Cleaning up')
        self.dropbox_bot.cleanup()
        self.initialized = False

    # @abstractmethod override
    def can_send_msg(self):
        return False

    # @abstractmethod override
    def can_send_img(self):
        return self.settings.get_sender('dropbox', 'sync_images')

    # @abstractmethod override
    def can_send_video(self):
        return self.settings.get_sender('dropbox', 'sync_videos')

    # @abstractmethod override
    def send_msg(self, msg, subject='', force_send=False):
        if not self.can_send_msg():
            logging.debug(
                'This sender cannot send messages or is configured not to send messages')
            return True

        return False

    # @abstractmethod override
    def send_image(self, fullname, subfolder, name):
        if not self.can_send_img():
            logging.debug(
                'This sender cannot send images or is configured not to send images')
            return True

        if not self.is_initialized() or not self.is_started():
            logging.debug('Not sending image to dropbox')
            return False

        logging.debug('Sending image to dropbox')
        return self.dropbox_bot.send_image(fullname, subfolder, name)

    # @abstractmethod override
    def send_video(self, fullname, subfolder, name):
        if not self.can_send_video():
            logging.debug(
                'This sender cannot send videos or is configured not to send videos')
            return True

        if not self.is_initialized() or not self.is_started():
            logging.debug('Not sending video to dropbox')
            return False

        logging.debug('Sending video to dropbox')
        return self.dropbox_bot.send_video(fullname, subfolder, name)
