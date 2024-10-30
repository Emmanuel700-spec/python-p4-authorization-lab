import flask
import pytest

from app import app
from models import Article, User

app.secret_key = b'a\xdb\xd2\x13\x93\xc1\xe9\x97\xef2\xe3\x004U\xd1Z'

class TestApp:
    '''Flask API in app.py'''

    @pytest.fixture(autouse=True)
    def setup(self):
        # Clear the database before each test
        with app.test_client() as client:
            client.get('/clear')
            yield client  # This will allow the tests to run

    def test_can_only_access_member_only_while_logged_in(self):
        '''Allows logged-in users to access member-only article index at /members_only_articles.'''
        client = flask.Flask.test_client(app)

        user = User.query.first()
        client.post('/login', json={'username': user.username})

        response = client.get('/members_only_articles')
        assert response.status_code == 200, "User should be able to access member-only articles"

        client.delete('/logout')

        response = client.get('/members_only_articles')
        assert response.status_code == 401, "Logged-out user should not access member-only articles"

    def test_member_only_articles_shows_member_only_articles(self):
        '''Only shows member-only articles at /members_only_articles.'''
        client = flask.Flask.test_client(app)

        user = User.query.first()
        client.post('/login', json={'username': user.username})

        response_json = client.get('/members_only_articles').get_json()
        
        assert response_json is not None, "Response should not be None"
        for article in response_json:
            assert article['is_member_only'] == True, "All articles should be member-only"

    def test_can_only_access_member_only_article_while_logged_in(self):
        '''Allows logged-in users to access full member-only articles at /members_only_articles/<int:id>.'''
        client = flask.Flask.test_client(app)

        user = User.query.first()
        client.post('/login', json={'username': user.username})

        # Fetch an article ID that exists and is member-only
        article = Article.query.filter_by(is_member_only=True).first()
        assert article is not None, "No member-only articles found in the database"
        
        article_id = article.id

        response = client.get(f'/members_only_articles/{article_id}')
        assert response.status_code == 200, "User should be able to access the member-only article"

        client.delete('/logout')

        response = client.get(f'/members_only_articles/{article_id}')
        assert response.status_code == 401, "Logged-out user should not access member-only articles"
