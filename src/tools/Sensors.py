#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding: utf8
#
# Copyright 2019-2021 Denis Meyer
#
# This file is part of raspi-surveillance
#

"""Reads an interprets sensor data"""

import time
import datetime
from os import system
import os
import logging
import threading
from subprocess import call

system('sudo killall pigpiod')
SLEEP_KILL_S = 4
logging.info('Initializing pigpiod for {}s...'.format(SLEEP_KILL_S))
time.sleep(SLEEP_KILL_S)
system('sudo pigpiod')

import RPi.GPIO as GPIO
import pigpio
from picamera import PiCamera


class Sensors:
    """Initialize as follows:

    0. Constructor
    1. Call init
    2. Call warmup
    3. Call start
    4. Call loop, sleep, repeat 4.
    """

    LOW = 0
    HIGH = 1

    def __init__(self, settings, cb_motion_detected=None, cb_motion_ended=None):
        """Initialization

        :param settings: The settings
        :param cb_motion_detected: On motion detected
        :param cb_motion_ended: On motion ended
        """
        self.settings = settings
        self.cb_motion_detected = cb_motion_detected
        self.cb_motion_ended = cb_motion_ended

        self.time_sleep_init_s = self.settings.get('sleep')['sensors_init_sec']
        self.time_sleep_warmup_s = self.settings.get('sleep')['sensors_warmup_sec']
        self.pin_pir = self.settings.get('pins')['sensor_pir']

        self.initialized = False
        self.warmed_up = False
        self.started = False
        self.cleaned_up = False
        self.looping = False
        self.capturing_image = False

        self.pir_state = self.LOW
        self.curr_val = self.LOW

    def init(self):
        """Manual initialization because of the sleep"""
        if self.initialized:
            logging.info('Already initialized')
            return

        logging.info('Initializing')

        self.pi = pigpio.pi()
        if not self.pi.connected:
            logging.error('GPIO (pigpio) not connected')
            return

        self.cleaned_up = False
        self.initialized = True

    def warmup(self):
        """Warms up the sensors"""
        if not self.initialized:
            logging.error('Not initialized')
            return

        if self.warmed_up:
            logging.info('Already warmed up')
            return

        logging.info('Warming up for {}s...'.format(
            self.time_sleep_warmup_s))
        time.sleep(self.time_sleep_warmup_s)
        self.warmed_up = True

    def start(self):
        """Starts the system"""
        if not self.initialized:
            logging.error('Not initialized')
            return

        if not self.warmed_up:
            logging.error('Not warmed up')
            return

        if self.started:
            logging.info('Already started')
            return

        logging.info('Starting')
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_pir, GPIO.IN)
        self.started = True

    def cleanup(self):
        """Cleans up the system"""
        if self.cleaned_up:
            logging.info('Already cleaned up')
            return

        logging.info('Cleaning up')
        GPIO.cleanup()
        self.pi.stop()
        system('sudo killall pigpiod')
        self.cleaned_up = True
        self.warmed_up = False
        self.started = False
        self.initialized = False

    def tick(self):
        """Tick (single loop), reads sensor data"""
        if not self.initialized:
            logging.error('Not initialized')
            return

        if not self.started:
            logging.error('Not started')
            return

        if not self.warmed_up:
            logging.error('Not warmed up')
            return

        if self.looping:
            logging.info('Already looping')
            return

        self.looping = True
        try:
            self.curr_val = self.pi.read(self.pin_pir)
            if self.curr_val == self.HIGH:
                if self.pir_state == self.LOW:
                    self.pir_state = self.HIGH
                    if self.cb_motion_detected:
                        self.cb_motion_detected()
            else:
                if self.pir_state == self.HIGH:
                    self.pir_state = self.LOW
                    if self.cb_motion_ended:
                        self.cb_motion_ended()
        finally:
            self.looping = False

    def _cb_img_captured(self):
        self.capturing_image = False

    def capture_camera_image(self, cb):
        """Captures a camera image

        :param cb: Callback
        """
        if self.capturing_image:
            logging.debug('Image capturing from camera already in progress')
            return

        logging.debug('Capturing image from camera')
        self.capturing_image = True

        curr_datetime = '{:%Y-%m-%d-%H-%M-%S}'.format(datetime.datetime.now())
        folder_name = '{}/rs-{}'.format(self.settings.get('local_sync_folder_name'), curr_datetime)
        c_thread = CameraCaptureThread(id=1,
                                       name='CameraCaptureThread-{}'.format(
                                           curr_datetime),
                                       nr_imgs=self.settings.get('image')['nr_to_take'],
                                       res_width=self.settings.get('camera')['resolution_width'],
                                       res_height=self.settings.get('camera')['resolution_height'],
                                       deg_rot=self.settings.get('camera')['rotation_degrees'],
                                       folder_name=folder_name,
                                       video_active=self.settings.get('video')['active'],
                                       video_s=self.settings.get('video')['seconds'],
                                       time_sleep_warmup_s=self.settings.get('sleep')['camera_warmup_sec'],
                                       time_sleep_betweenimages_s=self.settings.get('sleep')['between_images_sec'],
                                       cb_img_captured=cb,
                                       cb_img_captured_internal=self._cb_img_captured)
        c_thread.start()


