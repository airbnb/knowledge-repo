import unittest

from bs4 import BeautifulSoup
from sqlalchemy import and_

from knowledge_repo import KnowledgeRepository
from knowledge_repo.app.proxies import db_session
from knowledge_repo.app.models import Post


class PostTest(unittest.TestCase):

    def setUp(self):
        self.repo = KnowledgeRepository.for_uri('tests/test_repo', auto_create=True)
        self.app = self.repo.get_app(config='tests/config_server.py')
        self.client = self.app.test_client()

        with self.app.app_context():
            # for this test, pick one post
            post = (db_session.query(Post)
                              .filter(Post.is_published)
                              .first())
            self.post_id = post.id
            self.post_rendered_url = '/post/{}'.format(post.path)

    def test01_check_render_route(self):
        """
        Check post path will render in /post/<path>
        """
        rv = self.client.get(self.post_rendered_url)
        assert rv.status == "200 OK"

    def test02_check_post_stats(self):
        """
        Make sure pageview, distinct viewers correct for post
        """
        rv = self.client.get(self.post_rendered_url)

        data = rv.data.decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')

        # we'll check the post_stats of the post by computing them
        # and ensuring that the upper-right-hand text is correct
        icon = soup.findAll("div", {"id": "pageview_stats"})
        pageviews_str = icon[0].text.strip()

        with self.app.app_context():
            post = (db_session.query(Post)
                              .filter(Post.id == self.post_id)
                              .first())
            distinct_viewers = post.view_user_count
            pageviews = post.view_count

        db_pageviews_str = "Viewed {pageviews} times by {distinct_viewers} different users".format(**locals())

        assert db_pageviews_str == pageviews_str, "'{}' is not '{}'!".format(db_pageviews_str, pageviews_str)

    def test03_check_post_metadata(self):
        """
        Check post metadata
        """
        rv = self.client.get(self.post_rendered_url)

        data = rv.data.decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')
        metadata = soup.findAll("div", {"class": "metadata"})

        assert metadata

        metadata = metadata[0]
        children = metadata.contents

        # strip out the \n
        children = [c for c in children if c != ' ' and c != '\n']

        for (i, child) in enumerate(children):
            try:
                metadata_elem = child.findAll("span")
                assert children[i + 1].contents
            except:
                pass

if __name__ == '__main__':
    unittest.main()
