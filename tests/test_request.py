import json
from unittest import TestCase
from mock import Mock
from httplib import HTTPSConnection
from time import struct_time, mktime, gmtime, strftime
from decimal import Decimal, ROUND_UP

from puntopagos.request import PuntopagosRequest
from puntopagos.response import PuntopagosResponse
from puntopagos import util


class RequestTest(TestCase):
    def setUp(self):
        self.key = 'KEY'
        self.secret = 'SECRET'

    def test_create_request(self):
        request = PuntopagosRequest(key=self.key, secret=self.secret)

        self.assertTrue(isinstance(request, PuntopagosRequest))
        self.assertEqual(request.key, self.key)
        self.assertEqual(request.secret, self.secret)
        self.assertTrue(request.connection is not None)
        self.assertTrue(hasattr(request, 'time'))
        self.assertTrue(isinstance(request.time, struct_time))
        self.assertTrue(mktime(gmtime()) - mktime(request.time) < 60) # max 2 minutes for acceptance of puntopagos headers
    
    def test_create_request_default_connection(self):
        request = PuntopagosRequest(key=self.key, secret=self.secret)

        self.assertTrue(isinstance(request.connection, HTTPSConnection))
    
    def test_create_request_default_response_class(self):
        request = PuntopagosRequest(key=self.key, secret=self.secret)

        self.assertEqual(request.response_class, PuntopagosResponse)
    
    def test_create_request_custom_connection(self):
        connection = Mock()

        request = PuntopagosRequest(key=self.key, secret=self.secret, connection=connection)

        self.assertEqual(connection, request.connection)


class RequestCreateTest(TestCase):
    def setUp(self):
        self.connection = Mock()
        self.connection.getresponse.return_value = 'response'
        self.key = 'KEY'
        self.secret = 'SECRET'
        self.request = PuntopagosRequest(key=self.key, secret=self.secret, connection=self.connection)
        self.response_class = Mock()

    def test_call_create(self):
        trx_id = 'TRX_ID_1'
        medio_pago = 3
        monto = Decimal('100.002')
        detalle = 'Lorem ipsum dolor sit amet'
        authorization_string = util.authorization_string(action='create', trx_id=trx_id, monto=monto, fecha=self.request.time)
        headers = util.create_headers(authorization_string=authorization_string, 
                                      time=self.request.time, 
                                      key=self.request.key, secret=self.request.secret)
        fecha = strftime('%a, %d %b %Y %H:%M:%S GMT', self.request.time)
        body = json.dumps({'trx_id': trx_id, 
                           'medio_pago': medio_pago, 
                           'monto': float(monto.quantize(Decimal('0.01'), rounding=ROUND_UP)), 
                           'detalle': detalle, 
                           'fecha': fecha})
        self.request.response_class = self.response_class

        response = self.request.create(trx_id=trx_id, medio_pago=medio_pago, monto=monto, detalle=detalle)

        self.connection.request.assert_called_once_with(method='POST', url='/transaccion/crear', headers=headers, body=body)
        self.connection.getresponse.assert_called_once_with()
        self.response_class.assert_called_once_with(self.connection.getresponse())
        

class RequestStatusTest(TestCase):
    def setUp(self):
        self.connection = Mock()
        self.connection.getresponse.return_value = 'response'
        self.key = 'KEY'
        self.secret = 'SECRET'
        self.request = PuntopagosRequest(key=self.key, secret=self.secret, connection=self.connection)
        self.response_class = Mock()
    
    def test_get_status_aprobado(self):
        token = '9XJ08401WN0071839'
        trx_id = '9787415132'
        monto = Decimal('10.001')
        authorization_string = util.authorization_string(action='status', trx_id=trx_id, monto=monto, fecha=self.request.time, token=token)
        headers = util.create_headers(authorization_string=authorization_string, 
                                      time=self.request.time, 
                                      key=self.request.key, secret=self.request.secret)
        self.request.response_class = self.response_class

        response = self.request.status(token=token, trx_id=trx_id, monto=monto)
        
        self.connection.request.assert_called_once_with(method='GET', url='/transaccion/9XJ08401WN0071839', headers=headers)
        self.connection.getresponse.assert_called_once_with()
        self.response_class.assert_called_once_with(self.connection.getresponse())


