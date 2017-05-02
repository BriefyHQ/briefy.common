"""Briefy Common config."""
from prettyconf import casts
from prettyconf import config


ENV = config('ENV', default='staging')
MOCK_SQS = config('MOCK_SQS', default=False)

# used to disable on update in the timestamp mixin
IMPORT_KNACK = config('IMPORT_KNACK', casts.Boolean(), default=False)

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
EVENT_QUEUE = config('EVENT_QUEUE', default='event-{0}'.format(_queue_suffix))

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

# Cache config
CACHE_HOST = config('CACHE_HOST', default='localhost')
CACHE_PORT = config('CACHE_PORT', default='11212')
CACHE_BACKEND = config('CACHE_BACKEND', default='dogpile.cache.pylibmc')
CACHE_EXPIRATION_TIME = config('CACHE_EXPIRATION_TIME', default=3600)
CACHE_ASYNC_REFRESH = config('CACHE_ASYNC_REFRESH', casts.Boolean(), default=False)
