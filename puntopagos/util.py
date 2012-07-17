import base64
import hmac
import hashlib
import httplib
from decimal import Decimal, ROUND_UP
from time import strftime

AUTHORIZATION_STRINGS = {
    'create': 'transaccion/crear\n%(trx_id)s\n%(monto)s\n%(fecha)s',
    'status': 'transaccion/traer\n%(token)s\n%(trx_id)s\n%(monto)s\n%(fecha)s',
    'notification': 'transaccion/notificacion\n%(token)s\n%(trx_id)s\n%(monto)s\n%(fecha)s'
}

RFC1123_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'


def authorization_string(action, trx_id, monto, fecha, token=None):
    monto = str(monto.quantize(Decimal('0.01'), rounding=ROUND_UP))
    fecha = strftime(RFC1123_FORMAT, fecha)
    if action in AUTHORIZATION_STRINGS:
        return AUTHORIZATION_STRINGS[action] % locals()


def create_headers(authorization_string, time, key, secret):
    sign = base64.b64encode(hmac.HMAC(secret, authorization_string, hashlib.sha1).digest())
    return {'Fecha': strftime(RFC1123_FORMAT, time),
            'Autorizacion': 'PP %(key)s:%(sign)s' % {'key': key, 'sign': sign},
            'Content-Type': 'application/json; charset=utf-8'}


def get_connection(ssl=True, sandbox=False, debug=0):
    host = 'sandbox.puntopagos.com' if sandbox else 'www.puntopagos.com'
    connection = httplib.HTTPSConnection(host) if ssl else httplib.HTTPConnection(host)
    connection.set_debuglevel(debug)
    return connection
