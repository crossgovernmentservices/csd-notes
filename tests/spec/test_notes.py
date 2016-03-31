import pytest

from app.blueprints.notes.models import Note
from tests.util import app, db  # noqa


@pytest.mark.use_fixtures('app', 'db')
class TestWhenUpdatingANote(object):

    def test_it_stores_the_previous_version(self, db):  # noqa
        note = Note.create('Test note')
        assert len(note.history) == 0

        note.update('Test note edited')
        assert len(note.history) == 1

        assert note.history[0].content == 'Test note'
        assert note.history[0].version == 1


@pytest.mark.use_fixtures('app', 'db')
class TestWhenANoteHasHistory(object):

    def test_it_can_be_reverted_to_a_previous_version(self, db):  # noqa
        note = Note.create('Test note')
        note.update('Test note edited')
        note.update('Test note edited again')
        assert len(note.history) == 2
        assert note.history[0].version == 0
        assert note.history[1].version == 1

        note.revert()

        assert len(note.history) == 3
        assert note.content == 'Test note edited'

        note.revert(version=2)

        assert len(note.history) == 4
        assert note.content == 'Test note edited again'
