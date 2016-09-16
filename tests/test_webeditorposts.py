import json
import unittest

from bs4 import BeautifulSoup
import datetime

from knowledge_repo import KnowledgeRepository, KnowledgePost
from knowledge_repo.app.app import db_session
from knowledge_repo.app.models import User, Post, Tag


class WebEditorPostTest(unittest.TestCase):
    """The test class for webeditor posts."""

    @classmethod
    def setUpClass(cls):
        """Set up the WebEditor Test Class.

        Create a webpost and a testuser
        """
        cls.repo = KnowledgeRepository.for_uri('sqlite:///:memory::test_posts', auto_create=True)
        cls.repo.config.editors = ['test_knowledge_editor']
        cls.app = cls.repo.get_app(config='tests/config_server.py')
        cls.app.config['AUTH_USERNAME_REQUEST_HEADER'] = 'user_header'
        cls.app.config['DEBUG'] = True
        cls.client = cls.app.test_client()

        cls.post_path = 'webeditor/misc/Test_Webeditor_Functionality'
        kp = KnowledgePost(cls.post_path)

        headers = {'title': 'Test Webeditor Functionality',
                   'authors': ['webeditor_test_user'],
                   'project': 'test_project',
                   'tldr': 'This is the test tldr for the webpost.',
                   'created_at': datetime.date.today(),
                   'updated_at': datetime.date.today()}
        md = 'Test Text'
        kp.write(md=md, headers=headers)
        cls.repo.add(kp)

        with cls.app.app_context():
            post = Post()
            db_session.add(post)
            post.update_metadata_from_kp(kp)
            db_session.commit()

            cls.post_id = post.id

    def test01_webeditor_route(self):
        """Test the /webposts route.

        This will need to test the security as well.
        The user 'Knowledge Default; is able to see all webposts,
        whereas 'Test User' should only see posts they've authored
        """

        with self.app.app_context():
            posts = db_session.query(Post).all()
            rv = self.client.get('/webposts', headers={'user_header': 'test_knowledge_editor'})

            assert rv.status == '200 OK'

            data = rv.data.decode('utf-8')
            soup = BeautifulSoup(data, 'html.parser')

            table_rows = soup.findAll("tr")

            # Subtract one for the header of the table
            assert len(table_rows) - 1 == len(posts)

            rv = self.client.get('/webposts', headers={'user_header': 'webeditor_test_user'})

            data = rv.data.decode('utf-8', 'html.parser')
            soup = BeautifulSoup(data, 'html.parser')
            table_rows = soup.findAll("tr")

            assert len(table_rows) - 1 == 1

    def test02_test_edit_form(self):
        """Test editing a webpost.

        Click on the edit button on the /webeditorpost route
        And ensure that the new route has the form fields
        filled out with the correct values
        """

        rv = self.client.get('/posteditor?post_id={}'.format(self.post_id))
        assert rv.status == "200 OK"
        data = rv.data.decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')

        with self.app.app_context():

            kp = self.repo.post(self.post_path)
            headers = kp.headers

            title = soup.findAll("input", {"id": "post_title"})[0]
            assert title['value'] == headers['title']

            # project = soup.findAll("input", {"id": "post_project"})[0]
            # assert project['value'] == post.project

            created_at = soup.findAll("input", {"id": "post_created_at"})[0]
            assert created_at['value'] == headers['created_at'].strftime('%Y-%m-%d')

            updated_at = soup.findAll("input", {"id": "post_updated_at"})[0]
            assert updated_at['value'] == headers['updated_at'].strftime('%Y-%m-%d')

            # TODO this now is populated by a "select"
            # author = soup.findAll("input", {"id": "post_author"})[0]
            # assert author['value'] == post.authors[0].username

            # feed_image = soup.findAll("input", {"id": "post_image_feed"})[0]
            # TODO(nikki_ray): For some reason the feed_image isn't being parsed
            # correctly
            # assert feed_image
            # assert feed_image['value']

            text = soup.findAll("textarea", {"id": "post_text"})[0]
            assert text.text.strip() == kp.read(headers=False).strip()

    def test03_test_save_button(self):
        """Test the save button on the webeditor form.

        Change the post text and make sure that
        the relevant field is updated in the db
        """
        new_post_text = "Here is the new post_text"

        with self.app.app_context():
            post = (db_session.query(Post)
                              .filter(Post.id == self.post_id)
                              .first())

            str_created_at = datetime.datetime.strftime(post.created_at, '%Y-%m-%d')
            str_updated_at = datetime.datetime.strftime(post.updated_at, '%Y-%m-%d')

            post_json_object = {
                'title': post.title,
                'project': post.project,
                'feed_image': "",  # TODO where do we store this?
                'tags': "",  # TODO pass tags
                'tldr': post.tldr,
                'status': post.status.value,
                'created_at': str_created_at,
                'updated_at': str_updated_at,
                'author': [auth.username for auth in post.authors],
                'markdown': new_post_text
            }

            url = "/save_post?post_id=" + str(post.id)
            rv = self.client.post(url,
                                  data=json.dumps(post_json_object),
                                  content_type='application/json')
            assert rv.status == "200 OK"

            kp = self.repo.post(self.post_path)

            assert kp.read(headers=False).strip() == new_post_text

    def test04_test_review_button(self):
        """Test the review functionality.

        Ensure that submitting a post for review changes the status
        And that going back to the form editor changes the button text
        And a review comment area is added
        """
        rv = self.client.post('/submit?post_id={}'.format(self.post_id),
                              data=json.dumps({'post_reviewers': 'test_post_reviewers'}),
                              content_type='application/json')

        assert rv.status == "200 OK"

        rv = self.client.get('/posteditor?post_id={}'.format(self.post_id))

        assert rv.status == "200 OK"

        data = rv.data.decode("utf-8")
        soup = BeautifulSoup(data, 'html.parser')

        comments_textarea = soup.findAll("textarea", {"id": "comment-text"})
        assert comments_textarea

        btn_in_review = soup.findAll("button", {"id": "btn_in_review"})
        assert btn_in_review and btn_in_review[0].text.strip() == "In Review Phase"

        with self.app.app_context():
            post = (db_session.query(Post)
                              .filter(Post.id == self.post_id)
                              .first())
            assert post.status == self.repo.PostStatus.SUBMITTED

    def test05_test_author_can_publish_button(self):
        """Test changing the permission for authors.

        Clicking the author_can_publish checkbox
        should change the relevant field in the db
        """
        url = "/author_publish?post_id=" + str(self.post_id)
        rv = self.client.post(url)

        assert rv.status == "200 OK"
        with self.app.app_context():
            post = (db_session.query(Post)
                              .filter(Post.id == self.post_id)
                              .first())
            kp = self.repo.post(post.path)
            assert kp.is_accepted is True

    def test06_test_publish_button(self):
        """Test the publish functionality.

        Test that clicking the publish button changes the status
        and the button text.

        Test that clicking it again changes the status back
        and the button text
        """
        # test that clicking the publish button changes the status
        rv = self.client.post('/publish_post?post_id={}'.format(self.post_id))

        assert rv.status == "200 OK"
        with self.app.app_context():
            post = (db_session.query(Post)
                              .filter(Post.id == self.post_id)
                              .first())
            assert post.status == self.repo.PostStatus.PUBLISHED
            rv = self.client.get('/posteditor?post_id={}'.format(self.post_id))

            assert rv.status == "200 OK"

            data = rv.data.decode("utf-8")
            soup = BeautifulSoup(data, 'html.parser')

            # go to the posteditor form to check the button
            btn_publish = soup.findAll("button", {"id": "btn_publish"})
            assert btn_publish and btn_publish[0].text.strip() == "Unpublish"

            rv = self.client.post('/unpublish_post?post_id={}'.format(self.post_id))
            assert rv.status == "200 OK"

            post = (db_session.query(Post)
                              .filter(Post.id == self.post_id)
                              .first())

            assert post.status == self.repo.PostStatus.UNPUBLISHED

            rv = self.client.get('/posteditor?post_id={}'.format(self.post_id))

            assert rv.status == "200 OK"

            data = rv.data.decode("utf-8")
            soup = BeautifulSoup(data, 'html.parser')

            # go to the posteditor form to check the button
            btn_publish = soup.findAll("button", {"id": "btn_publish"})
            assert btn_publish and btn_publish[0].text.strip() == "Publish"

    def test07_test_delete_button(self):
        """Test webpost deletion."""
        rv = self.client.get('/delete_post?post_id={}'.format(self.post_id))
        assert rv.status == "200 OK"

        with self.app.app_context():
            post = (db_session.query(Post)
                              .filter(Post.id == self.post_id)
                              .first())
            assert not post

    @classmethod
    def tearDownClass(cls):
        """Remove the user we created."""
        pass

if __name__ == '__main__':
    unittest.main()
