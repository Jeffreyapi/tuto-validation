import marimo as mo
import httpx
import os

CLICKHOUSE_URL = os.environ.get("CLICKHOUSE_HTTP_URL", "http://clickhouse:8123")
CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "default")
try:
    CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "") or open("/tmp/ch_pwd.txt").read().strip()
except Exception:
    CLICKHOUSE_PASSWORD = ""
CLICKHOUSE_DB = os.environ.get("CLICKHOUSE_DATABASE", "warehouse")

def ch_query(sql):
    # Execute une requete ClickHouse et retourne les resultats.
    resp = httpx.post(
        CLICKHOUSE_URL,
        params={"database": CLICKHOUSE_DB, "user": CLICKHOUSE_USER},
        auth=(CLICKHOUSE_USER, CLICKHOUSE_PASSWORD),
        content=sql + " FORMAT JSON",
    )
    resp.raise_for_status()
    return resp.json()["data"]

app = mo.App()

@app.cell
def _():
    try:
        tables = ch_query("SHOW TABLES")
        mo.table(tables)
    except Exception as e:
        mo.md(f"Erreur ClickHouse: {e}")
    return