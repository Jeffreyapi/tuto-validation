import marimo as mo
import os
from prefect import flow, task, get_run_logger

from data.client import execute, ping

SQL_CREATE = "CREATE TABLE IF NOT EXISTS warehouse.products_raw (id UInt32, name String, price Float64, category String, loaded_at DateTime DEFAULT now()) ENGINE = MergeTree() ORDER BY (id, loaded_at)"

@task(name="create-raw-table", retries=2)
def create_table():
    execute(SQL_CREATE)

@task(name="extract-products", retries=1)
def extract_products():
    logger = get_run_logger()
    try:
        import httpx
        api_url = os.environ.get("SOURCE_API_URL", "https://fakestoreapi.com/products")
        logger.info(f"Fetching from {api_url}")
        resp = httpx.get(api_url, timeout=30)
        resp.raise_for_status()
        products = resp.json()
        logger.info(f"Fetched {len(products)} products")
        return products
    except Exception as exc:
        logger.warning(f"Source API unreachable ({exc}) - fallback synthetique")
        return [
            {"id": i, "title": f"Produit test {i}", "price": 9.99 + i, "category": "synthetic"}
            for i in range(1, 21)
        ]

@task(name="load-to-clickhouse")
def load_to_clickhouse(products):
    logger = get_run_logger()
    if not products:
        logger.warning("No products to load")
        return
    rows = ", ".join(
        f"({p['id']}, '{p['title'][:200]}', {p['price']}, '{p['category']}')"
        for p in products
    )
    execute(f"INSERT INTO warehouse.products_raw (id, name, price, category) VALUES {rows}")
    logger.info(f"Loaded {len(products)} rows into ClickHouse")

@flow(name="extract-products", log_prints=True)
def main(run_id=None, published_tag=None):
    logger = get_run_logger()
    logger.info("Starting extraction pipeline")
    assert ping(), "ClickHouse unreachable"
    create_table()
    products = extract_products()
    load_to_clickhouse(products)
    logger.info("Pipeline completed successfully")

app = mo.App()

@app.cell
def _():
    mo.md("# Extract Products Job")
    return