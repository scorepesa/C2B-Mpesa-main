import xmltodict
from flask import request
from flask import current_app
from flask import Response
from Kannel import Gateway
import re
from flask.views import MethodView
from DlrStatus import DlrStatus

"""
SAMPLE DLR XML
<?xml version="1.0" encoding="utf-8" ?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><soapenv:Header><ns1:NotifySOAPHeader xmlns:ns1="http://www.huawei.com.cn/schema/common/v2_1"><ns1:spId>601779</ns1:spId><ns1:serviceId>6017792000163394</ns1:serviceId><ns1:traceUniqueID>504021504491810242319268489003</ns1:traceUniqueID></ns1:NotifySOAPHeader></soapenv:Header><soapenv:Body><ns2:notifySmsDeliveryReceipt xmlns:ns2="http://www.csapi.org/schema/parlayx/sms/notification/v2_2/local"><ns2:correlator>5101254726498973</ns2:correlator><ns2:deliveryStatus><address>254726986944</address><deliveryStatus>Insufficient_Balance</deliveryStatus></ns2:deliveryStatus></ns2:notifySmsDeliveryReceipt></soapenv:Body></soapenv:Envelope>
"""
class Dlr(MethodView):
    methods = ['POST', 'GET']

    def __init__(self):
        self.logger = current_app.logger
        super(Dlr, self).__init__()

    def response(self):
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
    
    def post(self):
        message = self.get_message_dict()
        _dlr = DlrStatus(self.logger)
        _dlr.update_dlr(message)        
        return self.response()
    
    """
    OrderedDict([(u'soapenv:Envelope', OrderedDict([(u'@xmlns:soapenv', u'http://schemas.xmlsoap.org/soap/envelope/'), (u'@xmlns:xsi', u'http://www.w3.org/2001/XMLSchema-instance'), (u'soapenv:Header', OrderedDict([(u'ns1:NotifySOAPHeader', OrderedDict([(u'@xmlns:ns1', u'http://www.huawei.com.cn/schema/common/v2_1'), (u'ns1:spId', u'601779'), (u'ns1:serviceId', u'6017792000163394'), (u'ns1:traceUniqueID', u'504021504491810242319268489003')]))])), (u'soapenv:Body', OrderedDict([(u'ns2:notifySmsDeliveryReceipt', OrderedDict([(u'@xmlns:ns2', u'http://www.csapi.org/schema/parlayx/sms/notification/v2_2/local'), (u'ns2:correlator', u'5101254726498973'), (u'ns2:deliveryStatus', OrderedDict([(u'address', u'254726986944'), (u'deliveryStatus', u'Insufficient_Balance')]))]))]))]))])
    """
    def get_message_dict(self):
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

    def fomatted_date(self, date_obj):
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


