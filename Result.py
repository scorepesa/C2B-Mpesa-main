import xmltodict
from C2B import C2B
from flask import request
from flask import Response
from Publisher import Publisher
import re
from flask_restful import reqparse
import json
"""
"""
class PaymentTimeout(C2B):
    methods = ['GET', 'POST']

    def __init(self):
        super(PaymentTimout, self).__init__()
     #[('conversation_id', u'AG_20180803_00007e0700519cc31bcc'), 
     #('ref_no', u'25790871363'), ('msisdn', u'254726986944'),
     #('status', u'COMPLETED')])
    def get_params(self):
        self.logger.info("GOT request GET %r" % (request.args)) 
        parser = reqparse.RequestParser()
        parser.add_argument('conversationId', type=str)
        parser.add_argument('refNo', type=str)
        parser.add_argument('msisdn', type=str)
        parser.add_argument('transactionId', type=str)
        parser.add_argument('status', type=str)
        args = parser.parse_args()
        return args
    #200=SUCCESS, 999=FAILED
    def response(self, reference, response_code, response_desc):
        data = {"status":response_code, "message":response_desc, "reference":reference}

	self.info("Returning response 000: %r " % data)
        return Response(        
            response=json.dumps(data),
            status=response_code,
            mimetype='application/json')

    def post(self):
        message = self.get_params()
        self.process_withdrawal_status(message)
        status = message.get('status')
	if status not in ['COMPLETED']:
            #reverse
            return self.response(message.get('reference'), status, 'OK FAILED')
        
        #update status OK
        return self.response(message.get('reference'),
            200, 'OK ACCEPTED')

    def get(self):
        message = self.get_params()
        self.process_withdrawal_status(message)
        status = message.get('status')
	if status not in ['COMPLETE']:
            #reverse
            return self.response(message.get('reference'), status, 'OK FAILED')
        
        #update status OK
        return self.response(message.get('reference'),
            200, 'OK ACCEPTED')

    def process_withdrawal_status(self, message):
        self.info("Publish .. creating publish instance, queue," \
		"exchange: (%s, %s) " % ('WITHDRAWAL_STATUS', 'WITHDRAWAL_STATUS'))
        message['exchange'] = 'WITHDRAWAL_STATUS'
        publisher = Publisher('WITHDRAWAL_STATUS', 'WITHDRAWAL_STATUS')

        self.logger.info("Publish calling publish status : %r" % message)
        publisher.publish(message, 'WITHDRAWAL_STATUS')

        self.info("POST: Withdraw status Queued successfully with message: %r " % message)


class PaymentResult(C2B):
    methods = ['GET', 'POST']

    def __init(self):
        super(PaymentResult, self).__init__()
    #{"Result":{"ResultType":0,"ResultCode":2001,"ResultDesc":"The initiator information is invalid.","OriginatorConversationID":"20252-9776791-1","ConversationID":"AG_20181117_000050c10b9d5af1acbc","TransactionID":"MKH8Y36IIE","ReferenceData":{"ReferenceItem":{"Key":"QueueTimeoutURL","Value":"http:\\/\\/internalapi.safaricom.co.ke\\/mpesa\\/b2cresults\\/v1\\/submit"}}}}

    def get_params(self):
        self.logger.info("GOT request PAYMENT PARAMS %r" % (request.data)) 
        #parser = reqparse.RequestParser()
        #parser.add_argument('Result', type=dict, location='json')
        
        #args = parser.parse_args()
        data = json.loads(request.data)
        args = data.get('Result')
        self.logger.info("GOT ARGS %r" % (args))
        det = {"ResultType": args.get('ResultType'),
               "ResultCode":args.get('ResultCode'),
               "ResultDesc":args.get('ResultDesc'),
               "OriginatorConversationID":args.get('OriginatorConversationID'),
               "ConversationID":args.get('ConversationID'),
               "TransactionID":args.get('TransactionID')}
        return det

    #200=SUCCESS, 999=FAILED
    def response(self, reference, response_code, response_desc):
        data = {"status":response_code, "message":response_desc, "reference":reference}

	self.info("Returning response 000: %r " % data)
        return Response(        
            response=json.dumps(data),
            status=response_code,
            mimetype='application/json')

    def post(self):
        message = self.get_params()
        self.process_withdrawal_status(message)
        status = message.get('status')
	if status not in ['COMPLETED']:
            #reverse
            return self.response(message.get('reference'), status, 'OK FAILED')
        
        #update status OK
        return self.response(message.get('reference'),
            200, 'OK ACCEPTED')

    def get(self):
        message = self.get_params()
        self.process_withdrawal_status(message)
        status = message.get('status')
	if status not in ['COMPLETE']:
            #reverse
            return self.response(message.get('reference'), status, 'OK FAILED')
        
        #update status OK
        return self.response(message.get('reference'),
            200, 'OK ACCEPTED')

    def process_withdrawal_status(self, message):
        self.info("Publish .. creating publish instance, queue," \
		"exchange: (%s, %s) " % ('WITHDRAWAL_STATUS', 'WITHDRAWAL_STATUS'))
        message['exchange'] = 'WITHDRAWAL_STATUS'
        publisher = Publisher('WITHDRAWAL_STATUS', 'WITHDRAWAL_STATUS')

        self.logger.info("Publish calling publish status : %r" % message)
        publisher.publish(message, 'WITHDRAWAL_STATUS')

        self.info("POST: Withdraw status Queued successfully with message: %r " % message)


