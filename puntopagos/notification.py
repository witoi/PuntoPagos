import json
import decimal

from time import strptime

from puntopagos import util


class InvalidHeaderException(Exception): pass


class InvalidBodyException(Exception): pass


class InvalidNotificationException(Exception): pass



def verify_notification(headers, body, key, secret):
    body = json.loads(body, parse_float=lambda x: decimal.Decimal(x).quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_UP))

    if 'Fecha' not in headers or 'Autorizacion' not in headers:
        raise InvalidHeaderException

    fecha = strptime(headers['Fecha'], "%a, %d %b %Y %H:%M:%S GMT")

    try:
        authorization_string = util.authorization_string(action='notification',
                                                     trx_id=body['trx_id'],
                                                     monto=body['monto'],
                                                     fecha=fecha,
                                                     token=body['token'])
    except KeyError:
        raise InvalidBodyException

    expected_headers = util.create_headers(authorization_string, fecha, key, secret)

    for key, value in expected_headers.items():
        try:
            if headers[key] != value:
                raise InvalidNotificationException
        except KeyError:
            raise InvalidHeaderException

    return body
