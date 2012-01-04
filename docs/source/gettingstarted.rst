Getting started
###############

Create a transaction
--------------------

First, you need an api key and an api secret provided by puntopagos.

Then instanciate a PuntoPagoRequest object

.. autoclass:: puntopagos.PuntoPagoRequest

For create a transaction the PuntoPagoRequest class provide the create method.

.. automethod:: puntopagos.PuntoPagoRequest.create

Example
+++++++

    >>> config = {'key': APIKEY, 'secret': APISECRET}
    >>> request = PuntoPagoRequest(config=config)
    >>> response = request.create(trx_id='1', medio_pago='3', monto=100.0)
    >>> response.complete
    True
    >>> response.token
    'LXAAYDOMUAVUBKG0'
    >>> response.redirection_url
    'http://www.puntopagos.com/transaccion/procesar/LXAAYDOMUAVUBKG0'   

Response is an instance of PuntoPagoCreateResponse

.. autoclass:: puntopagos.PuntoPagoCreateResponse
   :members:


Retrieving transaction status
-----------------------------

For retrieving a transaction status the PuntoPagoRequest class provide status method.

.. automethod:: puntopagos.PuntoPagoRequest.status

Example
+++++++
    >>> request = PuntoPagoRequest(config=config)
    >>> response = request.status(token='LXAAYDOMUAVUBKG0', monto=100.0, trx_id='1')
    >>> response.complete
    True

Response is an instance of PuntoPagoStatusResponse

.. autoclass:: puntopagos.PuntoPagoStatusResponse
   :members:
   