class SMSResult(C2B):
    #ref_no=59826881125&msisdn=254726986944&status=DELIVERED
    #def get_params(self):
    #    parser = reqparse.RequestParser()
    #    parser.add_argument('id', type=str)
    #    parser.add_argument('status', type=str)
    #    parser.add_argument('phoneNumber', type=str)
    #    args = parser.parse_args()

    #    args.update({'ref_no':args.get('id')})
    #    args.update({'status':args.get('status')})
    #    args.update({'msisdn':args.get('phoneNumber')})
    #    return args

    def get_params(self):
        data = request.stream.read()
        self.info("RECEIVED XML REQUEST FOR DLR: %r" % data)
        try:
            xml_dict_data = xmltodict.parse(data)
        except Exception, e:
            self.error("FAILED TO PARSE XML ERROR: Attempt %s, Error: %r"
             % (attempt, e))
            self.error("FAILED TO PARSE XML REQUEST: %r" % data)
            xml_dict_data = None

        message_dict = {}
        if xml_dict_data:
            headers = xml_dict_data.get('soapenv:Envelope', {}).get('soapenv:Header')
            spid = headers.get('ns1:NotifySOAPHeader').get('ns1:spId')
            service_id = headers.get('ns1:NotifySOAPHeader').get('ns1:serviceId')
            trace_unique_id = headers.get('ns1:NotifySOAPHeader').get('ns1:traceUniqueID')
            body = xml_dict_data.get('soapenv:Envelope', {}).get('soapenv:Body')
            _dlr = body.get('ns2:notifySmsDeliveryReceipt')
            correlator = _dlr.get('ns2:correlator')
            msisdn =_dlr.get('ns2:deliveryStatus').get('address')
            dlr_status = _dlr.get('ns2:deliveryStatus').get('deliveryStatus')
            message_dict.update(
                {'pipe':spid,'sdp_id':service_id, 'trace_unique_id':trace_unique_id,
                'correlator':correlator, 'msisdn':msisdn, 'dlr_status':dlr_status}
            )
        return message_dict

    def get(self):
        message = self.get_params()
        print "MESSAGE", message
        self.process_message_status(message)
        #update status OK
        return self.response(message.get('ref_no'),
            200, 'OK ACCEPTED')

    def post(self):
        message = self.get_params()
        self.process_message_status(message)
        #update status OK
        return self.response(message.get('ref_no'),
            200, 'OK ACCEPTED')

    def response(self,ref, status, desc):
        xml = """
 <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:loc="http://www.csapi.org/schema/parlayx/data/sync/v1_0/local">
   <soapenv:Header/>
   <soapenv:Body>
      <loc:syncOrderRelationResponse>
         <loc:result>0</loc:result>
         <loc:resultDescription>OK</loc:resultDescription>
      </loc:syncOrderRelationResponse>
   </soapenv:Body>
</soapenv:Envelope>"""

        self.info("Returning DLR Response 000: %r " % xml)
        return Response(xml, mimetype='text/xml')
    
    def fomatted_date(self, date_obj):
        _format = "%Y-%m-%d %H:%M:%S"
        return date_obj.strftime(_format)

    #def response(self, reference, response_code, response_desc):
    #    data = {"status":response_code, "message":response_desc, "reference":reference}
    #    self.info("Returning response 000: %r " % data)
    #    return Response(
    #        response=json.dumps(data),
    #        status=response_code,
    #        mimetype='application/json')

    def process_message_status(self, message):
        self.info("Publish .. creating publish instance, queue," \
		"exchange: (%s, %s) " % ('DLR_QUEUE', 'DLR_QUEUE'))
        message['exchange'] = 'DLR_QUEUE'
        message['reference'] = message.get('ref_no')

        publisher = Publisher('DLR_QUEUE', 'DLR_QUEUE')

        self.logger.info("Publish calling publish status : %r" % message)
        publisher.publish(message, 'DLR_QUEUE')

        self.info("POST: DLR Queued successfully with message: %r " % message)


