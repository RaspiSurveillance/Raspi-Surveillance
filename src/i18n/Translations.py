#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding: utf8
#
# Copyright 2019-2021 Denis Meyer
#
# This file is part of raspi-surveillance
#

import logging

"""The translation table"""

_translations = {
    'sender.started.subject': 'RaspiSurveillance started',
    'sender.started.message': 'RaspiSurveillance started',
    'sender.stopped.subject': 'RaspiSurveillance stopped',
    'sender.stopped.message': 'RaspiSurveillance stopped',
    'sensors.motion.detected_timestamp.subject': 'Raspi Surveillance - Alert',
    'sensors.motion.detected_timestamp.message': 'Motion detected on {:%Y-%m-%d %H:%M:%S}.'
}


def translate(key, default=''):
    """Returns the value for the given key or - if not found - a default value

    :param key: The key to be translated
    :param default: The default if no value could be found for the key
    """
    try:
        return _translations[key]
    except KeyError as exception:
        logging.error(
            'Returning default for key "{}": "{}"'.format(key, exception))
        return default
