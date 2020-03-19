from flask import current_app

#from flask.views import MethodView

from flask_restful import Resource

class C2B(Resource):

    methods = ['GET', 'POST']
    QUEUE_NAME = 'C2B_QUEUE'
    EXCHANGE_NAME = 'C2B_QUEUE'
    ROUTING_KEY = 'C2B_QUEUE'
    SMS_QUEUE_NAME= 'INBOX_QUEUE'
    SMS_EXCHANGE_NAME='INBOX_QUEUE'
    SMS_ROUTING_KEY='INBOX_QUEUE'


    def __init__(self):
        self.logger = current_app.logger
        super(C2B, self).__init__()

    def formatted_date(self, date_obj):
        _format = "%Y-%m-%d %H:%M:%S"
        return date_obj.strftime(_format)

    def info(self, text):
        self.logger.info(text)

    def debug(self, text):
        self.logger.debug(text)

    def fatal(self, text):
        self.logger.fatal(text)

    def error(self, text):
        self.logger.error(text)


