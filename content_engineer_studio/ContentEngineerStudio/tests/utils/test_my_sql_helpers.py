import pytest

from ContentEngineerStudio.utils.my_sql_helpers import SQL, HashedBotMessages


@pytest.fixture
def setUp():
    sql = SQL()
    sql.connect()
    return sql


def test_can_connect_to_database(setUp):
    pass
