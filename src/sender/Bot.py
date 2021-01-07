#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding: utf8
#
# Copyright 2019-2021 Denis Meyer
#
# This file is part of raspi-surveillance
#

"""An abstract bot"""

from abc import ABC, abstractmethod

class Bot(ABC):

    def __init__(self, settings):
        """Initialization"""
        super().__init__()

        self.settings = settings

    @abstractmethod
    def init(self):
        """Initializes the Bot

        :return: Boolean flag whether this Bot has been initialized
        """
        return False

    @abstractmethod
    def is_finished(self):
        """Returns a boolean flag whether this Bot is finished doing its tasks

        :return: Boolean flag whether this Bot is finished doing its tasks
        """
        return True

    @abstractmethod
    def start(self):
        """Starts the Bot

        :return: Boolean flag whether this Bot has been started
        """
        return False

    @abstractmethod
    def stop(self):
        """Stops the Bot

        :return: Boolean flag whether this Bot has been stopped
        """
        return True

    @abstractmethod
    def cleanup(self):
        """Cleans up the Bot

        :return: Boolean flag whether this Bot has been cleaned up
        """
        return False

    @abstractmethod
    def send_message(self, msg):
        """Sends a message

        :param msg: The message
        :return: True if successfully sent, False else
        """
        return False

    @abstractmethod
    def send_image(self, fullname, subfolder, name):
        """Sends an image

        :param fullname: The full name
        :param subfolder: The subfolder
        :param name: The name
        :return: True if successfully sent, False else
        """
        return False

    @abstractmethod
    def send_video(self, fullname, subfolder, name):
        """Sends a video

        :param fullname: The full name
        :param subfolder: The subfolder
        :param name: The name
        :return: True if successfully sent, False else
        """
        return False
