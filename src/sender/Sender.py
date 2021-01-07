#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding: utf8
#
# Copyright 2019-2021 Denis Meyer
#
# This file is part of raspi-surveillance
#

"""An abstract sender"""

from abc import ABC, abstractmethod

class Sender(ABC):
    """Senders need to be registered BY HAND in SenderRegister::_SENDER_INFO"""

    def __init__(self, settings):
        """Initialization"""
        super().__init__()

        self.settings = settings
        self.initialized = False
        self.started = False

    @abstractmethod
    def is_initialized(self):
        """Returns a boolean flag whether this Sender is initialized

        :return: Boolean flag whether this Sender is initialized
        """
        return self.initialized

    @abstractmethod
    def is_started(self):
        """Returns a boolean flag whether this Sender is started

        :return: Boolean flag whether this Sender is started
        """
        return self.started

    @abstractmethod
    def is_finished(self):
        """Returns a boolean flag whether this Sender is finished doing its tasks

        :return: Boolean flag whether this Sender is finished doing its tasks
        """
        return True

    @abstractmethod
    def get_name(self):
        """Returns the name of the Sender

        :return: The name of the Sender
        """
        return 'Sender'

    @abstractmethod
    def init(self):
        """Returns a boolean flag whether this Sender is initialized

        :return: Boolean flag whether this Sender is initialized
        """
        return False

    @abstractmethod
    def start(self):
        """Starts the Sender"""
        self.started = True

    @abstractmethod
    def stop(self):
        """Stops the Sender"""
        self.started = False

    @abstractmethod
    def cleanup(self):
        """Cleans up the Sender, usually on end (destructor)"""
        self.initialized = False

    @abstractmethod
    def can_send_msg(self):
        """Returns whether this Sender can send a message

        :return: Boolean flag whether this Sender can send a message
        """
        return False

    @abstractmethod
    def can_send_img(self):
        """Returns whether this Sender can send an image

        :return: Boolean flag whether this Sender can send an image
        """
        return False

    @abstractmethod
    def can_send_video(self):
        """Returns whether this Sender can send a video

        :return: Boolean flag whether this Sender can send a video
        """
        return False

    @abstractmethod
    def send_msg(self, msg, subject='', force_send=False):
        """Sends a message

        :param msg: The message
        :param subject: The subject
        :param force_send: Boolean flag whether message should be forced to send
        :return: Boolean flag whether message was sent
        """
        return False

    @abstractmethod
    def send_image(self, fullname, subfolder, name):
        """Sends an image

        :param fullname: The full name
        :param subfolder: The subfolder
        :param name: The name
        :return: Boolean flag whether message was sent
        """
        return False

    @abstractmethod
    def send_video(self, fullname, subfolder, name):
        """Sends a video

        :param fullname: The full name
        :param subfolder: The subfolder
        :param name: The name
        :return: Boolean flag whether message was sent
        """
        return False
