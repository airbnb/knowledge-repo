import unittest

from knowledge_repo import KnowledgeRepository


class ClusterTest(unittest.TestCase):

    def setUp(self):
        self.repo = KnowledgeRepository.for_uri('tests/test_repo', auto_create=True)
        self.app = self.repo.get_app(config='tests/config_server.py').test_client()
        self.headers = {}
#         username_request_header = app.config.get("USERNAME_REQUEST_HEADER")
#         self.knowledge_username = 'clusters_test_user'
#         self.headers = {
#             username_request_header: self.knowledge_username
#         }
#         engine.echo = False

    def test01_test_cluster_folder(self):
        """
        test the cluster folder view
        """
        folder_alpha = '/cluster?group_by=folder&sort_by=alpha&sort_asc=1'
        folder_num = '/cluster?group_by=folder&sort_by=count'

        alpha_response = self.app.get(folder_alpha, headers=self.headers)
        assert (alpha_response.status == '200 OK')

        num_response = self.app.get(folder_num, headers=self.headers)
        assert (num_response.status == '200 OK')

    def test02_test_cluster_author(self):
        """
        test the cluster author view
        """
        author_alpha = '/cluster?group_by=author&sort_by=alphas&sort_asc=1'
        author_num = '/cluster?group_by=author&sort_by=count'

        alpha_response = self.app.get(author_alpha, headers=self.headers)
        assert (alpha_response.status == '200 OK')

        num_response = self.app.get(author_num, headers=self.headers)
        assert (num_response.status == '200 OK')

    def test03_test_cluster_tags(self):
        """
        test the cluster tags view
        """
        tags_alpha = '/cluster?group_by=tags&sort_by=alphas&sort_asc=1'
        tags_num = '/cluster?group_by=tags&sort_by=count'

        alpha_response = self.app.get(tags_alpha, headers=self.headers)
        assert (alpha_response.status == '200 OK')

        num_response = self.app.get(tags_num, headers=self.headers)
        assert (num_response.status == '200 OK')


if __name__ == '__main__':
    unittest.main()
