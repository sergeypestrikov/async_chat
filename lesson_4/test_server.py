import unittest
from lesson_3.server import get_client_msg
from lesson_3.variables import ACTION, ACCOUNT_NAME, RESPONSE, PRESENCE, TIME, USER, ERROR


class TestGetClientMsg(unittest.TestCase):

    error = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    ok = {RESPONSE: 200}
# не гость
    def test_not_guest(self):
        self.assertNotEqual(get_client_msg(
            {ACTION: PRESENCE,
             TIME: 1.1,
             USER: {ACCOUNT_NAME: 'Guest'}
             }
        ), self.ok)

# нет действия
    def test_no_action(self):
        self.assertEqual(get_client_msg(
            {TIME: 1.1,
             USER: {ACCOUNT_NAME: 'Guest'}
            }
        ), self.error)

# проверка запроса
    def test_check_request(self):
        self.assertEqual(get_client_msg(
            {ACTION: PRESENCE,
             TIME: 1.1,
             USER: {ACCOUNT_NAME: 'Guest'}
             }
        ), self.ok)


if __name__ == '__main__':
    unittest.main()
