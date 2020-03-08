#!/usr/bin/env python

import os
import logging.config
from yaml import full_load

def setup_logging(name=None):
    """Setup logging configuration"""
    path = 'log_config.yml'
    default_level = logging.DEBUG

    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = full_load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    return logging.getLogger(name)
