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
import argparse


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


def parse_args(__prog__, settings):
    """Parses the command line arguments
    
    :param __prog__: Program name
    :param settings: The settings
    :return: Parsed arguments
    """
    parser = argparse.ArgumentParser(prog=__prog__)

    parser.add_argument('--reswidth', required=False, type=int,
                        help='resolution width', default=settings.get('camera')['resolution_width'])
    parser.add_argument('--resheight', required=False, type=int,
                        help='resolution height', default=settings.get('camera')['resolution_height'])
    parser.add_argument('--rotation_degrees', required=False, type=int,
                        help='rotation_degrees', default=settings.get('camera')['rotation_degrees'])
    parser.add_argument('--image_nr_to_take', required=False, type=int,
                        help='Number of images to take', default=settings.get('image')['nr_to_take'])
    parser.add_argument('--video_active', required=False, type=bool,
                        help='Flag whether video is active', default=settings.get('video')['active'])
    parser.add_argument('--video_seconds', required=False,
                        help='Number of seconds to take as video', default=settings.get('video')['seconds'])

    parser.add_argument('--sender_l_active', required=False, type=bool,
                        help='Sender: Log - active', default=settings.get_sender('log', 'active'))
    parser.add_argument('--sender_l_send_messages', required=False, type=bool,
                        help='Sender: Log - send_messages', default=settings.get_sender('log', 'send_messages'))
    parser.add_argument('--sender_l_send_images', required=False, type=bool,
                        help='Sender: Log - send_images', default=settings.get_sender('log', 'send_images'))
    parser.add_argument('--sender_l_send_videos', required=False, type=bool,
                        help='Sender: Log - send_videos', default=settings.get_sender('log', 'send_videos'))
    parser.add_argument('--sender_l_prefix', required=False,
                        help='Sender: Log - prefix', default=settings.get_sender('log', 'prefix'))

    parser.add_argument('--sender_m_active', required=False, type=bool,
                        help='Sender: Mail - active', default=settings.get_sender('mail', 'active'))
    parser.add_argument('--sender_m_send_messages', required=False, type=bool,
                        help='Sender: Mail - send_messages', default=settings.get_sender('mail', 'send_messages'))
    parser.add_argument('--sender_m_send_videos', required=False, type=bool,
                        help='Sender: Mail - send_videos', default=settings.get_sender('mail', 'send_videos'))
    parser.add_argument('--sender_m_server', required=False,
                        help='Sender: Mail - server', default=settings.get_sender('mail', 'server'))
    parser.add_argument('--sender_m_server_port', required=False,
                        help='Sender: Mail - server_port', default=settings.get_sender('mail', 'server_port'))
    parser.add_argument('--sender_m_address', required=False,
                        help='Sender: Mail - address', default=settings.get_sender('mail', 'address'))
    parser.add_argument('--sender_m_password', required=False,
                        help='Sender: Mail - password', default=settings.get_sender('mail', 'password'))
    parser.add_argument('--sender_m_intv_msg_s', required=False,
                        help='Sender: Mail - interval_messages_send_sec', default=settings.get_sender('mail', 'interval_messages_send_sec'))
    parser.add_argument('--sender_m_prefix', required=False,
                        help='Sender: Mail - prefix', default=settings.get_sender('mail', 'prefix'))

    parser.add_argument('--sender_d_active', required=False, type=bool,
                        help='Sender: Dropbox - active', default=settings.get_sender('dropbox', 'active'))
    parser.add_argument('--sender_d_sync_images', required=False, type=bool,
                        help='Sender: Dropbox - sync_images', default=settings.get_sender('dropbox', 'sync_images'))
    parser.add_argument('--sender_d_sync_videos', required=False, type=bool,
                        help='Sender: Dropbox - sync_videos', default=settings.get_sender('dropbox', 'sync_videos'))
    parser.add_argument('--sender_d_access_token', required=False,
                        help='Sender: Dropbox - access_token', default=settings.get_sender('dropbox', 'access_token'))
    parser.add_argument('--sender_d_remote_folder_name', required=False,
                        help='Sender: Dropbox - remote_folder_name', default=settings.get_sender('dropbox', 'remote_folder_name'))

    parser.add_argument('--sender_t_active', required=False, type=bool,
                        help='Sender: Telegram - active', default=settings.get_sender('telegram', 'active'))
    parser.add_argument('--sender_t_send_messages', required=False, type=bool,
                        help='Sender: Telegram - send_messages', default=settings.get_sender('telegram', 'send_messages'))
    parser.add_argument('--sender_t_send_images', required=False, type=bool,
                        help='Sender: Telegram - send_images', default=settings.get_sender('telegram', 'send_images'))
    parser.add_argument('--sender_t_send_videos', required=False, type=bool,
                        help='Sender: Telegram - send_videos', default=settings.get_sender('telegram', 'send_videos'))
    parser.add_argument('--sender_t_token', required=False,
                        help='Sender: Telegram - token', default=settings.get_sender('telegram', 'token'))
    parser.add_argument('--sender_t_chat_id', required=False,
                        help='Sender: Telegram - chat_id', default=settings.get_sender('telegram', 'chat_id'))
    parser.add_argument('--sender_t_intv_msg_s', required=False,
                        help='Sender: Telegram - interval_messages_send_sec', default=settings.get_sender('telegram', 'interval_messages_send_sec'))
    parser.add_argument('--sender_t_prefix', required=False,
                        help='Sender: Telegram - prefix', default=settings.get_sender('telegram', 'prefix'))
    
    args = parser.parse_args()

    return args


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
