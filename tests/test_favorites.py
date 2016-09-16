import unittest
from bs4 import BeautifulSoup
from sqlalchemy import and_

from knowledge_repo import KnowledgeRepository
from knowledge_repo.app.models import User, Vote, Post
from knowledge_repo.app.app import db_session


class FavoriteTest(unittest.TestCase):

    def setUp(self):
        self.repo = KnowledgeRepository.for_uri('tests/test_repo', auto_create=True)
        self.repo_app = self.repo.get_app(config='tests/config_server.py')
        self.app = self.repo_app.test_client()
        self.headers = {}

        self.knowledge_username = 'favorite_test_user'
        username_request_header = self.repo_app.config.get(
            "AUTH_USERNAME_REQUEST_HEADER")
        self.headers = {
            username_request_header: self.knowledge_username
        }

    def test_like_and_unlike_a_post(self):
        """
        Like and then unlike a post
        """
        with self.repo_app.app_context():
            post = (db_session.query(Post)
                    .filter(Post.is_published)
                    .first())

            old_likes = (db_session.query(Vote)
                         .filter(Vote.object_id == post.id)
                         .filter(Vote.object_type == 'post')
                         .all())
            rv = self.app.get("/like?post_id=" + str(post.id), headers=self.headers)

            assert rv.status == '200 OK', post.path + rv.status

            new_likes = (db_session.query(Vote)
                         .filter(Vote.object_id == post.id)
                         .filter(Vote.object_type == 'post')
                         .all())

            assert len(old_likes) + 1 == len(new_likes)

            # assert that if you re-like the page, the number of likes doesn't
            # change
            rv = self.app.get("/like?post_id=" + str(post.id), headers=self.headers)

            assert rv.status == '200 OK'

            like_again = (db_session.query(Vote)
                          .filter(Vote.object_id == post.id)
                          .filter(Vote.object_type == 'post')
                          .all())
            assert len(like_again) == len(new_likes)

            """
            Let's unlike it again
            """
            old_likes = (db_session.query(Vote)
                         .filter(Vote.object_id == post.id)
                         .filter(Vote.object_type == 'post')
                         .all())
            rv = self.app.get("/unlike?post_id=" + str(post.id), headers=self.headers)

            assert rv.status == '200 OK'

            new_likes = (db_session.query(Vote)
                         .filter(Vote.object_id == post.id)
                         .filter(Vote.object_type == 'post')
                         .all())
            assert len(new_likes) == len(old_likes) - 1

    def test_favorites(self):
        """
        test the favorites route, and make sure the number of posts = number of votes with that user_id
        """
        with self.repo_app.app_context():
            rv = self.app.get("/favorites", headers=self.headers)
            assert rv.status == "200 OK"
            data = rv.data.decode('utf-8')
            soup = BeautifulSoup(data, 'html.parser')
            all_posts = soup.findAll(
                'div', {'class': 'row row-space-4 panel feed-post'})

            user = (db_session.query(User)
                    .filter(User.username == self.knowledge_username)
                    .first())
            votes = (db_session.query(Vote)
                     .filter(Vote.user_id == user.id)
                     .all())
            assert len(votes) == len(all_posts)


if __name__ == '__main__':
    unittest.main()
