import unittest

from sqlalchemy import and_

from knowledge_repo import KnowledgeRepository
from knowledge_repo.app.models import Post, Subscription, Email, User
from knowledge_repo.app.utils.emails import send_internal_error_email, send_subscription_emails, send_comment_email, send_review_email
from knowledge_repo.app.proxies import db_session


class EmailTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.repo = KnowledgeRepository.for_uri('tests/test_repo', auto_create=True)
        self.app = self.repo.get_app(config='tests/config_server.py')
        self.app.repository.config.editors = ['knowledge_editors']
        self.client = self.app.test_client()

        self.knowledge_username = 'email_test_user'
        # this creates a user
        with self.app.app_context():
            User(username=self.knowledge_username)

            web_post = Post(title='test_webpost')
            git_post = (db_session.query(Post)
                        .first())

            db_session.add(web_post)
            web_post.authors = ['test_author']

            git_post.tags = ['test_tag']

            db_session.commit()

            self.web_post_id = web_post.id
            self.git_post_id = git_post.id

    def test01_review_email(self):
        """ Test Review Email """
        commenter = 'test_commenter'
        comment_text = 'this is a test for review email'
        with self.app.app_context():
            with self.app.config['mail'].record_messages() as outbox:
                with self.app.test_request_context():
                    send_review_email(commenter=commenter,
                                      comment_text=comment_text,
                                      post_id=self.web_post_id)

            web_post = (db_session.query(Post)
                        .filter(Post.id == self.web_post_id)
                        .first())
            assert len(outbox) == 1
            assert outbox[0].subject == "Someone reviewed your web post!"
            # TODO assert format_commenter(commenter) in outbox[0].body
            assert comment_text in outbox[0].body
            assert web_post.title in outbox[0].body

    def test02_comment_email(self):
        """ Test Comment Email """
        with self.app.app_context():
            with self.app.config['mail'].record_messages() as outbox:
                with self.app.test_request_context():
                    commenter = 'test_commenter'
                    comment_text = 'this is a test for comment email'
                    send_comment_email(commenter=commenter,
                                       comment_text=comment_text,
                                       post_id=self.git_post_id)

            git_post = (db_session.query(Post)
                        .filter(Post.id == self.git_post_id)
                        .first())
            assert len(outbox) == 1
            assert outbox[0].subject == "Someone commented on your post!"
            # assert format_commenter(commenter) in outbox[0].body
            assert comment_text in outbox[0].body
            assert git_post.title in outbox[0].body

    def test03_internal_error_email(self):
        """ Test Internal Error Email """
        with self.app.app_context():
            with self.app.config['mail'].record_messages() as outbox:
                with self.app.app_context():
                    subject_line = 'test subject line'
                    send_internal_error_email(subject_line=subject_line)

                    assert len(outbox) == 1
                    assert outbox[0].subject == subject_line

                    # make sure that internal emails are sent to the editors
                    # TODO does this make sense for open source?
                    username_to_email = self.app.repository.config.username_to_email
                    knowledge_editors = self.app.repository.config.editors
                    editor_emails = [username_to_email(
                        editor) for editor in knowledge_editors]
                    assert sorted(outbox[0].recipients) == sorted(editor_emails)
                    assert 'This email is for internal debugging only.' in outbox[
                        0].body

    def test04_subscription_email(self):
        """ Test Subscription Email """
        # Subscribe to a tag from gitpost and webpost Note, don't send
        # a request to do it so that create_index() will happen later,
        # as it is before_first_request
        with self.app.app_context():
            db_session.expire_on_commit = False
            git_post = (db_session.query(Post)
                        .filter(Post.id == self.git_post_id)
                        .first())

            user = User(username=self.knowledge_username)
            if user.id is None:
                db_session.commit()
            user_id = user.id

            # grab the first tag from the post
            tag_id = git_post.tags[0].id
            post_id = git_post.id

            subscription = Subscription(user_id=user_id, object_type='tag',
                                        object_id=tag_id)
            db_session.add(subscription)
            db_session.commit()

            # Run a request, which should trigger a subscription email for
            # tag_to_subscribe
            with self.app.config['mail'].record_messages() as outbox:
                with self.app.app_context():
                    send_subscription_emails(git_post)

            emails_sent = (db_session.query(Email)
                           .filter(and_(Email.object_id == post_id,
                                        Email.user_id == user_id,
                                        Email.trigger_id == tag_id,
                                        Email.trigger_type == 'subscription'))
                           .all())

            # There should be exactly 1 email sent to the user for the target post
            # Check EmailSent records
            assert len(outbox) == 1, 'One subscription email should be actually sent'
            assert len(
                emails_sent) == 1, 'One subscription email should recorded as sent'
            # Check outbox of messages
            assert len(
                outbox[0].bcc) == 1, 'One subscription email should be actually sent to one user'
            assert "A knowledge post was just posted under tag" in outbox[0].body, 'Email should be the subscription email'

            username_to_email = self.app.repository.config.username_to_email
            assert outbox[0].bcc[0] == username_to_email(self.knowledge_username)

if __name__ == '__main__':
    unittest.main()
