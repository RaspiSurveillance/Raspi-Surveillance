#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding: utf8
#
# Copyright 2019-2021 Denis Meyer
#
# This file is part of raspi-surveillance
#

"""A graceful killer"""

import logging
import signal


class GracefulKiller:

    def __init__(self):
        """Initializes the graceful killer state"""
        self.kill_now = False
        signal.signal(signal.SIGINT, self._exit_gracefully)
        signal.signal(signal.SIGTERM, self._exit_gracefully)

    def _exit_gracefully(self, signum, frame):
        """Sets the graceful killer state to exit

        :param signum The exit signal
        :param frame: The frame
        """
        logging.info('Received exit signal {}'.format(signum))
        self.kill_now = True
