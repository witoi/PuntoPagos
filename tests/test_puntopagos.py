import unittest

import json
import base64
import ConfigParser
import sys

from puntopagos import (PuntoPagoRequest, PuntoPagoResponse, PuntoPagoNotification, \
                        sign, create_signable, PUNTOPAGOS_URLS)
import puntopagos

try:
    config = ConfigParser.ConfigParser()
    config.readfp(open('config.ini'))
    APIKEY = config.get('PuntoPagos', 'key')
    APISECRET = config.get('PuntoPagos', 'secret')
except:
    sys.stderr.write("Can not run test without 'APIKEY' and 'APISECRET'\n")
    sys.stderr.write("Put yours in 'config.ini'\n")
    sys.exit(1)


class UtilTest(unittest.TestCase):
    def test_create_signable(self):
        expected = 'transaccion/crear\n' \
                   '9787415132\n' \
                   '1000000.00\n' \
                   'Mon, 15 Jun 2009 20:50:30 GMT'

        signable = create_signable(action='transaccion/crear',
                                   data=('9787415132',
                                         '1000000.00',
                                         'Mon, 15 Jun 2009 20:50:30 GMT'))
        self.assertEquals(expected, signable)

    def test_sign(self):
        example_secret = 'uV3F4YluFJax1cKnvbcGwgjvx4QpvB+leU8dUj2o'

        expected = 'AVrD3e9idIqAxRSH+15Yqz7qQkc='
        signable = create_signable(action='transaccion/crear',
                                   data=('9787415132',
                                         '1000000.00',
                                         'Mon, 15 Jun 2009 20:45:30 GMT'))

        autorization = sign(signable, example_secret)
        self.assertEquals(autorization, expected)


class RequestTest(unittest.TestCase):
    def setUp(self):
        self.config = {'key': APIKEY, 'secret': APISECRET}

    #Step 1, 2 and 3
    def test_create_transaction(self):
        request = PuntoPagoRequest(sandbox=True,
                                   config=self.config)
        response = request.create({
            'trx_id': '1',
            'medio_pago': "3",
            'monto': 100.0,
        })
        self.assertTrue(isinstance(response, PuntoPagoResponse))
        self.assertTrue(response.complete)
        self.assertTrue(response.success)
        self.assertEquals(response.trx_id, '1')
        self.assertEquals(response.ammount, 100.0)
        self.assertTrue(response.token is not None)
        params = {
            'url': PUNTOPAGOS_URLS['sandbox'],
            'token': response.token
        }
        expected_url = "%(url)stransaccion/procesar/%(token)s" % params
        self.assertEquals(response.redirection_url,
                          'http://' + PUNTOPAGOS_URLS['sandbox'] +
                          '/transaccion/procesar/' + response.token)

class ResponseTest(unittest.TestCase):
    def setUp(self):
        self.config = {'key': '0PN5J17HBGZHT7ZZ3X82', 'secret': 'uV3F4YluFJax1cKnvbcGwgjvx4QpvB+leU8dUj2o'}

    #Step 4 and 5
    def test_json_response(self):
        to_json = {
            "token": "9XJ08401WN0071839",
            "trx_id": 9787415132,
            "medio_pago": "999",
            "monto": 1000000.00,
            "fecha": "2009-06-15T20:50:30",
            "numero_operacion": "7897851487",
            "codigo_autorizacion": "34581"
        }
        date = "Mon, 15 Jun 2009 20:50:30 GMT"
        notification_string = create_signable(
                                action='transaccion/notificacion',
                                data=('9XJ08401WN0071839',
                                      '9787415132',
                                      '1000000.00',
                                      'Mon, 15 Jun 2009 20:50:30 GMT'))
        autorization = "PP %(apikey)s:%(signed)s" % {
            'apikey': self.config['key'],
            'signed': sign(notification_string, self.config['secret'])}

        json_data = json.dumps(to_json)
        notification = PuntoPagoNotification(config=self.config,
                                             json_data=json_data,
                                             date=date,
                                             autorization=autorization)
        self.assertEquals(notification.data, to_json)
        self.assertTrue(notification.authorized)

        unjsonified_expected_response = {"respuesta": "00", "token": "9XJ08401WN0071839"}
        unjsonified_response = json.loads(notification.response)
        self.assertEquals(unjsonified_expected_response, unjsonified_response)
