#encoding=UTF-8

import json
import httplib
from time import strftime, gmtime
import hmac
import hashlib
import base64

PUNTOPAGOS_CODES = {
    'ok': '00',
    'no_ok': '99',
    }

PUNTOPAGOS_URLS = {
    'sandbox': 'sandbox.puntopagos.com',
    'production': 'www.puntopagos.com',
    }

PUNTOPAGOS_ACTIONS = {
    'create': '/transaccion/crear',
    'process': '/transaccion/procesar/%(token)s',
    'status': '/transaccion/%(token)s',
    }

PUNTOPAGOS_SIGNABLE_HEADERS = {
    'create': 'transaccion/crear\n' \
              '%(trx_id)s\n' \
              '%(monto)0.2f\n' \
              '%(fecha)s',
    'status': 'transaccion/traer\n' \
              '%(token)s\n' \
              '%(trx_id)s\n' \
              '%(monto)0.2f\n' \
              '%(fecha)s',
}

PUNTOPAGOS_PAYMENT_METHODS = {
    1: u"Botón de Pago Banco Santander",
    2: u"Tarjeta Presto",
    3: u"Webpay Transbank",
    4: u"Botón de Pago Banco de Chile",
    5: u"Botón de Pago BCI",
    6: u"Botón de Pago TBanc",
    7: u"Botón de Pago Banco Estado",
    #10:  "Tarjeta Ripley",
    15: u"Paypal",
    #999: u"Banco de Prueba"
    }


def get_image(medio_pago):
    assert medio_pago in PUNTOPAGOS_PAYMENT_METHODS
    return "http://www.puntopagos.com/content/mp%d.gif" % mp


def sign(string, key):
    return base64.b64encode(hmac.HMAC(key, string, hashlib.sha1).digest())


class PuntoPagoJsonResponseError(Exception):
    pass


class PuntoPagoResponse():
    complete = False
    data = {}

    def __init__(self, response, sandbox=False):
        self.sandbox = sandbox
        self.complete = response.status is httplib.OK
        if self.complete:
            try:
                content = response.read()
                print content
                self.data = json.loads(content)
            except ValueError:
                raise PuntoPagoJsonResponseError
            else:
                self._process_data()
        else:
            print response.read()

    def _process_data(self):
        '''
        Override this method for processing `dict` self.data
        previously set on constructor. By default does nothing.
        '''
        pass


class PuntoPagoCreateResponse(PuntoPagoResponse):
    success = False
    trx_id = None
    amount = None
    token = None

    def _process_data(self):
        self.trx_id = self.data['trx_id']
        self.amount = self.data['monto']
        self.token = self.data['token']
        self.method = self.data['medio_pago'] if 'medio_pago' in self.data else None
        action = PUNTOPAGOS_ACTIONS['process'] % {'token': self.token}
        params = {
            'url': PUNTOPAGOS_URLS['sandbox' if self.sandbox else 'production'],
            'action': action
        }
        self.redirection_url = "http://%(url)s%(action)s" % params
        self.success = self.data['respuesta'] == u'00'


class PuntoPagoStatusResponse(PuntoPagoResponse):
    pass


class PuntoPagoRequest:
    def __init__(self, config, sandbox=False, ssl=True):
        url = PUNTOPAGOS_URLS['sandbox' if sandbox else 'production']
        if ssl:
            self.connection = httplib.HTTPSConnection(url)
        else:
            self.connection = httplib.HTTPConnection(url)
        self.connection.set_debuglevel(3 if sandbox else 0)

        self.config = config
        self.sandbox = sandbox

    def status(self, token, trx_id, monto):
        '''
        Create a request for verify a transaction status

        :param token:       Unique token, asigned by puntopagos to transaction.
        :param trx_id:      Client unique transaction id (varchar(50)).
        :param monto:       Transaction total amount.
        '''

        now = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
        data = {
            'token': token,
            'trx_id': trx_id,
            'monto': monto,
            'fecha': now
        }

        authorization_string = PUNTOPAGOS_SIGNABLE_HEADERS['status'] % data
        headers = self.create_headers(authorization_string, now)
        status_action = PUNTOPAGOS_ACTIONS['status'] % {'token': token}

        self.connection.request(method='GET', url=status_action, headers=headers)
        response = self.connection.getresponse()

        return PuntoPagoStatusResponse(response, sandbox=self.sandbox)

    def create(self, trx_id, medio_pago, monto, detalle=''):
        '''
        Create a request (and a transaction) to puntopagos.com.

        :param trx_id:      Client unique transaction id (varchar(50)).
        :param medio_pago:  Payment method id, valid ids in PUNTOPAGOS_PAYMENT_METHODS.
        :param monto:       Transaction total amount.
        :param detalle:     Transaction detail (optional).
        '''
        now = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
        data = {
            'trx_id': trx_id,
            'medio_pago': medio_pago,
            'monto': monto,
            'detalle': detalle,
            'fecha': now
        }

        authorization_string = PUNTOPAGOS_SIGNABLE_HEADERS['create'] % data
        headers = self.create_headers(authorization_string, now)
        body = json.dumps(data)

        self.connection.request(method='POST', url=PUNTOPAGOS_ACTIONS['create'],
                                headers=headers, body=body)
        response = self.connection.getresponse()

        return PuntoPagoCreateResponse(response, sandbox=self.sandbox)

    def create_headers(self, authorization_string, now):
        '''
        Create standard headers for a puntopagos.com request

        :param authorization_string: Signable authorization string.
        :param now: struct_time usually returned by `gmtime()`
        '''
        signed = sign(authorization_string, self.config['secret'])
        params = {'apikey': self.config['key'], 'signed': signed}
        authorization = 'PP %(apikey)s:%(signed)s' % params
        return {
            'Fecha': now,
            'Autorizacion': authorization,
            'Content-Type': 'application/json'
        }
