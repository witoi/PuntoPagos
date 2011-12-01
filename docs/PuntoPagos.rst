Rest API
--------

  =================== ====== =================== ==================================== =========
  Función             Método Headers             Contenido                            Respuesta
  =================== ====== =================== ==================================== =========
  transaccion/crear   POST   Fecha, Autorizacion trx_id, medio_pago, monto, detalle*  respuesta, token, trx_id, monto, error*
  transaccion/<token> GET    Fecha, Autorizacion                                      respuesta, token, trx_id*, medio_pago*, monto*, fecha_aprobacion*, numero_tarjeta*, num_cuotas*, tipo_cuotas*, valor_cuota*, primer_vencimiento*, numero_operacion*, codigo_autorizacion*, error*
  =================== ====== =================== ==================================== =========


Peticiones al comercio
----------------------

  ================= ====== =================== ============= =========
  URL               Método Headers             Contenido     Respuesta
  ================= ====== =================== ============= =========
  url_notificacion  POST   Fecha, Autorizacion               token, trx_id, medio_pago, monto, fecha_aprobacion, numero_tarjeta, num_cuotas, tipo_cuotas, valor_cuota, primer_vencimiento, numero_operacion, codigo_autorizacion  respuesta, token, error*
  ================= ====== =================== ============= =========


Redirecciones al usuario
------------------------

  =========================================== ======
  URL                                         Método
  =========================================== ======
  <**putopago**>/transaccion/procesar/<token> GET
  <**comercio**>/url_exito/<token>            GET
  <**comercio**>/url_fracaso/<token>          GET
  =========================================== ======


Simbología:
...........

 ``*``: opcional

Tipos de las variables del contenido(en Python)(deducidos de los ejemplos):
...........................................................................

 - **codigo_autorizacion**: string
 - **detalle**: string?
 - **error**: string?
 - **fecha_aprobacion**: string (yyyy-MM-ddTHH:mm:ss)
 - **medio_pago**: string (con código segun tabla)
 - **monto**: Decimal, con dos decimales
 - **num_cuotas**: ?
 - **numero_operacion**: string
 - **numero_tarjeta**: ?
 - **primer_vencimiento**: ?
 - **respuesta**: string(con código segun tabla)
 - **tipo_cuotas**: ?
 - **token**: string
 - **trx_id**: int
 - **valor_cuota**: ?
