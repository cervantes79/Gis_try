try:
    import app
    import unittest
except Exception as e:
    print("Modules are missing", repr(e))

charset = "text/html; charset=utf-8"


def check_response(route):
    return app.app.test_client().get(route).status_code


def check_content(route):
    return app.app.test_client().get(route).content_type


def check_data(route):
    print(route, len(app.app.test_client().get(route).data))
    return len(app.app.test_client().get(route).data) > 0


class TestAddresses(unittest.TestCase):
    def test_addresses_response(self):
        self.assertEqual(check_response('/addresses'), 200)

    def test_addresses_content(self):
        self.assertEqual(check_content('/addresses'), charset)

    def test_addresses_data(self):
        self.assertTrue(check_data('/addresses'))


class TestApiAddresses(unittest.TestCase):
    def test_api_addresses_response(self):
        self.assertEqual(check_response('/api/addresses'), 200)

    def test_api_addresses_content(self):
        self.assertEqual(check_content('/api/addresses'), charset)

    def test_api_addresses_data(self):
        self.assertTrue(check_data('/api/addresses'))
