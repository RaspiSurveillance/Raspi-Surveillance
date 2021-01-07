#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding: utf8
#
# Copyright 2019-2021 Denis Meyer
#
# This file is part of raspi-surveillance
#

"""A dropbox bot - encapsulates calls to the dropbox API"""

import logging
import os
import datetime
import time

from sender.Bot import Bot


class DropboxBot(Bot):

    def __init__(self, settings):
        """Initialization

        :param settings: The settings
        """
        super().__init__(settings)

        logging.info('Initializing Dropbox Bot')

        #import dropbox
        self.dropbox = __import__('dropbox', globals(), locals(), [], 0)

        self.cloud_folder = self.settings.get('dropbox', 'remote_folder_name')
        self.access_token = self.settings.get_sender('dropbox', 'access_token')

        self.cleaned_up = True
        self.initialized = False
        self.started = False

        self.bot = None

    # @abstractmethod override
    def init(self):
        """Manual initialization"""
        if self.initialized:
            logging.info('Already initialized')
            return

        logging.debug('Initializing')

        try:
            self.bot = self.dropbox.Dropbox(self.access_token)
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
        self.cloud_folder = ''
        self.access_token = ''

        self.cleaned_up = True

        return self.cleaned_up

    # @abstractmethod override
    def send_message(self, msg, subject=''):
        return True

    # @abstractmethod override
    def send_image(self, fullname, subfolder, name):
        if not self.initialized:
            logging.error('Not initialized')
            return False

        if not self.started:
            logging.error('Not started')
            return False

        path = '/{}/{}/{}'.format(self.cloud_folder,
                                  subfolder.replace(os.path.sep, '/'), name)
        while '//' in path:
            path = path.replace('//', '/')
        logging.info('Uploading to "{}"'.format(path))

        try:
            with open(fullname, 'rb') as f:
                data = f.read()
        except Exception as e:
            logging.error('Failed to open file "{}": "{}"'.format(fullname, e))
            return False

        try:
            overwrite = True
            mode = (
                self.dropbox.files.WriteMode.overwrite if overwrite else self.dropbox.files.WriteMode.add)
            mtime = os.path.getmtime(fullname)
            res = self.bot.files_upload(data,
                                        path,
                                        mode,
                                        client_modified=datetime.datetime(
                                            *time.gmtime(mtime)[:6]),
                                        mute=True)
            logging.debug('Uploaded as "{}"'.format(res.name.encode('utf8')))
            return True
        except self.dropbox.exceptions.ApiError as err:
            logging.error('API error: "{}"'.format(err))
            return False
        except Exception as e:
            logging.error(
                'Failed to upload file "{}": "{}"'.format(fullname, e))
            return False

    # @abstractmethod override
    def send_video(self, fullname, subfolder, name):
        self.send_image(fullname, subfolder, name)
