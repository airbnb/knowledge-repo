import unittest
from bs4 import BeautifulSoup

from knowledge_repo import KnowledgeRepository


class TableTest(unittest.TestCase):

    def setUp(self):
        self.repo = KnowledgeRepository.for_uri('tests/test_repo', auto_create=True)
        self.app = self.repo.get_app(config='tests/config_server.py').test_client()
        self.headers = {}

    def test01_table_route(self):
        """
        test table view
        """
        rv = self.app.get("/table", headers=self.headers)
        assert (rv.status == "200 OK")
        soup = BeautifulSoup(rv.data.decode('utf-8'), 'html.parser')
        post_rows = soup.findAll('tr', {'class': 'table-post'})
        for row in post_rows:
            column_ids = ['path', 'author', 'tags', 'updated_at',
                          'views', 'upvotes', 'comments', 'tldr']

            for column in column_ids:
                elem = row.findAll(
                    'td', id=lambda x: x and x.startswith(column))
                assert elem
                if column == 'path':
                    path_link = elem[0].findAll("a")[0]
                    path_href = path_link['href']
                    assert self.app.get(
                        path_href, headers=self.headers).status == "200 OK"

    def test02_table_sorts(self):
        """
        Test sorting table view
        """
        sort_by = ['Title', 'CreatedAt', 'UpdatedAt',
                   'Uniqueviews', 'Upvotes', 'Comments']
        for sort in sort_by:
            rv = self.app.get('/table?sort_by=' + sort, headers=self.headers)
            assert (rv.status == "200 OK")
            rv = self.app.get('/table?sort_by=' + sort +
                              "&sort_asc=1", headers=self.headers)
            assert (rv.status == "200 OK")


if __name__ == '__main__':
    unittest.main()
