import unittest
from bs4 import BeautifulSoup

from knowledge_repo import KnowledgeRepository
from knowledge_repo.app.app import db_session
from knowledge_repo.app.models import PageView, Comment, Vote
from sqlalchemy import func


class FeedTest(unittest.TestCase):

    def setUp(self):
        self.repo = KnowledgeRepository.for_uri('tests/test_repo', auto_create=True)
        self.repo_app = self.repo.get_app(config='tests/config_server.py')
        self.app = self.repo_app.test_client()
        self.headers = {}
        self.data = []

    def test01_ten_posts(self):
        """
        test to make sure we have 10 posts
        test helper functions to make sure that the likes, pageviews, comments
        and metadata are correct
        """
        rv = self.app.get("/feed", headers=self.headers)
        assert (rv.status == "200 OK")
        data = rv.data.decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')
        all_posts = soup.findAll('div', {'class': 'row feed-post'})
        self.data = all_posts

    def test02_test_link_to_post(self):
        """
        For the posts, test to make sure that a link exists
        and that hitting that link gives a 200
        """
        posts = self.data

        for post in posts:
            title_link = post.findAll("a")[0]
            title_href = title_link['href']
            title_text = title_link.string

            assert(len(title_href))
            assert(self.app.get(title_href, headers=self.headers).status == "200 OK")

    def test03_test_post_stats(self):
        """
        Test post_stats
        """
        posts = self.data

        for post in posts:
            title_link = post.findAll("a")[0]
            title_href = title_link['href']
            find_equal = title_href.find("=")
            page_id = title_href[find_equal + 1:]

            # get pageviews
            # TODO: refine this for latest pageview model
            pageviews = post.findAll(
                "i", id=lambda x: x and x.startswith('tooltip-pageviews'))
            assert (len(pageviews) == 1)
            pageview_value = int(pageviews[0].text)
            pageview_query = (db_session.query(func.count(PageView.id))
                              .filter(PageView.page == page_id)
                              .scalar())
            assert (pageview_query == pageview_value + 1)
            # get likes
            likes = post.findAll(
                "i", id=lambda x: x and x.startswith('tooltip-likes'))
            assert (len(likes) == 1)

            likes_value = int(likes[0].text)
            likes_query = (db_session.query(Vote)
                           .filter(Vote.page == page_id)
                           .all())
            assert (likes_value == len(likes_query))

            # get comments
            comments = post.findAll(
                "i", id=lambda x: x and x.startswith('tooltip-comments'))
            assert (len(comments) == 1)

            comments_values = int(comments[0].text)
            comments_query = (db_session.query(Comment)
                              .filter(Comment.post_id == page_id)
                              .all())
            assert (comments_values == len(comments_query))

    def test04_test_post_metadata(self):
        """
        Test post metadata
        """
        posts = self.data

        for post in posts:
            author = post.findAll('span', {'class': 'feed-authors'})
            assert author

            date = post.findAll('span', {'class': 'feed-dates'})
            assert date

            tags = post.findAll('span', {'class': 'feed-tags'})
            assert tags

            image = post.findAll('img')
            assert image

    def test05_test_bogus_filter(self):
        """
        Test that a bogus filter returns 0 posts
        """
        url = '/feed?filters=bogus%20filter'
        rv = self.app.get(url, headers=self.headers)

        assert rv.status == '200 OK'

        data = rv.data.decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')
        all_posts = soup.findAll('div', {'class': 'row feed-post'})
        assert not all_posts

    def test06_real_filter(self):
        """
        Test that search filter "template" returns the three posts
        """
        url = '/feed?filters=template'
        rv = self.app.get(url, headers=self.headers)

        assert rv.status == '200 OK'

        data = rv.data.decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')
        all_posts = soup.findAll('div', {'class': 'row feed-post'})
        assert len(all_posts) == 3, "Expected 3 posts, found {}".format(len(all_posts))

if __name__ == '__main__':
    unittest.main()
