from bs4 import BeautifulSoup
from flask import url_for
import pytest


@pytest.fixture
def form_submit(client):
    return client.post(url_for('notes.add'), data={
        'content': 'A *lovely* new note'})


@pytest.fixture
def follow_redirect(client, form_submit):
    return client.get(form_submit.headers['Location'])


@pytest.fixture
def soup(follow_redirect):
    return BeautifulSoup(follow_redirect.get_data(as_text=True), 'html.parser')


@pytest.mark.use_fixtures('db_session', 'form_submit')
class TestWhenAddingANewNote(object):

    def test_it_redirects_to_the_list_view(self, db_session, form_submit):
        assert form_submit.status_code == 302
        assert url_for('notes.list') in form_submit.headers['Location']

    def test_it_updates_the_list_view(self, db_session, soup):
        notes = soup.find_all(class_='note')
        assert len(notes) > 0
        assert 'A <em>lovely</em> new note' in str(notes[0].find(itemprop='text'))
