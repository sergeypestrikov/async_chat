import unittest
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, PRESENCE, TIME, USER, ERROR
from client import create_presence, answer_process


class TestClient(unittest.TestCase):
    # проверка запроса
    def test_check_request(self):
        check = create_presence()
        check[TIME] = 1.1

        self.assertEqual(check, {
            ACTION: PRESENCE,
            TIME: 1.1,
            USER: {ACCOUNT_NAME: 'Guest'}
        })

    # проверка ответа на 200
    def test_check_200(self):
        self.assertEqual(answer_process({RESPONSE: 200}), '200: OK')

    # проверка ответа на 400
    def test_check_400(self):
        self.assertEqual(answer_process({RESPONSE: 400, ERROR: 'Bad Request'}), '400: BAD REQUEST')


if __name__ == '__main__':
    unittest.main()