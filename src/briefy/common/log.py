"""Briefy Common logging."""
from briefy.common.config import LOG_SERVER

import logging
import logstash


logger = logging.getLogger('briefy.common')

log_handler = None

if LOG_SERVER:
    log_handler = logstash.LogstashHandler(
        LOG_SERVER, 5543, version=1
    )
    logger.addHandler(log_handler)
