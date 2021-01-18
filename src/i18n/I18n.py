#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding: utf8
#
# Copyright 2019-2021 Denis Meyer
#
# This file is part of raspi-surveillance
#

"""I18n - The i18n handling"""


import logging
import time
import json
import os


class I18n:

    _FILE_JSON_TRANSLATIONS = 'translations.json'

    def __init__(self, filename=_FILE_JSON_TRANSLATIONS):
        """Initializes the class
        
        :param filename: The translations file name
        """
        logging.info('Initializing')

        self.filename = filename

        self._translations_dict = {}

        ### Init ###

        self._read_translations()
        logging.debug(self._translations_dict)

    def _read_translations(self):
        """Reads the translations from file"""
        logging.debug('Reading translations from file')

        try:
            with open(self.filename, 'r') as jf:
                self._translations_dict = json.load(jf)
        except Exception as e:
            logging.error('Could not load from file "{}": "{}"'.format(self.filename, e))

    def get(self, key, default=''):
        """Returns the value for the given key or - if not found - a default value

        :param key: The key
        :param default: The default if no value could be found for the key
        """
        try:
            return self._translations_dict[key]
        except KeyError as exception:
            logging.error('Returning default for key "{}": "{}"'.format(key, exception))
            return default
