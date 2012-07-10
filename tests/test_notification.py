import json
from unittest import TestCase

from mock import Mock

from puntopagos.notification import verify_notification, InvalidHeaderException, InvalidBodyException, InvalidNotificationException


class VerifyTest(TestCase):
    def setUp(self):
        self.key = '0PN5J17HBGZHT7ZZ3X82'
        self.secret = 'uV3F4YluFJax1cKnvbcGwgjvx4QpvB+leU8dUj2o'

    def test_verify_notification(self):
        body = '{"token":"9XJ08401WN0071839","trx_id":9787415132,"medio_pago":"999",' \
               '"monto":1000000.00,"fecha":"2009-06-15T20:49:00","numero_operacion":"7897851487",' \
               '"codigo_autorizacion":"34581"}'
        headers = {'Autorizacion': 'PP 0PN5J17HBGZHT7ZZ3X82:dGuEQg8Qb8vL+OyL+aQrUF6ZgOs=',
                   'Fecha': 'Mon, 15 Jun 2009 20:45:30 GMT',
                   'Content-Type': 'application/json'}
        
        result = verify_notification(headers=headers, body=body, key=self.key, secret=self.secret)

        self.assertEqual(json.loads(body), result)

    def test_verify_invalid_notification(self):
        body = '{"token":"9XJ08401WN0071839","trx_id":9787415132,"medio_pago":"999",' \
               '"monto":1000000.00,"fecha":"2009-06-15T20:49:00","numero_operacion":"7897851487",' \
               '"codigo_autorizacion":"34581"}'
        headers = {'Autorizacion': 'PP 0PN5J17HBGZHT7ZZ3X82:dGuEQg8Qb8vL+OyL+aQrUF6ZgMALA=',
                   'Fecha': 'Mon, 15 Jun 2009 20:45:30 GMT',
                   'Content-Type': 'application/json'}
        
        self.assertRaises(InvalidNotificationException, verify_notification, headers=headers, body=body, key=self.key, secret=self.secret)

    def test_verify_headers_wo_Fecha(self):
        body = '{"token":"9XJ08401WN0071839","trx_id":9787415132,"medio_pago":"999",' \
               '"monto":1000000.00,"fecha":"2009-06-15T20:49:00","numero_operacion":"7897851487",' \
               '"codigo_autorizacion":"34581"}'
        headers = {'Autorizacion': 'PP 0PN5J17HBGZHT7ZZ3X82:fU6+JLYWzOSGuo76XJzT/Z596Qg=',
                   'Content-Type': 'application/json'}
        
        self.assertRaises(InvalidHeaderException, verify_notification, headers=headers, body=body, key=self.key, secret=self.secret)

    def test_verify_headers_wo_Autorizacion(self):
        body = '{"token":"9XJ08401WN0071839","trx_id":9787415132,"medio_pago":"999",' \
               '"monto":1000000.00,"fecha":"2009-06-15T20:49:00","numero_operacion":"7897851487",' \
               '"codigo_autorizacion":"34581"}'
        headers = {'Fecha': 'Mon, 15 Jun 2009 20:48:30 GMT',
                   'Content-Type': 'application/json'}
        
        self.assertRaises(InvalidHeaderException, verify_notification, headers=headers, body=body, key=self.key, secret=self.secret)

    def test_verify_headers_wo_Contenttype(self):
        body = '{"token":"9XJ08401WN0071839","trx_id":9787415132,"medio_pago":"999",' \
               '"monto":1000000.00,"fecha":"2009-06-15T20:49:00","numero_operacion":"7897851487",' \
               '"codigo_autorizacion":"34581"}'
        headers = {'Fecha': 'Mon, 15 Jun 2009 20:48:30 GMT',
                   'Autorizacion': 'PP 0PN5J17HBGZHT7ZZ3X82:fU6+JLYWzOSGuo76XJzT/Z596Qg='}
        
        self.assertRaises(InvalidHeaderException, verify_notification, headers=headers, body=body, key=self.key, secret=self.secret)

    def test_verify_body_wo_trx_id(self):
        body = '{"token":"9XJ08401WN0071839","medio_pago":"999",' \
               '"monto":1000000.00,"fecha":"2009-06-15T20:49:00","numero_operacion":"7897851487",' \
               '"codigo_autorizacion":"34581"}'
        headers = {'Autorizacion': 'PP 0PN5J17HBGZHT7ZZ3X82:dGuEQg8Qb8vL+OyL+aQrUF6ZgOs=',
                   'Fecha': 'Mon, 15 Jun 2009 20:45:30 GMT',
                   'Content-Type': 'application/json'}
        
        self.assertRaises(InvalidBodyException, verify_notification, headers=headers, body=body, key=self.key, secret=self.secret)

    def test_verify_body_wo_monto(self):
        body = '{"token":"9XJ08401WN0071839","trx_id":9787415132,"medio_pago":"999",' \
               '"fecha":"2009-06-15T20:49:00","numero_operacion":"7897851487",' \
               '"codigo_autorizacion":"34581"}'
        headers = {'Autorizacion': 'PP 0PN5J17HBGZHT7ZZ3X82:dGuEQg8Qb8vL+OyL+aQrUF6ZgOs=',
                   'Fecha': 'Mon, 15 Jun 2009 20:45:30 GMT',
                   'Content-Type': 'application/json'}
        
        self.assertRaises(InvalidBodyException, verify_notification, headers=headers, body=body, key=self.key, secret=self.secret)


    def test_verify_body_wo_token(self):
        body = '{"trx_id":9787415132,"medio_pago":"999",' \
               '"monto":1000000.00,"fecha":"2009-06-15T20:49:00","numero_operacion":"7897851487",' \
               '"codigo_autorizacion":"34581"}'
        headers = {'Autorizacion': 'PP 0PN5J17HBGZHT7ZZ3X82:dGuEQg8Qb8vL+OyL+aQrUF6ZgOs=',
                   'Fecha': 'Mon, 15 Jun 2009 20:45:30 GMT',
                   'Content-Type': 'application/json'}
        
        self.assertRaises(InvalidBodyException, verify_notification, headers=headers, body=body, key=self.key, secret=self.secret)
