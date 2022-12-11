import unittest
import json
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, PRESENCE, TIME, USER, ERROR, ENCODING
from common.utils import get_msg, send_msg

# Тестирование отправки и получения
class TestSocket:

    # Создаем словарь для тестовой отправки
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_msg = None
        self.recv_msg = None

    # Тест отправки в сокет - кодировка и сохранение
    def send(self, send_to_sock):
        test_json_msg = json.dumps(self.test_dict)
        self.encoded_msg = test_json_msg.encode(ENCODING)
        self.recv_msg = send_to_sock

    # Получение данных из сокета
    def recv(self):
        test_json_msg = json.dumps(self.test_dict)
        return test_json_msg.encode(ENCODING)


class TestUtils(unittest.TestCase):
    test_sender = {
        ACTION: PRESENCE,
        TIME: 1.1,
        USER: {ACCOUNT_NAME: 'Guest'}
    }
    test_receiver_ok = {RESPONSE: 200}
    test_receiver_error = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    # Тест непосредственной отправки
    def test_send_msg(self):
        test_socket = TestSocket(self.test_sender)
        send_msg(test_socket, self.test_sender)
        self.assertEqual(test_socket.encoded_msg, test_socket.recv_msg)
        with self.assertRaises(Exception):
            send_msg(test_socket, test_socket)

    # Тест на получение сообщений
    def test_get_msg(self):
        test_socket_ok = TestSocket(self.test_receiver_ok)
        test_socket_error = TestSocket(self.test_receiver_error)
        self.assertEqual(get_msg(test_socket_ok), self.test_receiver_ok)
        self.assertEqual(get_msg(test_socket_error), self.test_receiver_error)


if __name__ == '__main__':
    unittest.main()