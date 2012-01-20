import json

from httplib import HTTPSConnection
from time import gmtime, strftime
from decimal import Decimal, ROUND_UP

from puntopagos.response import PuntopagosResponse
from puntopagos import util


class PuntopagosRequest:
    key = None
    secret = None
    response_class = PuntopagosResponse

    def __init__(self, key, secret,
                       connection=None, ssl=True, sandbox=False, debug=0):
        self.key = key
        self.secret = secret
        self.time = gmtime()

        if connection:
            self.connection = connection
        else:
            self.connection = util.get_connection(ssl, sandbox, debug)

    def create(self, trx_id, medio_pago, monto, detalle):
        authorization_string = util.authorization_string(action='create',
                                                         trx_id=trx_id,
                                                         monto=monto,
                                                         fecha=self.time)
        headers = util.create_headers(authorization_string=authorization_string,
                                      time=self.time, key=self.key, secret=self.secret)
        fecha = strftime(util.RFC1123_FORMAT, self.time)
        body = json.dumps({'trx_id': trx_id,
                           'medio_pago': medio_pago,
                           'monto': float(monto.quantize(Decimal('0.01'), rounding=ROUND_UP)),
                           'detalle': detalle, 
                           'fecha': fecha})

        self.connection.request(method='POST', url='/transaccion/crear', headers=headers, body=body)
        response = self.connection.getresponse()
        return self.response_class(response)

    def status(self, token, trx_id, monto):
        authorization_string = util.authorization_string(action='status', trx_id=trx_id, 
                                                         monto=monto, fecha=self.time, token=token)
        headers = util.create_headers(authorization_string=authorization_string, 
                                      time=self.time, 
                                      key=self.key, secret=self.secret)
        self.connection.request(url='/transaccion/%(token)s' % {'token': token}, headers=headers, method='GET')
        response = self.connection.getresponse()
        return self.response_class(response)
