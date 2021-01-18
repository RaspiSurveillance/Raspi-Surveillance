#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding: utf8
#
# Copyright 2019-2021 Denis Meyer
#
# This file is part of raspi-surveillance
#

"""Raspi Surveillance main class"""

import time
import datetime
import logging

from tools.GracefulKiller import GracefulKiller
from sender.SenderRegister import SenderRegister
from tools.FileSyncer import FileSyncer
from i18n.I18n import I18n
from tools.Helper import parse_args


class RaspiSurveillance:

    def __init__(self, __prog__, settings):
        """Initialization

        :param settings: The settings
        """
        logging.info('Initializing surveillance')

        self.settings = settings

        # Parse command line arguments
        self.args = parse_args(__prog__, self.settings)
        self._init_settings()

        self.i18n = I18n()

        self.running = False
        self.last_mail_sent_time = None
        self.last_telegram_msg_sent_time = None
        self.last_detection_time = None

        # Initialize GracefulKiller for the main loop
        logging.debug('Initializing GracefulKiller')
        self.g_killer = GracefulKiller()

        # Initialize sensors
        self._load_sensors()

        # Initialize Senders
        self._load_senders()

        logging.debug('Filtering active sensors')
        self.active_senders = self._init_and_start_senders()

        # Initialize FileSyncer
        logging.info('Initializing FileSyncer')
        self.file_syncer = FileSyncer(self.settings, self.active_senders)

        # Initialize internally
        self._init()

    def _init_settings(self):
        # Save given parameters
        self.settings.set('camera', 'resolution_width', self.args.reswidth)
        self.settings.set('camera', 'resolution_height', self.args.resheight)
        self.settings.set('camera', 'rotation_degrees', self.args.rotation_degrees)
        self.settings.set('image', 'nr_to_take', self.args.image_nr_to_take)
        self.settings.set('video', 'active', self.args.video_active)
        self.settings.set('video', 'seconds', self.args.video_seconds)

        self.settings.set_sender('log', 'active', self.args.sender_l_active)
        self.settings.set_sender('log', 'send_messages', self.args.sender_l_send_messages)
        self.settings.set_sender('log', 'send_images', self.args.sender_l_send_images)
        self.settings.set_sender('log', 'send_videos', self.args.sender_l_send_videos)
        self.settings.set_sender('log', 'prefix', self.args.sender_l_prefix)

        self.settings.set_sender('mail', 'active', self.args.sender_m_active)
        self.settings.set_sender('mail', 'send_messages', self.args.sender_m_send_messages)
        self.settings.set_sender('mail', 'send_videos', self.args.sender_m_send_videos)
        self.settings.set_sender('mail', 'server', self.args.sender_m_server)
        self.settings.set_sender('mail', 'server_port', self.args.sender_m_server_port)
        self.settings.set_sender('mail', 'address', self.args.sender_m_address)
        self.settings.set_sender('mail', 'password', self.args.sender_m_password)
        self.settings.set_sender('mail', 'interval_messages_send_sec', self.args.sender_m_intv_msg_s)
        self.settings.set_sender('mail', 'prefix', self.args.sender_m_prefix)

        self.settings.set_sender('dropbox', 'active', self.args.sender_d_active)
        self.settings.set_sender('dropbox', 'sync_images', self.args.sender_d_sync_images)
        self.settings.set_sender('dropbox', 'sync_videos', self.args.sender_d_sync_videos)
        self.settings.set_sender('dropbox', 'access_token', self.args.sender_d_access_token)
        self.settings.set_sender('dropbox', 'remote_folder_name', self.args.sender_d_remote_folder_name)

        self.settings.set_sender('telegram', 'active', self.args.sender_t_active)
        self.settings.set_sender('telegram', 'send_messages', self.args.sender_t_send_messages)
        self.settings.set_sender('telegram', 'send_images', self.args.sender_t_send_images)
        self.settings.set_sender('telegram', 'send_videos', self.args.sender_t_send_videos)
        self.settings.set_sender('telegram', 'token', self.args.sender_t_token)
        self.settings.set_sender('telegram', 'chat_id', self.args.sender_t_chat_id)
        self.settings.set_sender('telegram', 'interval_messages_send_sec', self.args.sender_t_intv_msg_s)
        self.settings.set_sender('telegram', 'prefix', self.args.sender_t_prefix)

    def _load_sensors(self):
        """Loads the sensors"""
        logging.info('Loading Sensors')
        if self.settings.get('use_sensors'):
            _sensors = __import__('tools.Sensors', globals(), locals(), ['Sensors'], 0)
            self.sensors = _sensors.Sensors(self.settings,
                                            cb_motion_detected=self._cb_motion_detected,
                                            cb_motion_ended=self._cb_motion_ended)

    def _load_senders(self):
        """Loads the Senders"""
        logging.info('Loading Senders')

        self.list_senders = []

        s_register = SenderRegister()
        for sender in s_register.senders:
            logging.debug(sender)
            if self.settings.get_sender(sender['package'], 'active'):
                logging.debug('Status: Active')
                self.list_senders.append(sender['class'](self.settings))
            else:
                logging.debug('Status: Inactive')

    def _init_and_start_senders(self):
        """Initializes and starts all senders. Returns a list of successfully initialized and started senders

        :return: list of successfully initialized and started senders
        """
        logging.debug('Initializing Senders')
        # Init Senders and filter for successfully initialized senders
        l = [sender for sender in self.list_senders if sender.init()]

        logging.debug('Starting Senders')
        # Start Senders and filter for successfully started senders
        l = [sender for sender in l if sender.start()]

        return l

    def _send_msg_to_senders(self, msg, subject='', force_send=False):
        """Sends a message to all senders

        :param msg: The message
        """
        logging.debug('Sending message to Senders')

        for sender in self.active_senders:
            if not sender.send_msg(msg, subject=subject, force_send=force_send):
                logging.info(
                    'Message not sent to Sender "{}"'.format(sender.get_name()))

    def _init(self):
        """Manual initialization"""
        logging.debug('Initializing')

        if self.settings.get('use_sensors'):
            logging.debug('Initializing sensors')
            self.sensors.init()
            logging.debug('Warming up sensors')
            self.sensors.warmup()
            logging.debug('Starting sensors')
            self.sensors.start()
        else:
            logging.info('No sensors')

        # List all active senders
        if self.active_senders:
            logging.info('Found {} active sender(s):'.format(
                len(self.active_senders)))
            for sender in self.active_senders:
                logging.info('\t- {}'.format(sender.get_name()))
        else:
            logging.info('No active Senders found')

        # Send start message
        logging.debug('Sending start message')
        self._send_msg_to_senders(
            self.i18n.get('sender.started.message'),
            subject=self.i18n.get('sender.started.subject'),
            force_send=True)

        if not self.file_syncer.init():
            logging.error('Failed to initialize FileSyncer')
        else:
            if self.settings.get('initial_folder_cleanup'):
                logging.info('Initially cleaning up local folder')
                # Cleanup folder on startup
                self.file_syncer.sync(cleanup=True)

    def _cleanup_wait_senders_finish(self):
        """Waits for all Senders to finish until a max amount of time"""
        logging.info('Waiting for Senders to finish its tasks')
        all_finished = False
        curr_time = time.time()
        max_wait_s = self.settings.get('max_wait')['finish_sender_tasks_sec']
        while not all_finished and not ((time.time() - curr_time) > max_wait_s):
            all_finished = True
            for sender in self.active_senders:
                if not sender.is_finished():
                    logging.info(
                        'Sender "{}" not yet finished'.format(sender.get_name()))
                    all_finished = False
                    time.sleep(self.settings.get('sleep')
                               ['sender_finished_sec'])
        if all_finished:
            logging.info('All Senders finished its tasks')
        else:
            logging.info(
                'Not all senders finished its tasks. Forcing to stop.')

    def _cleanup_wait_filesyncer_finish(self):
        """Waits for FilySyncer to finish until a max amount of time"""
        logging.info('Waiting for FileSyncer to finish its tasks')
        curr_time = time.time()
        max_wait_s = self.settings.get(
            'max_wait')['finish_filesyncer_tasks_sec']
        while self.file_syncer.syncing and not ((time.time() - curr_time) > max_wait_s):
            logging.info('FileSyncer not yet finished')
            time.sleep(self.settings.get('sleep')['file_sync_finished_sec'])
        if not self.file_syncer.syncing:
            logging.info('FileSyncer finished its tasks')
        else:
            logging.info(
                'FileSyncer did not finish its tasks. Forcing to stop.')

    def _cleanup(self):
        """Cleans up all initialized resources"""
        logging.info('Cleaning up')

        # Send stop message
        logging.debug('Sending stop message')
        self._send_msg_to_senders(
            self.i18n.get('sender.stopped.message'),
            subject=self.i18n.get('sender.stopped.subject'),
            force_send=True)

        self.file_syncer.cleanup()

        if self.settings.get('use_sensors') and self.sensors:
            self.sensors.cleanup()

        # Wait for Senders to finish
        self._cleanup_wait_senders_finish()

        # Wait for FileSyncer to finish
        self._cleanup_wait_filesyncer_finish()

        # Cleanup
        for sender in self.active_senders:
            sender.stop()
            sender.cleanup()

        self.running = False

        logging.info('Done cleaning up')

    def run(self):
        """Starts the surveillance loop"""
        if self.running:
            logging.info('Already started')
            return

        if not self.running:
            self.running = True

        use_sensors = self.settings.get('use_sensors')
        senders_active = len(self.active_senders) > 0
        filesyncer_active = self.file_syncer.initialized
        if not use_sensors and not senders_active and not filesyncer_active:
            logging.warn(
                'Not starting surveillance loop: No sensors, no Senders, no FileSyncer')
            return

        logging.info('Starting surveillance loop')

        try:
            while not self.g_killer.kill_now:
                try:
                    if self._check_sensors():
                        self.sensors.tick()
                    time.sleep(self.settings.get('sleep')['main_loop_sec'])
                except:
                    self.g_killer.kill_now = True
                    logging.info('Stopping surveillance loop')
        finally:
            self._cleanup()
            logging.info('Stopping')

    def _on_images_captured(self):
        """Callback on images captured"""
        logging.debug('Image capturing done')

        self.file_syncer.sync()

    def _cb_motion_detected(self):
        """Callback on motion detected"""
        logging.info('Motion detected')

        logging.info('Not reading sensor data for about {} seconds'.format(
            self.settings.get('sleep')['check_sensors_sec']))

        self.last_detection_time = time.time()
        # Take some images
        if self.settings.get('use_sensors'):
            self.sensors.capture_camera_image(cb=self._on_images_captured)

        # Send a notification message
        logging.debug('Sending motion detected message')
        msg = self.i18n.get('sensors.motion.detected_timestamp.message').format(datetime.datetime.now())
        self._send_msg_to_senders(msg, subject=self.i18n.get('sensors.motion.detected_timestamp.subject'))

    def _cb_motion_ended(self):
        """Callback on motion ended"""
        logging.debug('Motion ended')

    def _check_sensors(self):
        """Checks whether to check the sensors

        :return: True if it is time to send, False else
        """
        if not self.settings.get('use_sensors'):
            return False

        curr_time = time.time()

        if not self.last_detection_time:
            return True

        if (curr_time - self.last_detection_time) > self.settings.get('sleep')['check_sensors_sec']:
            return True

        return False
