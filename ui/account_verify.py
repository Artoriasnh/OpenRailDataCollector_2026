from typing import Dict, Tuple, Optional

import psycopg2
import stomp


DEFAULT_RAIL_HOST = "publicdatafeeds.networkrail.co.uk"
DEFAULT_RAIL_PORT = 61618
DEFAULT_CONNECT_TIMEOUT = 6


def _safe_disconnect(conn) -> None:
    if conn is None:
        return
    try:
        if conn.is_connected():
            conn.disconnect()
    except Exception:
        pass


def _normalize_sql_info(sql_info: Dict) -> Dict:
    return {
        "sql_host": (sql_info.get("sql_host") or "localhost").strip(),
        "port": int(sql_info.get("port") or 5432),
        "database_name": (sql_info.get("database_name") or "postgres").strip(),
        "sql_username": (sql_info.get("sql_username") or "postgres").strip(),
        "sql_password": sql_info.get("sql_password") or "",
        "schema_name": (sql_info.get("schema_name") or "public").strip(),
    }


def _build_rail_target(rail_info: Optional[Dict]) -> Tuple[str, int]:
    if not rail_info:
        return DEFAULT_RAIL_HOST, DEFAULT_RAIL_PORT

    host = (rail_info.get("rail_host") or DEFAULT_RAIL_HOST).strip()
    port = int(rail_info.get("rail_port") or DEFAULT_RAIL_PORT)
    return host, port


def verify_stomp_credentials(
    email: str,
    password: str,
    rail_info: Optional[Dict] = None,
) -> Tuple[bool, str]:
    conn = None
    try:
        host, port = _build_rail_target(rail_info)

        conn = stomp.Connection12(
            host_and_ports=[(host, port)],
            keepalive=True,
            heartbeats=(5000, 5000),
            timeout=DEFAULT_CONNECT_TIMEOUT,
        )

        conn.connect(
            username=email,
            passcode=password,
            wait=True,
        )

        return True, f"STOMP login success ({host}:{port})"

    except Exception as exc:
        return False, f"STOMP login failed: {exc}"

    finally:
        _safe_disconnect(conn)


def verify_postgres_connection(sql_info: Dict) -> Tuple[bool, str]:
    conn = None
    cur = None

    try:
        cfg = _normalize_sql_info(sql_info)

        conn = psycopg2.connect(
            host=cfg["sql_host"],
            port=cfg["port"],
            dbname=cfg["database_name"],
            user=cfg["sql_username"],
            password=cfg["sql_password"],
            connect_timeout=DEFAULT_CONNECT_TIMEOUT,
        )

        cur = conn.cursor()
        cur.execute("select version();")
        version = cur.fetchone()[0]

        cur.execute(
            """
            select exists (
                select 1
                from information_schema.schemata
                where schema_name = %s
            );
            """,
            (cfg["schema_name"],)
        )
        schema_exists = cur.fetchone()[0]

        if schema_exists:
            schema_msg = f"schema '{cfg['schema_name']}' found"
        else:
            schema_msg = f"schema '{cfg['schema_name']}' not found yet"

        return True, f"Database connection success: {schema_msg}\n{version}"

    except Exception as exc:
        return False, f"Database connection failed: {exc}"

    finally:
        try:
            if cur is not None:
                cur.close()
        except Exception:
            pass

        try:
            if conn is not None:
                conn.close()
        except Exception:
            pass


def test_all_connections(
    email: str,
    password: str,
    sql_info: Dict,
    rail_info: Optional[Dict] = None,
) -> Dict:
    rail_ok, rail_msg = verify_stomp_credentials(
        email=email,
        password=password,
        rail_info=rail_info,
    )

    db_ok, db_msg = verify_postgres_connection(sql_info=sql_info)

    return {
        "success": rail_ok and db_ok,
        "rail_ok": rail_ok,
        "rail_msg": rail_msg,
        "db_ok": db_ok,
        "db_msg": db_msg,
    }