#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding: utf8
#
# Copyright 2019-2021 Denis Meyer
#
# This file is part of raspi-surveillance
#

"""Sender Register"""

import logging

from tools.Helper import get_subclasses_of
import sender.Sender


class SenderRegister:

    _SENDER_INFO = [
        {
            'fullpackage': 'sender.log',
            'package': 'log',
            'name': 'LogSender',
            'class': None
        },
        {
            'fullpackage': 'sender.mail',
            'package': 'mail',
            'name': 'MailSender',
            'class': None
        },
        {
            'fullpackage': 'sender.dropbox',
            'package': 'dropbox',
            'name': 'DropboxSender',
            'class': None
        },
        {
            'fullpackage': 'sender.telegram',
            'package': 'telegram',
            'name': 'TelegramSender',
            'class': None
        }
    ]

    def __init__(self):
        """Initialization"""
        logging.info('Initializing SenderRegister')

        logging.info('Searching for senders')

        for s_info in self._SENDER_INFO:
            __import__(s_info['fullpackage'], globals(), locals(), [s_info['name']], 0)

        # Make sure the given class is a subclass of Sender
        self.sender_classes = get_subclasses_of(sender.Sender.Sender)
        for s_class in self.sender_classes:
            for s_info in self._SENDER_INFO:
                if s_info['name'] == s_class.__name__:
                    s_info['class'] = s_class
        self.senders = [s for s in self._SENDER_INFO if s['class'] != None]

        logging.info('Found {} Senders'.format(len(self.senders)))
