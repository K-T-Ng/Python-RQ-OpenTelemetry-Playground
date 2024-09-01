import fakeredis
import pytest


@pytest.fixture()
def mock_redis_conn():
    yield fakeredis.FakeRedis()
