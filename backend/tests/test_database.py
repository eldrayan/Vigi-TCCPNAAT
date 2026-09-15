"""
Descrição: Verifica a criação do diretório para bancos SQLite locais.
Autor: Leôncio Ferreira
"""

from app.infrastructure.database import ensure_sqlite_directory


def test_ensure_sqlite_directory_creates_parent(tmp_path) -> None:
    database = tmp_path / "nested" / "data" / "vigi.db"

    ensure_sqlite_directory(f"sqlite+aiosqlite:///{database}")

    assert database.parent.is_dir()
