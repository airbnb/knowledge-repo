"""Test tag related functionality."""
import datetime
import json
import unittest

from knowledge_repo import KnowledgeRepository
from knowledge_repo.app.proxies import db_session
from knowledge_repo.app.models import Tag, User, Subscription, Post, assoc_post_tag


class TagsTest(unittest.TestCase):
    """The Test Class for all tag functionality."""

    def setUp(self):
        """Set up the TagsTest Class by instantiating a tag."""
        self.repo = KnowledgeRepository.for_uri('tests/test_repo', auto_create=True)
        self.app = self.repo.get_app(config='tests/config_server.py')
        self.client = self.app.test_client()

        # we'll create a tag for the purpose of tag testing
        test_run = datetime.datetime.now().strftime('%Y-%m-%d')

        with self.app.app_context():
            tag = Tag(name='test/tag_' + test_run)
            db_session.commit()
            TagsTest.tag_id = tag.id
            TagsTest.tag_name = tag.name

            # the default user is "knowledge_default"
            user = (db_session.query(User)
                    .filter(User.username == 'knowledge_default')
                    .first())

            TagsTest.user_id = user.id

            # We need an example post as well to test some of the
            # add/delete/rename functionality
            example_post = (db_session.query(Post).first())
            TagsTest.post_path = example_post.path

    def test01_test_subscribe_to_tag(self):
        """Test the subscription feature."""
        headers = {"X-InternalAuth-Username": "knowledge_default"}

        route_name = '/toggle_tag_subscription'
        tag_name = 'tag_name=' + TagsTest.tag_name
        action = 'subscribe_action=subscribe'
        full_url = '{route_name}?{tag_name}&{action}'.format(**locals())
        # check that status == 200 & the tag has been subscribed too
        rv = self.client.post(full_url, headers=headers)
        assert (rv.status == "200 OK")

        with self.app.app_context():
            subscription = (db_session.query(Subscription)
                            .filter(Subscription.object_id == TagsTest.tag_id)
                            .filter(Subscription.object_type == 'tag')
                            .first())
            assert subscription

    def test02_test_unsubscribe_to_tag(self):
        """Test the unsubscribe feature."""
        headers = {"X-InternalAuth-Username": "knowledge_default"}

        route_name = '/toggle_tag_subscription'

        with self.app.app_context():
            tag = db_session.query(Tag).first()

            tag_name = 'tag_name=' + TagsTest.tag_name
            action = 'subscribe_action=unsubscribe'
            full_url = '{route_name}?{tag_name}&{action}'.format(
                **locals())

            # check that status == 200 & the tag has been subscribed too
            rv = self.client.post(full_url, headers=headers)
            assert (rv.status == "200 OK")

            subscription = (db_session.query(Subscription)
                            .filter(Subscription.object_id == TagsTest.tag_id)
                            .filter(Subscription.object_type == 'tag')
                            .first())
            assert not subscription

    @unittest.skip("Current model code is broken: format_tags does not work, and does not make sense.")
    def test03_test_tag_list(self):
        """/tag_list is called when someone changes tags on the UI.

        Add the test tag to a post and ensure is has been added
        to the post_obj
        """
        with self.app.app_context():
            # we need to get the tag_string associate with the original post
            post_obj = (db_session.query(Post)
                        .filter(Post.path == TagsTest.post_path)
                        .first())
            post_tags_string = post_obj.format_tags()

            # add test/tag to this string
            test_tag_string = TagsTest.tag_name
            post_tags_string += ", " + test_tag_string

            data = {"tags": post_tags_string}
            rv = self.client.post('/tag_list?post_id=' + TagsTest.post_path,
                                  data=json.dumps(data),
                                  content_type='application/json',
                                  method='POST')

            assert rv.status == "200 OK"

            # check the new post tags string, and assert that "test/tag"
            post_obj = (db_session.query(Post)
                        .filter(Post.path == TagsTest.post_path)
                        .first())
            post_tags_string = post_obj.format_tags()

            assert test_tag_string in post_tags_string

    def test04_rename_tag_post(self):
        """/rename_tag is called from the batch_edit tag page.

        Rename the test/tag tag to test/tag_renamed, and
        check to make sure that old tag is deleted (we'll re-add it),
        the new tag is added, and
        the tag_string for related posts has changed
        """
        new_tag_string = TagsTest.tag_name + '_renamed'

        with self.app.app_context():
            # get all the posts with the old_tag_string
            post_tags = (db_session.query(assoc_post_tag)
                         .filter(assoc_post_tag.c.tag_id == TagsTest.tag_id)
                         .all())
            post_ids = [x[0] for x in post_tags]

            data = {'oldTagId': TagsTest.tag_id,
                    'newTag': new_tag_string}

            rv = self.client.post('/rename_tag',
                                  data=json.dumps(data),
                                  content_type='application/json')

            assert(rv.status == "200 OK")

            old_tag_obj = (db_session.query(Tag)
                           .filter(Tag.id == TagsTest.tag_id)
                           .all())
            assert not old_tag_obj

            new_tag_obj = (db_session.query(Tag)
                           .filter(Tag.name == new_tag_string)
                           .all())

            assert new_tag_obj and len(new_tag_obj) == 1
            new_id = new_tag_obj[0].id

            for post_id in post_ids:
                post_tag = (db_session.query(assoc_post_tag)
                            .filter(assoc_post_tag.c.post_id == post_id)
                            .filter(assoc_post_tag.c.tag_id == new_id)
                            .all())
                assert post_tag

    def test05_delete_tag(self):
        """/delete_tag_post deletes a tag from all posts.

        Check to make sure the tag is deleted, and all the posts with
        that tag don't have an associate
        """
        with self.app.app_context():
            tag_id = Tag(name=TagsTest.tag_name + '_renamed').id
            post_tags = (db_session.query(assoc_post_tag)
                         .filter(assoc_post_tag.c.tag_id == tag_id)
                         .all())
            post_ids = [x[0] for x in post_tags]
            delete_tag_url = '/delete_tag_post?tag_id={tag_id}'.format(**locals())
            rv = self.client.get(delete_tag_url)

            assert rv.status == "200 OK"

            tag = (db_session.query(Tag)
                   .filter(Tag.name == TagsTest.tag_name + '_renamed')
                   .first())

            assert not tag

            for post_id in post_ids:
                post_tag = (db_session.query(assoc_post_tag)
                            .filter(assoc_post_tag.c.tag_id == tag_id)
                            .filter(assoc_post_tag.c.post_id == post_id)
                            .all())
                assert not post_tag

    def tearDown(self):
        """Delete the tag that we created."""
        with self.app.app_context():
            tag = (db_session.query(Tag)
                   .filter(Tag.name == TagsTest.tag_name)
                   .first())
            if tag:
                db_session.delete(tag)
                db_session.commit()

if __name__ == '__main__':
    unittest.main()
