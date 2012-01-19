from decimal import Decimal, ROUND_UP
from time import strftime
import base64
import hmac
import hashlib


def authorization_string(action, trx_id, monto, fecha, token=None):
    monto = str(monto.quantize(Decimal('0.01'), rounding=ROUND_UP))
    fecha = strftime("%a, %d %b %Y %H:%M:%S GMT", fecha)
    if action == 'create':
        return 'transaccion/crear\n%(trx_id)s\n%(monto)s\n%(fecha)s' % locals()
    elif action == 'status':
        return 'transaccion/traer\n%(token)s\n%(trx_id)s\n%(monto)s\n%(fecha)s' % locals()


def create_headers(authorization_string, time, key, secret):
    sign = base64.b64encode(hmac.HMAC(secret, authorization_string, hashlib.sha1).digest())
    return {'Fecha': strftime('%a, %d %b %Y %H:%M:%S GMT', time),
            'Autorizacion': 'PP %(key)s:%(sign)s' % {'key': key, 'sign': sign},
            'Content-Type': 'application/json'}
