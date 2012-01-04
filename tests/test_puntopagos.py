import unittest
import json
import ConfigParser
import sys
import os

from puntopagos import (PuntoPagoRequest, PuntoPagoCreateResponse,\
                        PuntoPagoStatusResponse, sign, PUNTOPAGOS_URLS, PUNTOPAGOS_SIGNABLE_HEADERS)


config_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
try:
    config = ConfigParser.ConfigParser()
    config.readfp(open(config_filename))
    APIKEY = config.get('PuntoPagos', 'key')
    APISECRET = config.get('PuntoPagos', 'secret')
except:
    sys.stderr.write("Can not run test without 'APIKEY' and 'APISECRET'\n")
    sys.stderr.write("Put yours in '%s'\n" % config_filename)
    sys.exit(1)


class UtilTest(unittest.TestCase):
    def test_sign(self):
        example_secret = 'uV3F4YluFJax1cKnvbcGwgjvx4QpvB+leU8dUj2o'
        expected = 'AVrD3e9idIqAxRSH+15Yqz7qQkc='

        data={
            'trx_id': '9787415132', 
            'monto': 1000000.00,
            'fecha': 'Mon, 15 Jun 2009 20:45:30 GMT'
        }
        signable = PUNTOPAGOS_SIGNABLE_HEADERS['create'] % data
        autorization = sign(signable, example_secret)
        self.assertEquals(autorization, expected)


class RequestTest(unittest.TestCase):
    def setUp(self):
        self.config = {'key': APIKEY, 'secret': APISECRET}

    def test_create_transaction_and_use_it_for_test_status(self):
        request = PuntoPagoRequest(sandbox=True,
            config=self.config)
        creation_data = {
            'trx_id': '4',
            'medio_pago': "3",
            'monto': 100.0,
            }
        response = request.create(**creation_data)
        self.assertTrue(isinstance(response, PuntoPagoCreateResponse))
        self.assertTrue(response.complete)
        self.assertTrue(response.success)
        self.assertEquals(response.trx_id, creation_data['trx_id'])
        self.assertEquals(response.amount, 100.0)
        self.assertTrue(response.token is not None)
        params = {
            'url': PUNTOPAGOS_URLS['sandbox'],
            'token': response.token
        }
        expected_url = "%(url)stransaccion/procesar/%(token)s" % params
        self.assertEquals(response.redirection_url,
            'http://' + PUNTOPAGOS_URLS['sandbox'] +
            '/transaccion/procesar/' + response.token)

        # Begin status test
        status_response = request.status(token=response.token, monto=response.amount, trx_id=response.trx_id)
        self.assertTrue(isinstance(status_response, PuntoPagoStatusResponse))
        self.assertTrue(status_response.data['token'], response.token)
