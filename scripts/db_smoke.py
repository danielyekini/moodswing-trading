from __future__ import annotations

import os
import sys
from sqlalchemy import create_engine, text


DDL_CHECKS = [
    # Verify parents are partitioned by ticker
    ("article", "LIST"),
    ("sentiment_day", "LIST"),
    ("prediction", "LIST"),
]


def assert_partitioned(conn, table: str, strategy: str) -> None:
    res = conn.execute(
        text(
            """
            SELECT partstrat
            FROM pg_partitioned_table t
            JOIN pg_class c ON c.oid = t.partrelid
            WHERE c.relname = :table
            """
        ),
        {"table": table},
    ).fetchone()
    if not res:
        raise AssertionError(f"Table {table} is not partitioned")
    map_ = {"l": "LIST", "r": "RANGE", "h": "HASH"}
    if map_.get(res[0]) != strategy:
        raise AssertionError(f"Table {table} has strategy {res[0]} not {strategy}")


def assert_default_exists(conn, table: str) -> None:
    res = conn.execute(
        text(
            """
            SELECT c.relname
            FROM pg_inherits i
            JOIN pg_class c ON c.oid = i.inhrelid
            JOIN pg_class p ON p.oid = i.inhparent
            WHERE p.relname = :parent
            AND pg_get_expr(c.relpartbound, c.oid) = 'DEFAULT'
            """
        ),
        {"parent": table},
    ).fetchone()
    if not res:
        raise AssertionError(f"Default partition for {table} not found")


def main() -> int:
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL not set", file=sys.stderr)
        return 2
    engine = create_engine(url, future=True)
    with engine.begin() as conn:
        for tbl, strat in DDL_CHECKS:
            assert_partitioned(conn, tbl, strat)
            assert_default_exists(conn, tbl)
    print("DB smoke OK: partitioned parents and DEFAULT partitions exist")
    return 0


if __name__ == "__main__":
    sys.exit(main())






