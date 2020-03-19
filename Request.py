import xmltodict
from C2B import C2B
from flask import request
from flask import Response
from Publisher import Publisher
import re
from flask_restful import reqparse

class C2BValidate(C2B):
    methods = ['GET', 'POST']
    def __init(self):
        super(SoapMTRequest, self).__init__()

    def post(self):
        return {'ResultCode':0, 'ResultDesc':'Success'}, 201

    def get(self):
        return self.post()

class C2BRequest(C2B):
    methods = ['GET', 'POST']

    def __init(self):
        super(SoapMTRequest, self).__init__()

    #201=SUCCESS, 400=Invalid params, 500=FAILED
    def response(self, payment_id, response_code, response_desc):
        json ={"payment_id":payment_id, "response_code":response_code, "response_desc":response_desc}
        self.info("Returning response 000: %r " % json)
        return {'ResultCode':0, 'ResultDesc':'Success'}, 201

    def get_queue_message(self, message):
        queue_message = {
            "trans_time": message.get("TransTime"),
            "short_code": message.get("BusinessShortCode"),
            "first_name": message.get("FirstName", ""),
            "last_name": message.get("LastName", ""),
            "middle_name": message.get("MiddleName", ""),
            "network": message.get("SAFARICOM"),
            "trans_id": message.get("TransID"),
            "msisdn": message.get("MSISDN"),
            "amount": message.get("TransAmount"),
            "bill_ref_number": message.get("BillRefNumber"),
	    "exchange":self.EXCHANGE_NAME
            }
        if message.get('ResultCode'):
           queue_message['ResultCode'] = message.get("ResultCode")
        return queue_message

    def get_params(self):
        parser = reqparse.RequestParser()
        parser.add_argument('TransID', type=str, location='json')
        parser.add_argument('TransTime', type=str, location='json')
        parser.add_argument('BillRefNumber', type=str, location='json')
        parser.add_argument('FirstName', type=str, location='json')
        parser.add_argument('MiddleName', type=str, location='json')
        parser.add_argument('LastName', type=str, location='json')
        parser.add_argument('BusinessShortCode', type=str, location='json')
        parser.add_argument('TransAmount', type=str, location='json')
        parser.add_argument('MSISDN', type=str, location='json')
        args = parser.parse_args() 
        return args
 
    def post(self):
        message = self.get_message_dict()
        if not message or not message.get('TransID'):
            return {'response_code':400, 'response_desc':'Missing transaction ID'}, 400
        message['exchange'] = self.EXCHANGE_NAME
        publisher = Publisher(self.QUEUE_NAME, self.EXCHANGE_NAME)

        self.logger.info("Publish calling publish : %r => Q = %s, EX=%s" % (message, self.QUEUE_NAME, self.EXCHANGE_NAME))
	
	q_message =self.get_queue_message(message)
        publisher.publish(q_message, self.ROUTING_KEY)

        self.info("POST: Task Queued successfully with message: %r " % message)
        return self.response(message.get('TransID'),
            201, 'Succcess')

    def get(self):
        message = self.get_message_dict()
        self.logger.info("Publish .. creating publish instance, queue," \
            "exchange: (%s, %s) " % (self.QUEUE_NAME, self.EXCHANGE_NAME))
        publisher = Publisher(self.QUEUE_NAME, self.EXCHANGE_NAME)

        self.logger.info("Publish calling publish : %r" % message)
	q_message =self.get_queue_message(message)
        publisher.publish(q_message, self.ROUTING_KEY)

        self.info("GET: Task Queued successfully with message: %r " % message)
        return self.response(message.get('TransID'), 
		201, 'Transaction queued succcess'), 200

    def get_message_dict(self, attempt=1):
        data = self.get_params()
        self.info("RAW DATA %r " % request.data )
        if not data:
            self.info("NO data received ..")
            return {} 
        self.info("RECEIVED JSON REQUEST: %r" % data)

        return data
#######################SMS Receiver

