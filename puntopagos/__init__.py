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


def create_signable(action, data):
    return "\n".join([action] + list(data))


def sign(string, key):
    return base64.b64encode(hmac.HMAC(key, string, hashlib.sha1).digest())


class PuntoPagoResponse:
    success = False
    complete = False
    data = {}
    trx_id = None
    ammount = None
    token = None

    def __init__(self, response, sandbox=False):
        self.complete = response.status == 200
        if self.complete:
            try:
                self.data = json.loads(response.read())
            except ValueError:
                pass
            else:
                self.trx_id = self.data['trx_id']
                self.ammount = self.data['monto']
                self.token = self.data['token']
                params = {
                    'url': PUNTOPAGOS_URLS['sandbox' if sandbox else 'production'],
                    'token': self.token
                }
                self.redirection_url = "%(url)stransaccion/procesar/%(token)s" % params
                self.success = self.data['respuesta'] == u'00'


class PuntoPagoRequest:
    create_url = None

    def __init__(self, config, sandbox=False, ssl=True):
        url = PUNTOPAGOS_URLS['sandbox' if sandbox else 'production']
        if ssl:
            self.conn = httplib.HTTPSConnection(url)
        else:
            self.conn = httplib.HTTPConnection(url)
        # self.conn.set_debuglevel(3 if sandbox else 0)

        self.config = config
        self.sandbox = sandbox

    def create(self, data):
        assert isinstance(data, dict), "data must be `dict` type"

        jsonified = json.dumps(data)

        headers = self.create_headers(data)
        self.conn.request('POST',
                          PUNTOPAGOS_ACTIONS['create'],
                          headers=headers,
                          body=jsonified)
        response = self.conn.getresponse()
        return PuntoPagoResponse(response, sandbox=self.sandbox)

    def create_headers(self, data):
        now = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
        data_string = data.copy()
        data_string['fecha'] = now
        authorization_string = create_signable(action='transaccion/crear',
                                               data=('%(trx_id)s',
                                                     '%(monto)0.2f',
                                                     '%(fecha)s')) % data_string
        signed = sign(authorization_string, self.config['secret'])

        params = {'apikey': self.config['key'], 'signed': signed}
        authorization = 'PP %(apikey)s:%(signed)s' % params

        return {
            'Fecha': now,
            'Autorizacion': authorization,
	    'Content-Type': 'application/json'
        }


class PuntoPagoNotification:
    '''
    Verify the authenticity of a puntopago's response
    and create an abstraction.
    '''

    authorized = False
    ''' False when response can't be verified. '''

    data = {}
    ''' Response json string as python dict. '''

    def __init__(self, config, json_data, date, autorization):
        self.data = json.loads(json_data)
        self.date = date

        # set authorization_string RFC1123 date
        data_string = self.data.copy()
        data_string['fecha'] = date

        authorization_string = create_signable(action='transaccion/notificacion',
                                               data=('%(token)s',
                                                     '%(trx_id)d',
                                                     '%(monto)0.2f',
                                                     '%(fecha)s')) % data_string

        # sign authorization string
        signed = sign(authorization_string, config['secret'])

        params = {'apikey': config['key'], 'signed': signed}
        authorization_expected = 'PP %(apikey)s:%(signed)s' % params

        self.authorized = authorization_expected == autorization

        if self.authorized:
            self.response = json.dumps({
                'respuesta': PUNTOPAGOS_CODES['ok'],
                'token': self.data['token']
            })
        else:
            self.response = json.dumps({'respuesta': PUNTOPAGOS_CODES['no_ok']})
