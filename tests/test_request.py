from unittest import TestCase
from mock import Mock
from httplib import HTTPSConnection
from time import struct_time, mktime, gmtime, strftime
from decimal import Decimal, ROUND_UP
import json

from puntopagos.request import PuntopagoRequest
from puntopagos.response import PuntopagosCreateResponse, PuntopagosStatusResponse
from puntopagos import util


class RequestTest(TestCase):
    def setUp(self):
        self.key = 'KEY'
        self.secret = 'SECRET'

    def tearDown(self):
        pass

    def test_create_request(self):
        request = PuntopagoRequest(key=self.key, secret=self.secret)

        self.assertTrue(isinstance(request, PuntopagoRequest))
        self.assertEqual(request.key, self.key)
        self.assertEqual(request.secret, self.secret)
        self.assertTrue(request.connection is not None)
        self.assertTrue(hasattr(request, 'time'))
        self.assertTrue(isinstance(request.time, struct_time))
        self.assertTrue(mktime(gmtime()) - mktime(request.time) < 60) # max 2 minutes for acceptance of puntopagos headers
    
    def test_create_request_default_connection(self):
        request = PuntopagoRequest(key=self.key, secret=self.secret)

        self.assertTrue(isinstance(request.connection, HTTPSConnection))
    
    def test_create_request_default_create_response_class(self):
        request = PuntopagoRequest(key=self.key, secret=self.secret)

        self.assertEqual(request.create_response_class, PuntopagosCreateResponse)
    
    def test_create_request_default_status_response_class(self):
        request = PuntopagoRequest(key=self.key, secret=self.secret)

        self.assertEqual(request.status_response_class, PuntopagosStatusResponse)
        
    def test_create_request_custom_connection(self):
        connection = Mock()

        request = PuntopagoRequest(key=self.key, secret=self.secret, connection=connection)

        self.assertEqual(connection, request.connection)


class RequestCreateTest(TestCase):
    def setUp(self):
        self.connection = Mock()
        self.connection.request.return_value = 'response'
        self.key = 'KEY'
        self.secret = 'SECRET'
        self.request = PuntopagoRequest(key=self.key, secret=self.secret, connection=self.connection)
        self.create_response_class = Mock()

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
        self.request.create_response_class = self.create_response_class

        response = self.request.create(trx_id=trx_id, medio_pago=medio_pago, monto=monto, detalle=detalle)

        self.connection.request.assert_called_once_with(method='POST', url='/transaccion/crear', headers=headers, body=body)
        self.create_response_class.assert_called_once_with(self.connection.request())
        

class RequestStatusTest(TestCase):
    def setUp(self):
        self.connection = Mock()
        self.connection.request.return_value = 'response'
        self.key = 'KEY'
        self.secret = 'SECRET'
        self.request = PuntopagoRequest(key=self.key, secret=self.secret, connection=self.connection)
        self.status_response_class = Mock()
    
    def test_get_status_aprobado(self):
        token = '9XJ08401WN0071839'
        trx_id = '9787415132'
        monto = Decimal('10.001')
        expected = '{"respuesta":"00","token":"9XJ08401WN0071839","trx_id":"9787415132","medio_pago":"999","' \
                   'monto":10.01,"fecha":"2009-06-15T20:49:00","numero_operacion":"7897851487",' \
                   '"codigo_autorizacion":"34581"}'

        authorization_string = util.authorization_string(action='status', trx_id=trx_id, monto=monto, fecha=self.request.time, token=token)
        headers = util.create_headers(authorization_string=authorization_string, 
                                      time=self.request.time, 
                                      key=self.request.key, secret=self.request.secret)
        self.request.status_response_class = self.status_response_class

        response = self.request.status(token=token, trx_id=trx_id, monto=monto)
        
        self.connection.request.assert_called_once_with(method='GET', url='/transaccion/traer', headers=headers)
        self.status_response_class.assert_called_once_with(self.connection.request())


