import pytest

from affo_user_service.application import create_app, provisioning as provisioning_
from affo_user_service.extensions import db as db_

TEST_DATABASE_URI = f"sqlite://"


@pytest.fixture(scope="session", autouse=True)
def app(request):
    settings_override = {"TESTING": True, "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URI, "CACHE_TYPE": "simple"}
    app = create_app(settings_override)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope="session", autouse=True)
def db(app, request):
    db_.app = app
    db_.create_all()

    return db_


@pytest.fixture(scope="function")
def session(db, request):
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope="session")
def client(app, db):
    return app.test_client()


@pytest.fixture(scope="session", autouse=True)
def provisioning(app, db):
    provisioning_(app)
