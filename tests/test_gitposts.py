import unittest

from BeautifulSoup import BeautifulSoup
from sqlalchemy import and_

from knowledge_repo import KnowledgeRepository
from knowledge_repo.app.proxies import db_session
from knowledge_repo.app.models import Post


class GitPostTest(unittest.TestCase):
    def setUp(self):
        self.repo = KnowledgeRepository.for_uri('tests/test_repo', auto_create=True)
        self.app = self.repo.get_app(config='tests/config_server.py')
        self.client = self.app.test_client()

        with self.app.app_context():
            # for this test, pick one post
            post = (db_session.query(Post)
                              .filter(Post.is_published)
                              .first())

            GitPostTest.post_path = post.path

    def test01_check_render_route(self):
        """
        Check gitpost path will render in /render?markdown=
        """
        render_url = '/render?markdown='
        rv = self.client.get(render_url + GitPostTest.post_path)
        assert rv.status == "200 OK"

    @unittest.skip("Post stats formatting changed. Test needs to be updated.")
    def test02_check_post_stats(self):
        """
        Make sure pageview, distinct viewers correct for gitpost
        """
        render_url = '/render?markdown='
        rv = self.client.get(render_url + GitPostTest.post_path)

        data = rv.data.decode('utf-8')
        soup = BeautifulSoup(data)

        # we'll check the post_stats of the post by computing them
        # and ensuring that the upper-right-hand text is correct

        icon = soup.findAll("div", {"id": "pageview_stats"})
        pageviews_str = icon[0].text

        post = (db_session.query(Post)
                          .filter(Post.path == GitPostTest.post_path)
                          .first())
        pageviews = post.get_pageviews
        distinct_viewers = post.get_distinct_views

        db_pageviews_str = "Viewed {pageviews} times by {distinct_viewers} different users.".format(**locals())

        assert db_pageviews_str == pageviews_str

    def test03_check_post_metadata(self):
        """
        Check gitpost metadata
        """
        render_url = '/render?markdown='
        rv = self.client.get(render_url + GitPostTest.post_path)

        data = rv.data.decode('utf-8')
        soup = BeautifulSoup(data)
        metadata = soup.findAll("p", {"id": "metadata"})

        assert metadata

        metadata = metadata[0]
        children = metadata.contents

        # strip out the \n
        children = [c for c in children if c != ' ' and c != '\n']

        for (i, child) in enumerate(children):
            try:
                metadata_elem = child.findAll("strong")
                assert children[i + 1].contents
            except:
                pass

if __name__ == '__main__':
    unittest.main()
