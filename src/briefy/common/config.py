"""Briefy Common config."""
from prettyconf import config

ENV = config('ENV', default='staging')

# NewRelic
NEW_RELIC_ENVIRONMENT = ENV

_region = 'us-east-1' if NEW_RELIC_ENVIRONMENT == 'staging' else 'eu-central-1'
_queue_suffix = 'stg' if NEW_RELIC_ENVIRONMENT == 'staging' else 'live'

# AWS Credentials
AWS_ACCESS_KEY = config('AWS_ACCESS_KEY', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')


# SQS Integration
SQS_REGION = config('SQS_REGION', default=_region)

# Queues
EVENT_QUEUE = config('EVENT_QUEUE', default='event-{}'.format(_queue_suffix))

# Thumbor
THUMBOR_PREFIX_SOURCE = config('THUMBOR_PREFIX_SOURCE', default='source/')
THUMBOR_PREFIX_RESULT = config('THUMBOR_PREFIX_SOURCE', default='result/')
THUMBOR_KEY = config(
    'THUMBOR_KEY',
    default='dMXlEkjuSz3VoIn9THJOROfMPZa4FqSvDl3jXwN9'
)
THUMBOR_BASE_URL = config(
    'THUMBOR_BASE_URL',
    default='https://images.stg.briefy.co'
)
THUMBOR_INTERNAL_URL = config(
    'THUMBOR_INTERNAL_URL',
    default='http://briefy-thumbor.briefy-thumbor.svc.cluster.local'
)

# Log Server
LOG_SERVER = config('LOG_SERVER', default='')
