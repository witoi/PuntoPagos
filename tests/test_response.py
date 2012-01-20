#encoding=UTF-8

import json
from unittest import TestCase
from mock import Mock
import decimal

from puntopagos.response import PuntopagosResponse, PuntopagosBadResponseError


class PuntopagosResponseTest(TestCase):
    def setUp(self):
        self.http_response = Mock()
        self.fixture = {
            'autorizado': '{"codigo_autorizacion":"281172","error":null,"fecha_aprobacion":"2012-01-19T17:07:47",' \
                          '"medio_pago":"3","medio_pago_descripcion":"WebPay Transbank","monto":15000.00,' \
                          '"num_cuotas":0,"numero_operacion":"6998364387","numero_tarjeta":"6623",' \
                          '"primer_vencimiento":null,"respuesta":"00","tipo_cuotas":"Sin Cuotas","tipo_pago":null,' \
                          '"token":"LY26HNR6XNG8KN9W","trx_id":"79","valor_cuota":0}',
            'incompleta': '{"codigo_autorizacion":null,"error":"Transaccion incompleta","fecha_aprobacion":null,' \
                          '"medio_pago":null,"medio_pago_descripcion":null,"monto":0,"num_cuotas":0,' \
                          '"numero_operacion":null,"numero_tarjeta":null,"primer_vencimiento":null,"respuesta":"6",' \
                          '"tipo_cuotas":null,"tipo_pago":null,"token":"LY27TCESRB72PQLM","trx_id":null,"valor_cuota":0}',
            'rechazado':  '{"codigo_autorizacion":null,"error":"Transaccion rechazada","fecha_aprobacion":null,' \
                          '"medio_pago":null,"medio_pago_descripcion":null,"monto":0,"num_cuotas":0,"numero_operacion":null,' \
                          '"numero_tarjeta":null,"primer_vencimiento":null,"respuesta":"1","tipo_cuotas":null,' \
                          '"tipo_pago":null,"token":"LY26P3402U1YXGKN","trx_id":null,"valor_cuota":0}',
            'novalido':   '{"error":"Financiador no válido","monto":0,"respuesta":"99","token":null,"trx_id":null}'
        }

    def test_instance_complete(self):
        self.http_response.status = 200

        self.http_response.read.return_value = self.fixture['autorizado']
        data = json.loads(self.fixture['autorizado'],
                          parse_float=lambda x: decimal.Decimal(x).quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_UP))

        response = PuntopagosResponse(response=self.http_response)

        self.assertTrue(isinstance(response, PuntopagosResponse))
        self.assertTrue(hasattr(response, 'http_error'))
        self.assertTrue(response.http_error is None)
        self.assertTrue(hasattr(response, 'error'))
        self.assertTrue(response.error is None)
        self.assertTrue(hasattr(response, 'complete'))
        self.assertTrue(response.complete)
        self.assertTrue(hasattr(response, '_data'))
        self.assertTrue(isinstance(response._data, tuple))
        self.assertEqual(response._data, tuple(data.items()))
        self.http_response.read.assert_called_once()

    def test_instance_400(self):
        self.http_response.status = 400
        self.http_response.read.return_value = '<html><body>400 bad request</body></html>'

        response = PuntopagosResponse(response=self.http_response)

        self.assertFalse(response.complete)
        self.assertEqual(response.http_error, 400)
    
    def test_puntopagos_wrong_response(self):
        self.http_response.status = 200
        self.http_response.read.return_value = '<html><body>Hello, world</body></html>'

        try:
            PuntopagosResponse(response=self.http_response)
        except PuntopagosBadResponseError:
            return # ok
        self.assertTrue(False, "doesn't raise error")
            
    def test_get_data(self):
        self.http_response.status = 200
        self.http_response.read.return_value = self.fixture['autorizado']

        response = PuntopagosResponse(response=self.http_response)

        data = response.get_data()

    def test_instance_financiador_no_valido(self):
        self.http_response.status = 200
        self.http_response.read.return_value = self.fixture['novalido']

        response = PuntopagosResponse(self.http_response)

        self.assertEqual(response.error, u"Financiador no válido")
