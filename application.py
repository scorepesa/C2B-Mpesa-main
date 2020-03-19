#!/usr/bin/env python
from flask import Flask
import logging
import logging.handlers

import os
import Request
import Result
from flask_restful import  Api

cur_dir = os.path.dirname(__file__)

filename = '/var/log/scorepesa-c2b/b2c2b.log'

#attributes
app = Flask(__name__)

api = Api(app)

api.add_resource(Request.C2BValidate, '/c2b/validate')
api.add_resource(Request.C2BRequest, '/c2b/confirm')
api.add_resource(Result.PaymentResult, '/b2c/result')
api.add_resource(Result.PaymentTimeout, '/b2c/timeout')
api.add_resource(Result.SMSResult, '/sms/dlr')
api.add_resource(Request.ReceiveSms,'/inbox/request')

log_formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(name)-5s %(filename)s:%(lineno)d:%(funcName)-10s %(message)s", datefmt="%m-%d-%y %H:%M:%S")

app.logger.setLevel(logging.DEBUG)

handler = logging.handlers.SysLogHandler(address = '/dev/log')
handler.setFormatter(log_formatter)
app.logger.addHandler(handler)


handler2 = logging.handlers.RotatingFileHandler(filename, 
    maxBytes=50*1024*1024, backupCount=5)
handler2.setFormatter(log_formatter)
app.logger.addHandler(handler2)


app.logger.debug('this is debug')
app.logger.critical('this is critical')

@app.before_first_request
def setup_logging():
    app.logger.info("Logging set up ready .. bla bla bla")

if __name__ == '__main__':
    app.run(port=4000, debug= True)