"""
Sample xml mo
<?xml version="1.0" encoding="utf-8" ?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><soapenv:Body>
<ns1:syncOrderRelation xmlns:ns1=
"http://www.csapi.org/schema/parlayx/data/sync/v1_0/local"><ns1:userID>
<ID>254710542888</ID><type>0</type></ns1:userID><ns1:spID>601527</ns1:spID>
<ns1:productID>MDSP2000246236</ns1:productID>
<ns1:serviceID>6015272000113131</ns1:serviceID>
<ns1:serviceList>6015272000113131</ns1:serviceList>
<ns1:updateType>1</ns1:updateType>
<ns1:updateTime>20151125090837</ns1:updateTime>
<ns1:updateDesc>Addition</ns1:updateDesc>
<ns1:effectiveTime>20151125090837</ns1:effectiveTime>
<ns1:expiryTime>20361231210000</ns1:expiryTime><ns1:extensionInfo><item>
<key>accessCode</key><value>20750</value></item><item><key>chargeMode</key>
<value>18</value></item><item><key>MDSPSUBEXPMODE</key><value>1</value></item>
<item><key>objectType</key><value>1</value></item><item><key>isAutoExtend</key>
<value>0</value></item><item><key>shortCode</key><value>20750</value></item>
<item><key>isFreePeriod</key><value>false</value></item><item>
<key>payType</key><value>1</value></item><item><key>transactionID</key>
<value>404090102571511250908172197008</value></item><item><key>orderKey</key>
<value>999000000163761827</value></item><item><key>isSubscribeCnfmFlow</key>
<value>true</value></item><item><key>status</key><value>0</value></item><item>
<key>validTime</key><value>20361231210000</value></item><item>
<key>keyword</key><value>job</value></item><item><key>cycleEndTime</key>
<value>20151125210000</value></item><item><key>durationOfGracePeriod</key>
<value>-1</value></item><item><key>serviceAvailability</key><value>0</value>
</item><item><key>channelID</key><value>143</value></item><item>
<key>TraceUniqueID</key><value>404090102571511250908172197009</value></item>
<item><key>operCode</key><value></value></item><item><key>rentSuccess</key>
<value>true</value></item><item><key>try</key><value>false</value></item>
</ns1:extensionInfo></ns1:syncOrderRelation></soapenv:Body></soapenv:Envelope>
"""


class SoapMTRequest(MethodView):
    methods = ['GET', 'POST']

    def response(self):
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

        self.info("Returning MT response 000: %r " % xml)
        return Response(xml, mimetype='text/xml')

    def post(self):
        message = self.get_message_dict()
        message.update({'mt': 1, 'mo':0, 'text':message.get('keyword'),
        'from':message.get('msisdn'),  'correlator':message.get('transaction_id')})
        self.logger.info("Ready to invoke Gateway for message Receive ==> %r" % message)
        gateway = Gateway()

        self.logger.info("Calling GATWAY.RECEIVESMS .... ")
        status = gateway.receive_sms(message)

        self.info("POST: Task Queued successfully with message: %r " % status)
        return self.response()

    def get(self):
        message = self.get_message_dict()
        message.update(
            {'mt': 1, 'text':message.get('keyword'), 'mo':0,
            'from':message.get('msisdn'), 'correlator':message.get('transaction_id')})

        self.logger.info("Ready to invoke Gateway for message Receive ==> %r" % message)
        gateway = Gateway()

        self.logger.info("Calling GATWAY.RECEIVESMS .... ")
        status = gateway.receive_sms(message)

        self.info("POST: Task Queued successfully with message: %r " % status)
        return self.response()


    def get_message_dict(self, attempt=1):
        data = request.stream.read()
        self.info("RECEIVED XML REQUEST FOR MT: %r" % request)
        try:
            xml_dict_data = xmltodict.parse(data)
        except Exception, e:
            self.error("FAILED TO PARSE XML ERROR: Attempt %s, Error: %r"
             % (attempt, e))
            self.error("FAILED TO PARSE XML REQUEST: %r" % data)
            xml_dict_data = None

        message_dict = {}
        if xml_dict_data:
            sync_order_relation = xml_dict_data.get('soapenv:Envelope', {}).\
            get('soapenv:Body', {})\
            .get('ns1:syncOrderRelation', {})

            extension_info = sync_order_relation.get('ns1:extensionInfo', {}).\
            get('item', {})

            msisdn = sync_order_relation.get('ns1:userID', {}).get('ID', None)
            sp_id = sync_order_relation.get('ns1:spID', None)
            product_id = sync_order_relation.get('ns1:productID', None)
            service_id = sync_order_relation.get('ns1:serviceID', None)
            service_list = sync_order_relation.get('ns1:serviceList', None)
            update_type = sync_order_relation.get('ns1:updateType', None)
            time = sync_order_relation.get('ns1:updateTime', None)

            update_desc = sync_order_relation.get('ns1:updateDesc', None)
            effective_time = sync_order_relation.get('ns1:effectiveTime', None)
            expiry_time = sync_order_relation.get('ns1:expiryTime', None)

            extra_extension_info = self.get_extension_info(extension_info)

            message_dict.update(extra_extension_info)

            message_dict.update({
                "msisdn": msisdn,
                "sp_id": sp_id,
                "product_id": product_id,
                "service_id": service_id,
                "sdp_id": service_id,
                "service_list": service_list,
                "update_type": update_type,
                "expiry_time": expiry_time,
                "update_desc": update_desc,
                "effective_time": effective_time,
                "time": time,
            })

        return message_dict

    """
    Will get this key, value pair for the extract below
    accessCode 20750
    chargeMode 18
    MDSPSUBEXPMODE 1
    objectType 1
    isAutoExtend 0
    shortCode 20750
    isFreePeriod false
    payType 1
    transactionID 404090102571511250908172197008
    orderKey 999000000163761827
    isSubscribeCnfmFlow true
    status 0
    validTime 20361231210000
    keyword job
    cycleEndTime 20151125210000
    durationOfGracePeriod -1
    serviceAvailability 0
    channelID 143
    TraceUniqueID 404090102571511250908172197009
    operCode None
    rentSuccess true
    try false

    Yes, in snake case e.g TraceUniqueID >> trace_unique_id
    """
    def get_extension_info(self, extension_info):
        extras = {}
        for ord_dict in extension_info:
            extras.update({self.convert_to_snake_case(ord_dict.
            get('key')): ord_dict.get('value')})

        return extras

    def convert_to_snake_case(self, value):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def __init__(self):
        self.logger = current_app.logger
        super(SoapMTRequest, self).__init__()

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