class CameraCaptureThread(threading.Thread):

    def __init__(self,
                    id,
                    name,
                    nr_imgs,
                    res_width,
                    res_height,
                    deg_rot,
                    folder_name,
                    video_active=False,
                    video_s=3,
                    time_sleep_warmup_s=2,
                    time_sleep_betweenimages_s=0.5,
                    cb_img_captured=None,
                    cb_img_captured_internal=None):
        """Initializes the thread

        :param id: The ID
        :param name: The name
        :param nr_imgs: Number of images
        :param res_width: Resolution width
        :param res_height: Resolution height
        :param deg_rot: Rotation (in degree)
        :param folder_name: The folder name
        :param video_active: Whether to take a video
        :param video_s: Video length in seconds
        :param time_sleep_warmup_s: The warmup sleep (in s)
        :param time_sleep_betweenimages_s: Sleep time between taking images (in s)
        :param cb_img_captured: Callback on image captured
        :param cb_img_captured_internal: Callback on image captured (internal)
        """
        threading.Thread.__init__(self)

        self.id = id
        self.name = name
        self.nr_imgs = nr_imgs
        self.res_width = res_width
        self.res_height = res_height
        self.deg_rot = deg_rot
        self.folder_name = folder_name
        self.video_active = video_active
        self.video_s = video_s
        self.time_sleep_warmup_s = time_sleep_warmup_s
        self.time_sleep_betweenimages_s = time_sleep_betweenimages_s
        self.cb_img_captured = cb_img_captured
        self.cb_img_captured_internal = cb_img_captured_internal

    def _asserting_folder(self, fname):
        """Creates the folder to capture the images into

        :param fname: The folder name
        """
        logging.debug('Asserting folder "{}"'.format(fname))

        if not os.path.exists(fname):
            os.makedirs(fname)

    def run(self):
        """Runs the thread"""
        logging.debug('Starting thread [id="{}", name="{}"]'.format(
            self.id, self.name))
        try:
            with PiCamera() as camera:
                logging.debug('Camera image data [res_width={}, res_height={}, deg_rot={}]'.format(
                    self.res_width, self.res_height, self.deg_rot))
                camera.resolution = (self.res_width, self.res_height)
                camera.rotation = self.deg_rot
                camera.start_preview()
                logging.debug('Warming up camera for {}s'.format(self.time_sleep_warmup_s))
                time.sleep(self.time_sleep_warmup_s)
                self._asserting_folder(self.folder_name)
                logging.debug('Taking {} images'.format(self.nr_imgs))
                take_two_img_parts = self.video_active and (self.nr_imgs >= 2)
                images_taken = 0
                # First half of the images
                for _ in range(0, int(self.nr_imgs / 2) if take_two_img_parts else self.nr_imgs):
                    images_taken = images_taken + 1
                    iname = '{}/rs-{}.jpg'.format(self.folder_name, images_taken)
                    logging.debug('Capturing image #{}: "{}"'.format(images_taken, iname))
                    camera.capture(iname)
                    time.sleep(self.time_sleep_betweenimages_s)
                if self.video_active:
                    # Take video
                    iname = '{}/rs-video.h264'.format(self.folder_name)
                    try:
                        logging.debug('Capturing video: "{}"'.format(iname))
                        camera.start_recording(iname)
                        camera.wait_recording(self.video_s)
                        camera.stop_recording()
                        oname = '{}/rs-video.mp4'.format(self.folder_name)
                        retcode = call(["MP4Box", "-add", iname, oname])
                        if retcode != 0:
                            logging.error('Failed to convert video "{}" to "{}"'.format(oname))
                    except Exception as e:
                        logging.error('Failed to capture video "{}"'.format(iname))
                    if take_two_img_parts:
                        # Second half of the images
                        for _ in range(0, self.nr_imgs  - images_taken):
                            images_taken = images_taken + 1
                            iname = '{}/rs-{}.jpg'.format(self.folder_name, images_taken)
                            logging.debug('Capturing image #{}: "{}"'.format(images_taken, iname))
                            camera.capture(iname)
                            time.sleep(self.time_sleep_betweenimages_s)
                camera.stop_preview()
        finally:
            logging.debug(
                'Done capturing images in folder "{}"'.format(self.folder_name))
            if self.cb_img_captured_internal:
                self.cb_img_captured_internal()
            if self.cb_img_captured:
                self.cb_img_captured()
