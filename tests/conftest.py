import os

from flask.ext.migrate import upgrade
import mock
import pytest

from app.blueprints.base.models import User
from app.factory import create_app


@pytest.fixture(scope='module')
def app(request):
    test_db = os.path.join(os.path.dirname(__file__), '../test.db')
    test_db_uri = 'sqlite:///{}'.format(test_db)
    app = create_app(
        TESTING=True,
        TEST_DB_PATH=test_db,
        SQLALCHEMY_DATABASE_URI=test_db_uri)

    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='module')
def db(app, request):

    def remove_db():
        if os.path.exists(app.config['TEST_DB_PATH']):
            os.unlink(app.config['TEST_DB_PATH'])

    remove_db()

    # run migrations
    upgrade()

    request.addfinalizer(remove_db)

    return app.extensions['sqlalchemy'].db


@pytest.fixture(scope='function')
def db_session(db, request):
    connection = db.engine.connect()
    transaction = connection.begin()

    options = {'bind': connection, 'binds': {}}
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)

    return session


@pytest.fixture
def selenium(db, live_server, selenium):
    """Override selenium fixture to always use flask live server"""
    return selenium


@pytest.fixture
def test_user(db_session):
    return User.get_or_create(email='test@example.com', full_name='Test Test')


@pytest.yield_fixture
def logged_in(client, test_user):

    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True

    yield test_user

    with client.session_transaction() as session:
        del session['user_id']
        del session['_fresh']