"""
sample xml
<?xml version="1.0" encoding="utf-8" ?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><soapenv:Header>
 <ns1:NotifySOAPHeader xmlns:ns1="http://www.huawei.com.cn/schema/common/v2_1">
 <ns1:spRevId>Roamtech</ns1:spRevId><ns1:spRevpassword>Abcd1234
 </ns1:spRevpassword><ns1:spId>601384</ns1:spId>
 <ns1:serviceId>6013842000111545</ns1:serviceId>
 <ns1:linkid>27104549076002030223</ns1:linkid>
 <ns1:traceUniqueID>404090102571511270745496685004</ns1:traceUniqueID>
 </ns1:NotifySOAPHeader></soapenv:Header><soapenv:Body>
 <ns2:notifySmsReception xmlns:ns2=
 "http://www.csapi.org/schema/parlayx/sms/notification/v2_2/local">
 <ns2:correlator>123456</ns2:correlator><ns2:message><message>1</message>
 <senderAddress>tel:707889899</senderAddress>
 <smsServiceActivationNumber>tel:20032</smsServiceActivationNumber>
 <dateTime>2015-11-27T07:45:49Z</dateTime></ns2:message>
 </ns2:notifySmsReception></soapenv:Body></soapenv:Envelope>
"""


class SoapMORequest(MethodView):
    methods = ['GET', 'POST']

    def post(self):
        message = self.get_message_dict()
        message.update({'mo': 1})
        self.logger.info("Ready to invoke Gateway for message Receive ==> %r" % message)
        gateway = Gateway()

        self.logger.info("Calling GATWAY.RECEIVESMS .... ")
        status = gateway.receive_sms(message)

        self.info("POST: Task Queued successfully with message: %r " % status)
        return self.response()

    def get(self):
        message = self.get_message_dict()
        message.update({'mo': 1})
        self.logger.info("Ready to invoke Gateway for message Receive ==> %r" % message)
        gateway = Gateway()

        self.logger.info("Calling GATWAY.RECEIVESMS .... ")
        status = gateway.receive_sms(message)

        self.info("POST: Task Queued successfully with message: %r " % status)
        return self.response()

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

    def __init__(self):
        self.logger = current_app.logger
        super(SoapMORequest, self).__init__()

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

