from __future__ import print_function
import unittest
import json

from bs4 import BeautifulSoup

from knowledge_repo import KnowledgeRepository
from knowledge_repo.app.models import Comment, Post, User

from knowledge_repo.app.app import db_session


class CommentTest(unittest.TestCase):

    def setUp(self):
        self.repo = KnowledgeRepository.for_uri('tests/test_repo', auto_create=True)
        self.repo_app = self.repo.get_app(config='tests/config_server.py')
        self.app = self.repo_app.test_client()

        self.knowledge_username = 'comment_test_user'
        with self.repo_app.app_context():
            user = User(username=self.knowledge_username)
            if user.id is None:
                db_session.commit()
            self.user_id = user.id
        username_request_header = self.repo_app.config.get(
            "AUTH_USERNAME_REQUEST_HEADER")
        self.headers = {
            username_request_header: self.knowledge_username
        }

    def test01_comment_on_a_post(self):
        """
        Comment on a post
        """
        with self.repo_app.app_context():
            # get the number of comments on a given post
            post = (db_session.query(Post)
                              .filter(Post.is_published)
                              .first())
            n_comments = len(db_session.query(Comment)
                                       .filter(Comment.post_id == post.id)
                                       .all())

            assert post.status == self.repo.PostStatus.PUBLISHED

            # test commenting on a post
            data = {'text': 'This is a comment'}
            rv = self.app.post('/comment?path={}'.format(post.path),
                               headers=self.headers,
                               data=json.dumps(data),
                               content_type='application/json')

            assert rv.status == '200 OK'

            assert post.status == self.repo.PostStatus.PUBLISHED

            # check that new comment exists in db
            comment_exists = (db_session.query(Comment)
                                        .filter(Comment.post_id == post.id)
                                        .filter(Comment.user_id == self.user_id)
                                        .filter(Comment.text == data['text'])
                                        .first())
            assert comment_exists

            assert post.status == self.repo.PostStatus.PUBLISHED

            # check that the number of comments rendered increased by 1
            rv = self.app.get('/render?markdown=' + post.path,
                              headers=self.headers)
            soup = BeautifulSoup(rv.data.decode('utf-8'), 'html.parser')
            comments = soup.findAll("div", {"class": "post_comment"})
            assert comments, 'comments found in '
            assert len(comments) == n_comments + 1

    def test02_delete_a_comment(self):
        """
        Delete a comment
        """

        with self.repo_app.app_context():

            # get a post
            post = (db_session.query(Post)
                              .filter(Post.is_published)
                              .first())

            # create a comment
            data = {'text': 'This is a comment'}
            rv = self.app.post('/comment?path={}'.format(post.path),
                               headers=self.headers,
                               data=json.dumps(data),
                               content_type='application/json')

            # get comment id
            comment_id = (db_session.query(Comment)
                                    .filter(Comment.post_id == post.id)
                                    .filter(Comment.user_id == self.user_id)
                                    .filter(Comment.text == data['text'])
                                    .first()).id

            # test deleting a commment
            rv = self.app.get('/delete_comment?comment_id={}'.format(comment_id),
                              headers=self.headers)
            assert rv.status == '200 OK'
            delete_comment = (db_session.query(Comment)
                                        .filter(Comment.id == comment_id)
                                        .all())
            assert not delete_comment, 'comments found after deletion'


if __name__ == '__main__':
    unittest.main()
