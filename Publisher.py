from amqplib import client_0_8 as amqp
from utils import LocalConfigParser
#from dicttoxml import dicttoxml
import json
from flask import current_app


class Publisher(object):

    def __init__(self, queue_name, exchange_name):
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.configs = LocalConfigParser.parse_configs("RABBIT")
        self.logger = current_app.logger
        self.logger.error("COnfigs: %r" % self.configs)

    def publish(self, message, routing_key):


        self.logger.info("FOUND MESSAGE posting to Q: %r "
         % message)

        try:
            conn = amqp.Connection(host=self.configs['rabbithost'],
                userid=self.configs['rabbitusername'],
                password=self.configs['rabbitpassword'],
                virtual_host=self.configs['rabbitvhost'] or "/",
                insist=False)
        except Exception, e:
            self.logger.error("Error attempting to get Rabbit Connection: %r "
             % e)
            return;

        self.logger.info("Connection to rabbit established ...")
        try:
            self.logger.info("Attempting to queue message")
            ch = conn.channel()

            #ch.exchange_declare(exchange=self.exchange_name, type="fanout",
            #     durable=True, auto_delete=False)

            #ch.queue_declare(queue=self.queue_name, durable=True,
            #     exclusive=False, auto_delete=False)
            #ch.queue_bind(queue=self.queue_name, exchange=self.exchange_name,
            #     routing_key=routing_key)

            msg = amqp.Message(json.dumps(message))
            msg.properties["content_type"] = "text/plain"
            msg.properties["delivery_mode"] = 2

            ch.basic_publish(exchange=self.exchange_name,
                             routing_key=routing_key,
                             msg=msg)

            self.logger.info("Message queued success ... ")
        except Exception, e:
            self.logger.error("Error attempting to publish to Rabbit: %r " % e)
            conn.close()
        else:
            ch.close()
            conn.close()
