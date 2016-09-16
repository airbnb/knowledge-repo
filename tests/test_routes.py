import unittest

from knowledge_repo import KnowledgeRepository


class RouteTest(unittest.TestCase):

    def setUp(self):
        self.repo = KnowledgeRepository.for_uri('tests/test_repo', auto_create=True)
        self.app = self.repo.get_app(config='tests/config_server.py').test_client()
        self.headers = {}

    def test01_test_index(self):
        """
        Test routing / to /feed
        """
        rv = self.app.get('/', headers=self.headers)
        # index reroutes to /feed
        assert (rv.status == "302 FOUND")

    def test02_test_health(self):
        """
        Test /health
        """
        rv = self.app.get("/health", headers=self.headers)
        assert (rv.status == "200 OK")
        assert (rv.data.decode('utf-8') == "OK")

    def test03_test_ping(self):
        """
        Test /ping
        """
        rv = self.app.get("/ping", headers=self.headers)
        assert (rv.status == "200 OK")
        assert (rv.data.decode('utf-8') == "OK")

    def test04_test_stats(self):
        """
        Test /stats
        """
        rv = self.app.get('/stats')
        assert rv.status == '200 OK'

if __name__ == '__main__':
    unittest.main()
