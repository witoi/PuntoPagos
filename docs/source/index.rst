PuntoPagos Python API Documentation
***********************************


PuntopagosRequest class
=======================

For any operation with puntopagos you need a request object, this object provide 2 methods to create a transaction and retrieve the status. Creating a PuntopagosRequest object is as simple as next example.

    >>> from puntopagos.request import PuntopagosRequest
    >>> request = PuntopagosRequest(key='API-KEY', secret='API-SECRET')

The request instanciated above use a HTTPSConnection from httplib, if you want to use a different kind of connection, you need to emulate the API of this class and pass it as a parameter.

    >>> request = PuntopagosRequest(key='API-KEY', secret='API-SECRET', connection=MyOwnConnection('www.puntopagos.com'))

An useful implementation of this API is HTTPConnection (without the S), if you don't want SSL encryption.

    >>> request = PuntopagosRequest(key='API-KEY', secret='API-SECRET', connection=HTTPConnection('www.puntopagos.com'))

We provide an useful function to create connections for puntopagos.
    
    >>> from puntopagos.util import get_connection
    >>> connection = get_connection(ssl=True, sandbox=True, debug=3)
    <httplib.HTTPSConnection instance at 0x1748ef0>
    >>> connection.host
    'sandbox.puntopagos.com'
    >>> connection.debuglevel
    3


Create a transaction
====================

Creating a transaction needs 4 arguments, ``[trx_id, medio_pago, monto, detalle]`` as detailed in `PuntoPagos - Manual Técnico (REST API) v0.99, p. 3`.
    
    >>> from decimal import Decimal
    >>> from puntopagos.request import PuntopagosRequest
    >>> request = PuntopagosRequest(key='API=KEY', secret='API-SECRET')
    >>> response = request.create(trx_id='123', medio_pago='3', monto=Decimal('2000'), detalle='Foo bar product')

Note the ``monto`` is a Decimal from built-in module decimal.


Retrieving the status of a transaction
======================================

To retrieve a transaction's status, you need 3 arguments ``[trx_id, monto, token]`` as detailed in `PuntoPagos - Manual Técnico (REST API) v0.99, p. 7`.

    >>> response = request.status(trx_id='123', monto=Decimal('2000'), token='ABF56SDCL2345')


PuntopagosResponse class
========================

The create and status method both returns a PuntopagosResponse instance. This class provide several attributes for understanding the response of puntopagos.

For instance, if you don't provide a correct combination between ``trx_id``, ``monto`` and ``token`` for a status request, puntopagos will return a `400 Bad Request` response. You can check the ``complete``, if ``False`` then ``http_error`` exists and contains the http error code.

    >>> response = request.status(trx_id='123', monto=Decimal('2000'), token='ABF56SDCL2345')
    >>> response.complete
    False
    >>> response.http_error
    400

In case the response is success you will have an immutable attribute ``_data`` for the info retrieved by puntopagos, and a get_data() method for a ``dict`` with the same information.

    >>> response = request.status(trx_id='79', monto=Decimal('15000'), token='LY26HNR6XNG8KN9W')
    >>> response.complete
    True
    >>> response.get_data()
    {u'medio_pago': u'3', u'codigo_autorizacion': u'281172', u'medio_pago_descripcion': u'WebPay Transbank', u'tipo_pago': None, u'respuesta': u'00', u'monto': Decimal('15000.00'), u'num_cuotas': 0, u'tipo_cuotas': u'Sin Cuotas', u'fecha_aprobacion': u'2012-01-19T17:07:47', u'primer_vencimiento': None, u'numero_operacion': u'6998364387', u'token': u'LY26HNR6XNG8KN9W', u'trx_id': u'79', u'error': None, u'numero_tarjeta': u'6623', u'valor_cuota': 0}


Puntopagos known codes
======================

  ================  =================================
  meaning           ``respuesta``
  ================  =================================
  created           00 (without ``codigo_autorizacion``)
  authorized        00
  incomplete        6
  payment rejected  1
  invalid           99
  ================  =================================
