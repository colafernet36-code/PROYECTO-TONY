import os

import pytest

from database.base import Base
from database.session import check_database, make_engine


@pytest.fixture(scope="session")
def db_engine():
    url = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("Definir TEST_DATABASE_URL o DATABASE_URL para tests de integracion")

    engine = make_engine(url)
    try:
        check_database(engine)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"PostgreSQL no disponible en {url}: {exc}")

    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()
