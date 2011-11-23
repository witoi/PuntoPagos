import json
import httplib
from time import strftime, gmtime

from pp_util import sign

CODES = {
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


class PuntoPagoResponse:
    success = False
    complete = False

    def __init__(self, response):
        self.complete = response.status == 200


class PuntoPagoRequest:
    create_url = None

    def __init__(self, config, sandbox=False):
        url = PUNTOPAGOS_URLS['sandbox' if sandbox else 'production']
        self.conn = httplib.HTTPSConnection(url, port=443)
        self.conn.set_debuglevel(3 if sandbox else 0)

        self.config = config

    def create(self, data):
        assert isinstance(data, dict)

        jsonified = json.dumps(data)

        headers = self.create_headers(data)
        self.conn.request('POST',
                          PUNTOPAGOS_ACTIONS['create'],
                          headers=headers,
                          body=jsonified)
        response = self.conn.getresponse()
        return PuntoPagoResponse(response)
    
    def create_headers(self, data):
        now = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
        data_string = data.copy()
        data_string['fecha'] = now
        authorization_string = '\n'.join(('transaccion/notificacion',
                                           '%(trx_id)d',
                                           '%(monto)0.2f',
                                           '%(fecha)s')) % data_string
        signed = sign(authorization_string, self.config['secret'])
        params = {'apikey': self.config['key'], 'signed': signed}
        authorization = 'PP %(apikey)s:%(signed)s' % params

        return {
            'Fecha': now,
            'Autorizacion': authorization,
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

    def __init__(self, config, json_data, date, autorization, ex):
        self.data = json.loads(json_data)
        self.date = date

        # set authorization_string RFC1123 date
        data_string = self.data.copy()
        data_string['fecha'] = date

        authorization_string = '\n'.join(('transaccion/notificacion',
                                           '%(token)s',
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
                'respuesta': CODES['ok'],
                'token': self.data['token']
            })
        else:
            self.response = json.dumps({'respuesta': CODES['no_ok']})
