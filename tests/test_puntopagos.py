import unittest

import json as simplejson
import base64

from puntopagos import PuntoPagoRequest, PuntoPagoResponse, pp_util, PuntoPagoNotification

#Set your API KEY
APIKEY = '0PN5J17HBGZHT7ZZ3X82'
#Set your API SECRET
APISECRET = 'uV3F4YluFJax1cKnvbcGwgjvx4QpvB+leU8dUj2o'

EXAMPLE_AUTHORIZATION = "transaccion/traer\n9XJ08401WN0071839\n9787415132\n1000000.00\nMon, 15 Jun 2009 20:50:30 GMT"
EXAMPLE_AUTHORIZATION_NOTIFICATION = "transaccion/notificacion\n9XJ08401WN0071839\n9787415132\n1000000.00\nMon, 15 Jun 2009 20:50:30 GMT"


class UtilTest(unittest.TestCase):
    def test_sign(self):
        autorization = pp_util.sign(EXAMPLE_AUTHORIZATION, APISECRET)
        expected = 'r9XTqzmGmu/UCGkMhkdIwUKMM88='
        self.assertEquals(autorization, expected)


class RequestTest(unittest.TestCase):
    def setUp(self):
        self.config = {'key': APIKEY, 'secret': APISECRET}

    #Step 1, 2 and 3
    def test_create_transaction(self):
        request = PuntoPagoRequest(sandbox=True,
                                   config=self.config)
        response = request.create({
            'trx_id': 1,
            'medio_pago': '999',
            'monto': 100.0
        })
        self.assertTrue(isinstance(response, PuntoPagoResponse))
        self.assertTrue(response.complete)
        self.assertTrue(response.success)
        self.assertEquals(response.trx_id, 1)
        self.assertEquals(response.ammount, '100.00')
        self.assertTrue(response.token is not None)
        params = {
            'url': PuntoPagoRequest.SANDBOX_URL,
            'token': response.token
        }
        expected_url = "%(url)stransaccion/procesar/%(token)s" % params
        self.assertEquals(response.redirection_url,
                          PuntoPagoRequest.SANDBOX_URL +
                          'transaccion/procesar/' + response.token)

    #Step 4 and 5
    def test_json_response(self):
        to_json = {
            "token": "9XJ08401WN0071839",
            "trx_id": 9787415132,
            "medio_pago": "999",
            "monto": 1000000.0,
            "fecha": "2009-06-15T20:50:30",
            "numero_operacion": "7897851487",
            "codigo_autorizacion": "34581"
        }
        date = "Mon, 15 Jun 2009 20:50:30 GMT"
        autorization = "PP %(apikey)s:%(signed)s" % {
            'apikey': APIKEY,
            'signed': pp_util.sign(EXAMPLE_AUTHORIZATION_NOTIFICATION, APISECRET)}

        json = simplejson.dumps(to_json)
        notification = PuntoPagoNotification(config=self.config,
                                             json_data=json,
                                             date=date,
                                             autorization=autorization,
                                             ex=EXAMPLE_AUTHORIZATION_NOTIFICATION)                       
        self.assertEquals(notification.data, to_json)
        self.assertTrue(notification.authorized)

        unjsonified_expected_response = {"respuesta": "00", "token": "9XJ08401WN0071839"}
        unjsonified_response = simplejson.loads(notification.response)
        self.assertEquals(unjsonified_expected_response, unjsonified_response)
