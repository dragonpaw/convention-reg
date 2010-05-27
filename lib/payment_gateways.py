import logging
import urllib, urllib2

class PaymentDeclinedError(RuntimeError):
    pass

def quantum_gateway(login, key, amount, zip=None, name=None, address=None, email=None, ip=None, invoice=None, number=None, month=None, year=None, cvv=None, transparent=True, trans_type=None):
    log = logging.getLogger('lib.payment_gateways.quantum_gateway')

    # Can't use a dict, as the API is oddly sensitive to ordering. (WTF?!)
    values = [
        ('gwlogin', login),
        ('RestrictKey', key),
        ('trans_method', 'cc'),
        ('amount', str(amount)),
        ('Dsep', 'Pipe'),
    ]

    if name:
        values.append(('BNAME', name))

    if address:
        values.append(('BADDR1', address))

    if zip:
        values.append(('BZIP1', zip))

    if email:
        values.append(('BCUST_EMAIL', email))

    #('override_email_customer', 'N'),
    #('override_trans_customer', 'N'),

    if ip:
        values.append(('customer_ip', ip))

    if trans_type:
        values.append(('trans_type', trans_type))

    if invoice:
        values.append(('invoice_num', invoice))

    if transparent:
        url = 'https://secure.quantumgateway.com/cgi/tqgwdbe.php'
        values.append(('ccnum', number))
        values.append(('ccmo', "%02d" % int(month)))
        values.append(('ccyr', year % 100))
        if cvv:
            values.append(('CVV2', cvv))
            values.append(('CVVtype', 1)) # Is being passed.
    else:
        url = 'https://secure.quantumgateway.com/cgi/qgwdbe.php'
        raise NotImplementedError('Quantum Gateway Interactive not yet supported.')

    encoded = urllib.urlencode(values)
    req = urllib2.Request(url, encoded)
    response = urllib2.urlopen(req)
    reply = response.read()
    #logging.debug(encoded)
    logging.info(reply)

    #Response Sequence: Transaction Status, Auth Code, Transaction ID, AVS Response, CVV2 Response, Maxmind Score, Decline Reason, Decline Error Number
    #"APPROVED","019452","652145","Y","M","0.6"
    #"DECLINED","019452","652145","N","N","0.6","INVALID EXP DATE","205"
    APPROVED, AUTHCODE, TRANSACTION_ID, AVS, CVV2, MAXMIND, DECLINE_REASON, DECLINE_CODE = range(0,8)
    reply = [x.strip('"') for x in reply.split('|')]

    if reply[APPROVED] != 'APPROVED':
        if reply[DECLINE_CODE]:
            error_message = "%s (%s)" % (reply[DECLINE_REASON], reply[DECLINE_CODE])
        else:
            error_message = reply[DECLINE_REASON]
        raise PaymentDeclinedError(error_message)
    else:
        return reply[AUTHCODE], reply[TRANSACTION_ID]


if __name__ == '__main__':
    from django.conf import settings

    logging.basicConfig(level=logging.DEBUG)
    quantum_gateway(
        login = settings.LOCAL_SETTINGS.get('quantum_gateway','login'),
        key = settings.LOCAL_SETTINGS.get('quantum_gateway','key'),
        email='test@example.com',
        amount="19.95",
        name='Test Transaction',
        address='1234 Anytown PL',
        zip=66666,
        ip='127.0.0.1',
        number='4111111111111111',
        month=12,
        year=2010,
        cvv=111
    )

# Quantum Gateway Test Cards --------------------------------------------------
#Visa 4111111111111111 Expiration Date 12 of 2010
#MasterCard 5454545454545454 Expiration Date 12 of 2010

# CVV Responses ---------------------------------------------------------------
#CVV2 Entry 	Description 	Response Codes
#111 	Match 	M
#222 	No Match 	N
#333 	Not Processed 	P
#444 	Should have been present 	S
#555 	Issuer unable to process request 	U

# AVS Response ----------------------------------------------------------------
#Description 	                Zip
#Address and zip match 	        66666
#Address matches, Zip does not 	11111
#Neither address or zip match 	33333
#Zip matches, address does not 	77777

# Forced Decline --------------------------------------------------------------
#Decline Amounts Using Test Cards
#Amount 	Error#  Response
#.01    	200 	Authorization Declined
#.02    	201 	Call Voice Oper
#.03    	202 	Hold - Call
#.04    	203 	Call Voice Oper
#.05    	204 	Invalid Card No
#.06    	205 	Invalid Exp Date
#.07    	206 	Invalid ICA No
#.08    	207 	Invalid ABA No
#.09    	208 	Invalid PIN No
#.10    	209 	Invalid Bank MID
#.11    	210 	Invalid Term No
#.12    	211 	Invalid Amount
#.13    	212 	Invalid State CD
#.14    	213 	Invalid Tran FMT
#.15    	214 	Call Voice Oper
#.16    	215 	Lost/Stolen Card
#.17    	216 	Invalid Pin
#.18    	217 	Over Credit Flr
#.19    	218 	*Request Denied*
#.20    	220 	Not Online to ??
#.21    	200 	AUTH DECLINED
#.22    	200 	AUTH DECLINED
#.23    	200 	AUTH DECLINED
#.24    	200 	AUTH DECLINED
#.25    	200 	AUTH DECLINED
#.92    	200 	AUTH DECLINED
#.93    	200 	AUTH DECLINED
#.94    	200 	AUTH DECLINED
#.98    	298 	Error - Retry
#.99    	299 	Error Error - Retry
#1.69    	A Y 	Will always return a match for AVS
#19.58   	Not viewable 	Not Viewable
