import json

from httplib import HTTPSConnection
from time import gmtime, strftime
from decimal import Decimal, ROUND_UP

from puntopagos.response import PuntopagosCreateResponse, PuntopagosStatusResponse
from puntopagos import util


class PuntopagoRequest:
    key = None
    secret = None
    create_response_class = PuntopagosCreateResponse
    status_response_class = PuntopagosStatusResponse

    def __init__(self, key, secret, connection=None):
        self.key = key
        self.secret = secret
        self.time = gmtime()

        if connection:
            self.connection = connection
        else:
            self.connection = HTTPSConnection('www.puntopagos.com')
    
    def create(self, trx_id, medio_pago, monto, detalle):
        authorization_string = util.authorization_string(action='create', trx_id=trx_id, 
                                                         monto=monto, fecha=self.time)
        headers = util.create_headers(authorization_string=authorization_string, 
                                      time=self.time, 
                                      key=self.key, secret=self.secret)
        fecha = strftime('%a, %d %b %Y %H:%M:%S GMT', self.time)
        body = json.dumps({'trx_id': trx_id, 
                           'medio_pago': medio_pago, 
                           'monto': float(monto.quantize(Decimal('0.01'), rounding=ROUND_UP)), 
                           'detalle': detalle, 
                           'fecha': fecha})

        response = self.connection.request(method='POST', url='/transaccion/crear', headers=headers, body=body)
        return self.create_response_class(response)

    def status(self, token, trx_id, monto):
        authorization_string = util.authorization_string(action='status', trx_id=trx_id, 
                                                         monto=monto, fecha=self.time, token=token)
        headers = util.create_headers(authorization_string=authorization_string, 
                                      time=self.time, 
                                      key=self.key, secret=self.secret)
        response = self.connection.request(url='/transaccion/traer', headers=headers, method='GET')

        return self.status_response_class(response)
