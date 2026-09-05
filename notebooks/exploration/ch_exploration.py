import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import os

    import httpx
    import marimo as mo
    return httpx, mo, os


@app.cell
def _(httpx, os):
    # --- Connexion ClickHouse via HTTP (code tuto officiel) ---
    CLICKHOUSE_URL = "http://clickhouse:8123"
    CLICKHOUSE_USER = "default"
    CLICKHOUSE_DB = "warehouse"
    try:
        CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "") or open("/tmp/ch_pwd.txt").read().strip()
    except Exception:
        CLICKHOUSE_PASSWORD = ""

    def ch_query(sql):
        resp = httpx.post(
            CLICKHOUSE_URL,
            params={"database": CLICKHOUSE_DB, "user": CLICKHOUSE_USER, "password": CLICKHOUSE_PASSWORD},
            content=sql + " FORMAT JSON",
        )
        resp.raise_for_status()
        return resp.json()["data"]
    return (ch_query,)


@app.cell
def _(ch_query, mo):
    # --- Requete d'exploration ---
    tables = ch_query("SHOW TABLES")
    mo.md(str(tables))
    return (tables,)


if __name__ == "__main__":
    app.run()
