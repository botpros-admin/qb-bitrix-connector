"""
Database module for tracking sync state and ID mappings between QB and Bitrix24
"""

import sqlite3
from datetime import datetime
from config import DATABASE_PATH


def init_db():
    """Initialize the sync state database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Table to track last sync times for each entity type
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sync_state (
            entity_type TEXT PRIMARY KEY,
            last_sync_qb_to_bitrix TIMESTAMP,
            last_sync_bitrix_to_qb TIMESTAMP
        )
    ''')

    # Table to map QuickBooks IDs to Bitrix24 IDs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS id_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            qb_id TEXT,
            qb_list_id TEXT,
            bitrix_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(entity_type, qb_list_id)
        )
    ''')

    # Table to queue changes from Bitrix24 to be sent to QB
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bitrix_to_qb_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            bitrix_id TEXT NOT NULL,
            action TEXT NOT NULL,
            data TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP,
            error_message TEXT
        )
    ''')

    # Table to log sync operations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            direction TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            qb_id TEXT,
            bitrix_id TEXT,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DATABASE_PATH}")


def get_last_sync_time(entity_type, direction):
    """Get the last sync time for an entity type and direction"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    column = 'last_sync_qb_to_bitrix' if direction == 'qb_to_bitrix' else 'last_sync_bitrix_to_qb'
    cursor.execute(f'SELECT {column} FROM sync_state WHERE entity_type = ?', (entity_type,))
    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None


def update_last_sync_time(entity_type, direction):
    """Update the last sync time for an entity type and direction"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    column = 'last_sync_qb_to_bitrix' if direction == 'qb_to_bitrix' else 'last_sync_bitrix_to_qb'
    now = datetime.now().isoformat()

    cursor.execute(f'''
        INSERT INTO sync_state (entity_type, {column})
        VALUES (?, ?)
        ON CONFLICT(entity_type) DO UPDATE SET {column} = ?
    ''', (entity_type, now, now))

    conn.commit()
    conn.close()


def get_bitrix_id(entity_type, qb_list_id):
    """Get Bitrix24 ID for a QuickBooks entity"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT bitrix_id FROM id_mappings
        WHERE entity_type = ? AND qb_list_id = ?
    ''', (entity_type, qb_list_id))
    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None


def get_qb_list_id(entity_type, bitrix_id):
    """Get QuickBooks ListID for a Bitrix24 entity"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT qb_list_id FROM id_mappings
        WHERE entity_type = ? AND bitrix_id = ?
    ''', (entity_type, bitrix_id))
    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None


def save_id_mapping(entity_type, qb_list_id, bitrix_id):
    """Save a mapping between QB and Bitrix24 IDs"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO id_mappings (entity_type, qb_list_id, bitrix_id, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(entity_type, qb_list_id) DO UPDATE SET
            bitrix_id = ?, updated_at = ?
    ''', (entity_type, qb_list_id, bitrix_id, datetime.now().isoformat(),
          bitrix_id, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def add_to_qb_queue(entity_type, bitrix_id, action, data):
    """Add an item to the queue for syncing to QuickBooks"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO bitrix_to_qb_queue (entity_type, bitrix_id, action, data)
        VALUES (?, ?, ?, ?)
    ''', (entity_type, bitrix_id, action, data))

    conn.commit()
    conn.close()


def get_pending_qb_queue():
    """Get all pending items to sync to QuickBooks"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, entity_type, bitrix_id, action, data
        FROM bitrix_to_qb_queue
        WHERE status = 'pending'
        ORDER BY created_at
    ''')
    rows = cursor.fetchall()
    conn.close()

    return [{'id': r[0], 'entity_type': r[1], 'bitrix_id': r[2],
             'action': r[3], 'data': r[4]} for r in rows]


def mark_queue_item_processed(item_id, status='completed', error_message=None):
    """Mark a queue item as processed"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE bitrix_to_qb_queue
        SET status = ?, processed_at = ?, error_message = ?
        WHERE id = ?
    ''', (status, datetime.now().isoformat(), error_message, item_id))

    conn.commit()
    conn.close()


def log_sync(direction, entity_type, qb_id, bitrix_id, action, status, message=None):
    """Log a sync operation"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO sync_log (direction, entity_type, qb_id, bitrix_id, action, status, message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (direction, entity_type, qb_id, bitrix_id, action, status, message))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
