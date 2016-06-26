"""Briefy Common config."""
from os import environ as env

# NewRelic
NEW_RELIC_ENVIRONMENT = env.get('NEW_RELIC_ENVIRONMENT', 'staging')

_region = 'us-east-1' if NEW_RELIC_ENVIRONMENT == 'staging' else 'eu-west-1'
_queue_suffix = 'stg' if NEW_RELIC_ENVIRONMENT == 'staging' else 'live'

# AWS Credentials
AWS_ACCESS_KEY = env.get('AWS_ACCESS_KEY', '')
AWS_SECRET_ACCESS_KEY = env.get('AWS_SECRET_ACCESS_KEY', '')


# SQS Integration
SQS_REGION = env.get('SQS_REGION', _region)

# Queues
EVENT_QUEUE = env.get('EVENT_QUEUE', 'event-{}'.format(_queue_suffix))
