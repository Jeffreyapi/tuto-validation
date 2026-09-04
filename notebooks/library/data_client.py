import marimo as mo
import httpx
import os
from typing import Any

_CLICKHOUSE_URL = os.environ.get("CLICKHOUSE_HTTP_URL", "http://clickhouse:8123")
_CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "default")
try:
    _CLICKHOUSE_PASS = os.environ.get("CLICKHOUSE_PASSWORD", "") or open("/tmp/ch_pwd.txt").read().strip()
except Exception:
    _CLICKHOUSE_PASS = ""
_CLICKHOUSE_DB = os.environ.get("CLICKHOUSE_DATABASE", "warehouse")

def query(sql, database=_CLICKHOUSE_DB):
    # Execute un SELECT et retourne les lignes.
    resp = httpx.post(
        _CLICKHOUSE_URL,
        params={"database": database, "user": _CLICKHOUSE_USER},
        auth=(_CLICKHOUSE_USER, _CLICKHOUSE_PASS),
        content=sql + " FORMAT JSON",
    )
    resp.raise_for_status()
    return resp.json()["data"]

def execute(sql, database=_CLICKHOUSE_DB):
    # Execute un DDL/INSERT (pas de retour).
    httpx.post(
        _CLICKHOUSE_URL,
        params={"database": database, "user": _CLICKHOUSE_USER},
        auth=(_CLICKHOUSE_USER, _CLICKHOUSE_PASS),
        content=sql,
    ).raise_for_status()

def ping():
    # Verifie que ClickHouse est accessible.
    try:
        httpx.get(_CLICKHOUSE_URL + "/ping", timeout=5).raise_for_status()
        return True
    except Exception:
        return False

app = mo.App()

@app.cell
def _():
    status = "OK ClickHouse" if ping() else "ClickHouse unreachable"
    return mo.md(status)