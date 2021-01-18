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
import threading
import smtplib

from sender.Bot import Bot


class MailBot(Bot):

    def __init__(self, settings):
        """Initialization

        :param settings: The settings
        """
        super().__init__(settings)

        logging.info('Initializing mail Bot')

        self.mail_server = self.settings.get_sender('mail', 'server')
        self.mail_server_port = self.settings.get_sender('mail', 'server_port')
        self.mail_address = self.settings.get_sender('mail', 'address')
        self.mail_password = self.settings.get_sender('mail', 'password')

        self.cleaned_up = True
        self.initialized = False
        self.started = False

        self.running_threads = 0

        self.bot = None

    # @abstractmethod override
    def init(self):
        if self.initialized:
            logging.info('Already initialized')
            return

        logging.info('Initializing')

        try:
            logging.info('Logging in to "{}:{}"'.format(self.mail_server, self.mail_server_port))
            self.bot = smtplib.SMTP_SSL(self.mail_server, self.mail_server_port)
            self.bot.ehlo()
            self.bot.login(self.mail_address, self.mail_password)
            self.initialized = True
        except Exception as e:
            logging.error('Failed to log in: "{}"'.format(e))
            self.initialized = False

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

        if self.bot:
            try:
                self.bot.quit()
            except:
                pass

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
        return self.running_threads <= 0

    def _cb_internal(self, success):
        """Internal callback"""
        self.running_threads = self.running_threads - 1

    # @abstractmethod override
    def send_message(self, msg, subject=''):
        """Sends a mail

        :param msg: The message
        :param subject: The subject
        """
        if not self.initialized:
            logging.error('Not initialized')
            return

        self.running_threads = self.running_threads + 1

        _subject = '{}{}'.format(self.settings.get_sender('mail', 'prefix'), subject)
        _msg = '{}{}'.format(self.settings.get_sender('mail', 'prefix'), msg)
        m_thread = MailSenderThread(mail_server=self.bot,
                                    mail_address=self.mail_address,
                                    str_from=self.mail_address,
                                    str_subject=_subject,
                                    str_to=self.mail_address,
                                    str_msg=_msg,
                                    callbacks = [self._cb_internal])

        m_thread.start()

    # @abstractmethod override
    def send_image(self, fullname, subfolder, name):
        return True

    # @abstractmethod override
    def send_video(self, fullname, subfolder, name):
        return True

class MailSenderThread(threading.Thread):
    def __init__(self, mail_server, mail_address, str_from, str_subject, str_to, str_msg, callbacks=[]):
        """Initializes the thread

        :param mail_server: The server
        :param mail_address: The email address
        :param str_from: From address
        :param str_subject: The Subject
        :param str_to: To address
        :param str_msg: The message
        :param callbacks: List of callbacks
        """
        threading.Thread.__init__(self)

        self.mail_server = mail_server
        self.mail_address = mail_address
        self.str_from = str_from
        self.str_subject = str_subject
        self.str_to = str_to
        self.str_msg = str_msg
        self.callbacks = callbacks

    def run(self):
        """Runs the thread"""
        logging.debug('Starting thread')

        success = False
        try:
            logging.info('Sending email to email address "{}"'.format(self.mail_address))

            _msg = 'From:{}\nSubject:{}\nTo:{}\n\n{}'.format(self.str_from, self.str_subject, self.str_to, self.str_msg)
            logging.debug('Sending message with subject "{}": "{}"'.format(self.str_subject, self.str_msg))
            self.mail_server.sendmail(self.mail_address, self.mail_address, _msg)
            success = True
        except Exception as exc:
            logging.error('Unable to send email: "{}"'.format(exc))
        finally:
            logging.info('Done sending email')
            for cb in self.callbacks:
                if cb:
                    cb(success)
