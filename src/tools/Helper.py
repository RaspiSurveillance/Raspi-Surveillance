#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding: utf8
#
# Copyright 2019-2021 Denis Meyer
#
# This file is part of raspi-surveillance
#

"""Helper"""

import os
import sys
import logging


def initialize_logger(settings):
    """Initializes the logger

    :param settings: The settings
    """
    if settings.log_to_file:
        basedir = os.path.dirname(settings.log_filename)

        if not os.path.exists(basedir):
            os.makedirs(basedir)

    logger = logging.getLogger()
    logger.setLevel(settings.log_level)
    logger.propagate = False

    logger.handlers = []

    handler_console = logging.StreamHandler(sys.stdout)
    handler_console.setLevel(settings.log_level)
    handler_console.setFormatter(logging.Formatter(
        fmt=settings.log_format, datefmt=settings.log_dateformat))
    logger.addHandler(handler_console)

    if settings.log_to_file:
        handler_file = logging.FileHandler(
            settings.log_filename, mode='w', encoding=None, delay=False)
        handler_file.setLevel(settings.log_level)
        handler_file.setFormatter(logging.Formatter(
            fmt=settings.log_format, datefmt=settings.log_dateformat))
        logger.addHandler(handler_file)


def get_subclasses_of(klass):
    subclasses = set()
    work = [klass]
    classes = []
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                classes.append(child)
                work.append(child)

    return classes


def get_ascii_art_banner():
    return r"""
   -------------------------------------------------------------------------------------
  |  ____                 _      ____                       _ _ _                       |
  | |  _ \ __ _ ___ _ __ (_)    / ___| _   _ _ ____   _____(_) | | __ _ _ __   ___ ___  |
  | | |_) / _` / __| '_ \| |____\___ \| | | | '__\ \ / / _ \ | | |/ _` | '_ \ / __/ _ \ |
  | |  _ < (_| \__ \ |_) | |_____|__) | |_| | |   \ V /  __/ | | | (_| | | | | (_|  __/ |
  | |_| \_\__,_|___/ .__/|_|    |____/ \__,_|_|    \_/ \___|_|_|_|\__,_|_| |_|\___\___| |
  |                 |_| (C) 2019-2021 Denis Meyer                                       |
   -------------------------------------------------------------------------------------
"""
