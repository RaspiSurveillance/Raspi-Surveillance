#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding: utf8
#
# Copyright 2019-2021 Denis Meyer
#
# This file is part of raspi-surveillance
#

__prog__ = 'RaspiSurveillance'
__version__ = '1.0'

"""Main"""

import logging

from tools.Helper import initialize_logger, get_ascii_art_banner
from tools.Settings import Settings
from tools.RaspiSurveillance import RaspiSurveillance


if __name__ == "__main__":
    settings = Settings()
    initialize_logger(settings)

    logging.info(get_ascii_art_banner())

    raspi_surveillance = RaspiSurveillance(settings)
    raspi_surveillance.run()
