#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding: utf8
#
# Copyright 2019-2021 Denis Meyer
#
# This file is part of raspi-surveillance
#

"""A Mail bot"""

import logging

from sender.Bot import Bot


class LogBot(Bot):

    def __init__(self, settings):
        """Initialization

        :param settings: The settings
        """
        super().__init__(settings)

        logging.info('Initializing Log Bot')

        self.cleaned_up = True
        self.initialized = False
        self.started = False

        self.bot = None

    # @abstractmethod override
    def init(self):
        if self.initialized:
            logging.info('Already initialized')
            return

        logging.info('Initializing')

        self.initialized = True

        return self.initialized

    # @abstractmethod override
    def start(self):
        if not self.initialized:
            logging.error('Not initialized')
            return False

        if self.started:
            logging.info('Already started')
            return True

        logging.info('Starting')

        self.started = True

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
        if not self.initialized:
            logging.error('Not initialized')
            return

        logging.info('Cleaning up')

        self.cleaned_up = True

        return self.cleaned_up

    # @abstractmethod override
    def is_finished(self):
        return True # Not threaded

    # @abstractmethod override
    def send_message(self, msg, subject=''):
        if not self.initialized:
            logging.error('Not initialized')
            return

        logging.info('Message received:')
        logging.info('>>> Subject: {}'.format(subject))
        logging.info('>>> Message: {}'.format(msg))
        return True

    # @abstractmethod override
    def send_image(self, fullname, subfolder, name):
        if not self.initialized:
            logging.error('Not initialized')
            return

        logging.info('Image: "{}" (subfolder "{}", name "{}")'.format(fullname, subfolder, name))
        return True

    # @abstractmethod override
    def send_video(self, fullname, subfolder, name):
        if not self.initialized:
            logging.error('Not initialized')
            return

        logging.info('Video: "{}" (subfolder "{}", name "{}")'.format(fullname, subfolder, name))
        return True
