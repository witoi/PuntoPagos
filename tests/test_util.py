from unittest import TestCase
from time import strptime
from decimal import Decimal
from httplib import HTTPConnection, HTTPSConnection

from puntopagos import util


class AuthorizationStringTest(TestCase):
    def test_authorization_create(self):
        trx_id = 'trx_id_1'
        monto = Decimal('100.02')
        fecha = strptime('Thu, 19 Jan 2012 18:05:25 GMT', "%a, %d %b %Y %H:%M:%S GMT")

        authorization_string = util.authorization_string(action='create', trx_id=trx_id, monto=monto, fecha=fecha)

        self.assertEqual(authorization_string, 'transaccion/crear\ntrx_id_1\n100.02\nThu, 19 Jan 2012 18:05:25 GMT')
   
    def test_authorization_status(self):
        trx_id = '9787415132'
        token = '9XJ08401WN0071839'
        fecha = strptime('Mon, 15 Jun 2009 20:50:30 GMT', "%a, %d %b %Y %H:%M:%S GMT")
        monto = Decimal('10.002')

        authorization_string = util.authorization_string(action='status', trx_id=trx_id, monto=monto, fecha=fecha, token=token)

        expected = 'transaccion/traer\n9XJ08401WN0071839\n9787415132\n10.01\nMon, 15 Jun 2009 20:50:30 GMT'
        self.assertEqual(authorization_string, expected)

    def test_authorization_notification(self):
        trx_id = '9787415132'
        token = '9XJ08401WN0071839'
        fecha = strptime('Mon, 15 Jun 2009 20:50:30 GMT', "%a, %d %b %Y %H:%M:%S GMT")
        monto = Decimal('10.002')

        authorization_string = util.authorization_string(action='notification', trx_id=trx_id, monto=monto, fecha=fecha, token=token)

        expected = 'transaccion/notificacion\n9XJ08401WN0071839\n9787415132\n10.01\nMon, 15 Jun 2009 20:50:30 GMT'
        self.assertEqual(authorization_string, expected)


class CreateHeadersTest(TestCase):
    def setUp(self):
        self.key = '0PN5J17HBGZHT7ZZ3X82'
        self.secret = 'uV3F4YluFJax1cKnvbcGwgjvx4QpvB+leU8dUj2o'
        self.time = strptime('Mon, 15 Jun 2009 20:45:30 GMT', '%a, %d %b %Y %H:%M:%S GMT')
        self.authorization_string = 'transaccion/crear\n9787415132\n1000000.00\nMon, 15 Jun 2009 20:45:30 GMT'

    def test_create_headers(self):
        authorization = 'PP 0PN5J17HBGZHT7ZZ3X82:AVrD3e9idIqAxRSH+15Yqz7qQkc='
        expected = {'Fecha': 'Mon, 15 Jun 2009 20:45:30 GMT', 'Autorizacion': authorization, 'Content-Type': 'application/json; charset=utf-8'}

        headers = util.create_headers(authorization_string=self.authorization_string, time=self.time, key=self.key, secret=self.secret)

        self.assertEqual(headers, expected)


class CreatePuntopagosConnection(TestCase):
    def test_create_puntopagos_ssl_connection(self):
        connection = util.get_connection(ssl=True, sandbox=False)
        
        self.assertTrue(isinstance(connection, HTTPSConnection))
        self.assertEqual(connection.host, 'www.puntopagos.com')

    def test_create_puntopagos_nossl_connection(self):
        connection = util.get_connection(ssl=False, sandbox=False)
        
        self.assertTrue(isinstance(connection, HTTPConnection))
        self.assertEqual(connection.host, 'www.puntopagos.com')
        
    def test_create_puntopagos_ssl_sandbox_connection(self):
        connection = util.get_connection(ssl=True, sandbox=True)
        
        self.assertTrue(isinstance(connection, HTTPSConnection))
        self.assertEqual(connection.host, 'sandbox.puntopagos.com')

    def test_create_puntopagos_nossl_sandbox_connection(self):
        connection = util.get_connection(ssl=False, sandbox=True)
        
        self.assertTrue(isinstance(connection, HTTPConnection))
        self.assertEqual(connection.host, 'sandbox.puntopagos.com')

    def test_create_puntopagos_ssl_sandbox_connection_debug(self):
        debug_level = 3
        
        connection = util.get_connection(ssl=False, sandbox=True, debug=debug_level)
        
        self.assertEqual(connection.debuglevel, debug_level)
