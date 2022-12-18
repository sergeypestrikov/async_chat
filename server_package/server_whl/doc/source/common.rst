Common package
=================================================

Пакет общих утилит, использующихся в разных модулях проекта.

Скрипт wrapper.py
---------------

.. automodule:: common.wrapper
	:members:

Скрипт descriptor.py
---------------------

.. autoclass:: common.descriptor.Port
    :members:

Скрипт errors.py
---------------------

.. autoclass:: common.errors.ServerError
   :members:

Скрипт metaclasses.py
-----------------------

.. autoclass:: common.metaclasses.ServerVerifier
   :members:

.. autoclass:: common.metaclasses.ClientVerifier
   :members:

Скрипт utils.py
---------------------

common.utils. **get_msg** (client)


Функция приёма сообщений от удалённых компьютеров. Принимает сообщения JSON,
декодирует полученное сообщение и проверяет что получен словарь.

common.utils. **send_msg** (sock, message)


Функция отправки словарей через сокет. Кодирует словарь в формат JSON и отправляет через сокет.


Скрипт variables.py
---------------------

Содержит глобальные переменные проекта.