import logging
import sys


class LoggerConfig(object):

    LOGCONFIG = {
   'version': 1,
   'disable_existing_loggers': False,
   'formatters': {
       'verbose': {
           'format': '%(levelname)s %(module)s P%(process)d \
           T%(thread)d %(message)s'
           },
       },
   'handlers': {
       'stdout': {
           'class': 'logging.StreamHandler',
           'stream': sys.stdout,
           'formatter': 'verbose',
           },
       'file_logger': {
           'class': 'logging.handlers.RotatingFileHandler',
           'filename': '/var/log/bonyezampenzi/py_generic_message_producer.log',
           'formatter': 'verbose',
           },
       'sys-logger6': {
           'class': 'logging.handlers.SysLogHandler',
           'address': '/dev/log',
           'facility': "local6",
           'formatter': 'verbose',
           },
       },
   'loggers': {
       'my-logger': {
           'handlers': ['sys-logger6', 'file_logger', 'stdout'],
           'level': logging.INFO,
           'propagate': True,
           },
       }
   }
