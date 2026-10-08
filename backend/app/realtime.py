"""Authenticated SSE over PostgreSQL NOTIFY; works across API workers.

NOTIFY contains routing metadata only. Clients retrieve content through normal
authorized REST routes. Publication participates in the data transaction.
"""
import json
import os
import time
import jwt
import psycopg
from sqlalchemy import text

CHANNEL = "ticketcenter_events"

def publish(db, kind, ticket=None, message=None):
    if db.get_bind().dialect.name != "postgresql":
        return  # SQLite supports REST unit tests, not a production event stream.
    payload = {"type": kind}
    if ticket is not None:
        payload.update(ticket_id=ticket.id, department=ticket.department, employee_id=ticket.employee_id)
    if message is not None:
        payload.update(message_id=message.id, author_id=message.author_id)
    db.execute(text("SELECT pg_notify(:channel, :payload)"), {"channel": CHANNEL, "payload": json.dumps(payload)})

def event_visible(event, user):
    return event.get("ticket_id") is None or user["role"] == "admin" or (user["role"] == "employee" and event.get("employee_id") == user["id"]) or (user["role"] == "agent" and event.get("department") == user["department"])

def frame(event):
    return "data: " + json.dumps(event, separators=(",", ":")) + "\n\n"

async def stream_events(dsn, user_id, token_version, expires_at, request):
    try:
        async with await psycopg.AsyncConnection.connect(dsn, autocommit=True, connect_timeout=10) as conn:
            await conn.execute(f"LISTEN {CHANNEL}")
            async def active_user():
                cursor = await conn.execute("SELECT id,role,department,is_active,token_version FROM users WHERE id=%s", (user_id,))
                row = await cursor.fetchone()
                if not row or not row[3] or row[4] != token_version or time.time() >= expires_at:
                    return None
                return {"id": row[0], "role": row[1], "department": row[2]}
            if not await active_user():
                yield frame({"type": "session.expired"})
                return
            # Subscription is established before the client requests a fresh snapshot.
            yield frame({"type": "ready"})
            while not await request.is_disconnected():
                # Complete the notification iterator before querying this connection.
                # Psycopg holds its connection lock while the iterator is suspended.
                incoming = [notification async for notification in conn.notifies(timeout=15, stop_after=1)]
                for notification in incoming:
                    user = await active_user()
                    if user is None:
                        yield frame({"type": "session.expired"})
                        return
                    event = json.loads(notification.payload)
                    if event_visible(event, user):
                        # Internal routing fields never leave the service.
                        public = {key: event[key] for key in ("type", "ticket_id", "message_id", "author_id") if key in event}
                        yield frame(public)
                if not await active_user():
                    yield frame({"type": "session.expired"})
                    return
                yield ": heartbeat\n\n"
    except psycopg.Error:
        # No connection string, token, or SQL error is returned to the browser.
        yield frame({"type": "unavailable"})