class ReceiveSms(C2B):
    methods = ['GET', 'POST']

    def __init(self):
        super(SoapMTRequest, self).__init__()

    #201=SUCCESS, 400=Invalid params, 500=FAILED
    #def response(self, message,statusCode):
    #    self.info("Returning response 000: %r " % message)
    #    return {'response_code':statusCode, 'response_Desc':'Created'}

    def response(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:loc="http://www.csapi.org/schema/parlayx/sms/notification/v2_2/local">
   <soapenv:Header />
   <soapenv:Body>
      <loc:notifySmsReceptionResponse />
   </soapenv:Body>
</soapenv:Envelope>"""
        self.info("Returning MO response 000: %r " % xml)
        return Response(xml, mimetype='text/xml')


    def get_message_dict(self):
	data = request.stream.read()
	self.info("RECEIVED XML REQUEST: %r" % data)
	try:
	    xml_dict_data = xmltodict.parse(data)
	except Exception, e:
	    self.error("FAILED TO PARSE XML ERROR: %r" % e)
	    self.error("FAILED TO PARSE XML REQUEST: %r" % data)
	    xml_dict_data = None

	self.info("XML_DATA  %r" % xml_dict_data)

	message_dict = {}
	if xml_dict_data:
	    self.info("Reading XML DICT")
	    soap_envelope = xml_dict_data.get('soapenv:Envelope', {})
	    soap_header = soap_envelope.get('soapenv:Header', {}).\
	    get('ns1:NotifySOAPHeader', {})
	    sp_rev_id = soap_header.get("ns1:spRevId")
	    sp_rev_password = soap_header.get("ns1:spRevpassword")
	    sp_id = soap_header.get('ns1:spId', None)
	    service_id = soap_header.get('ns1:serviceId', None)
	    link_id = soap_header.get('ns1:linkid', None)
	    trace_unique_id = soap_header.get('ns1:traceUniqueID', None)

	    soap_body = soap_envelope.get("soapenv:Body", {}).\
	    get('ns2:notifySmsReception', {})

	    correlator = soap_body.get('ns2:correlator')
	    soap_message_dict = soap_body.get('ns2:message', {})
	    message = soap_message_dict.get('message')
	    msisdn = soap_message_dict.get('senderAddress', '').\
	    replace('tel:', '')
	    shortcode = soap_message_dict.get('smsServiceActivationNumber',
		 '').replace('tel:', '')
	    time = soap_message_dict.get('dateTime', '')

	    message_dict.update({
		"msisdn": msisdn,
		"sp_id": sp_id,
		"time": time,
		"short_code": shortcode,
		"message": message,
		"trace_unique_id": trace_unique_id,
		"link_id": link_id,
		"correlator": correlator,
		"service_id": service_id,
		"sdp_id": service_id,
		"sp_rev_id": sp_rev_id,
		"sp_rev_password": sp_rev_password

	    })

	    self.info("Processed message from xml : %r" % message_dict)

	return message_dict


    def fomatted_date(self, date_obj):
        _format = "%Y-%m-%d %H:%M:%S"
        return date_obj.strftime(_format)

    def get_extension_info(self, extension_info):
        extras = {}
        for ord_dict in extension_info:
            extras.update({self.convert_to_snake_case(ord_dict.
            get('key')): ord_dict.get('value')})

        return extras

    def convert_to_snake_case(self, value):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def get_params(self):
        parser = reqparse.RequestParser()
        parser.add_argument('msisdn', type=str)
        parser.add_argument('shortcode', type=str)
        parser.add_argument('message', type=str)
        parser.add_argument('timestamp', type=str)
        parser.add_argument('sLinkID', type=str)
        args = parser.parse_args() 
        args.update({'link_id':args.get('sLinkID')})
      
        return args
 
    def post(self):
        message = self.get_message_dict()
        self.info("Received inbox post request ==> %r" %(message,))
        if not message or not message.get('short_code'):
            return {'response_code':400, 'response_desc':'Missing MSISDN on POST'}, 400
        message['exchange'] = self.SMS_EXCHANGE_NAME
        publisher = Publisher(self.SMS_QUEUE_NAME, self.SMS_EXCHANGE_NAME)

        self.logger.info("Publish calling publish : %r" % message)
        publisher.publish(message, self.SMS_ROUTING_KEY)

        self.info("POST: Task Queued successfully with message: %r " % message)
        return self.response()

    def get(self):
        message = self.get_message_dict()
        self.logger.info("Publish .. creating publish instance, queue," \
            "exchange: (%s, %s) " % (self.SMS_QUEUE_NAME, self.SMS_EXCHANGE_NAME))
        
        message['exchange'] = self.SMS_EXCHANGE_NAME
        publisher = Publisher(self.SMS_QUEUE_NAME, self.SMS_EXCHANGE_NAME)

        self.logger.info("Publish calling publish : %r" % message)
        publisher.publish(message, self.SMS_ROUTING_KEY)

        self.info("GET: Task Queued successfully with message: %r " % message)
        return self.response()

