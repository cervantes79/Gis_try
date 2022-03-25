try:
    import load_data
    import unittest
except Exception as e:
    print("Modules are missing", repr(e))


class TestDatabaseMethods(unittest.TestCase):

    def test_get_query(self):
        query = "select True as truevalue"
        obj = [{'truevalue': 'True'}]
        self.assertTrue(load_data.get_query(query=query), obj)


class TestGetData(unittest.TestCase):
    def test_get_data(self):
        en = "5.31906738123115,56.60417303370079"
        sw = "-11.962067381231293,51.81965717678804"
        zoom = 5.51
        self.assertTrue(load_data.get_data(en=en, sw=sw, zoom=zoom), True)
