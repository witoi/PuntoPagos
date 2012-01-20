import json
import decimal


class PuntopagosBadResponseError(Exception):
    pass


class PuntopagosResponse:
    http_error = None
    error = None

    def __init__(self, response):
        self.complete = response.status is 200
        if self.complete:
            float_parser = lambda x: decimal.Decimal(x).quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_UP)
            try:
                data_dict = json.loads(response.read(), parse_float=float_parser)
            except ValueError:
                raise PuntopagosBadResponseError
            self._data = tuple(data_dict.items()) # We don't want mutables for this
            self.error = data_dict['error'] if 'error' in data_dict else None
        else:
            self.http_error = response.status

    def get_data(self):
        return dict(self._data)
