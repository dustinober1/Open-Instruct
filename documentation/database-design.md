# Database Schema Design

**Audience**: Junior Developers
**Purpose**: Complete SQLite database schema for Open-Instruct
**Database**: SQLite 3
**Location**: `backend/data/open_instruct.db`

---

## Table of Contents
1. [Overview](#overview)
2. [Entity Relationship Diagram](#entity-relationship-diagram)
3. [Table Definitions](#table-definitions)
4. [Indexes](#indexes)
5. [Migrations](#migrations)
6. [Queries](#queries)
7. [Backup & Restore](#backup--restore)

---

## Overview

### Why SQLite?

| Advantage | Explanation |
|-----------|-------------|
| **Zero Configuration** | No database server to install or manage |
| **Portable** | Single file (`open_instruct.db`) contains everything |
| **Fast** | In-process, no network overhead |
| **Cross-Platform** | Works on Windows, macOS, Linux |
| **Reliable** | ACID compliant, battle-tested |
| **Perfect for MVP** | Single-user, local-first use case |

### Database File Location

```
backend/
├── data/
│   ├── open_instruct.db        # Main database file
│   ├── open_instruct.db-shm     # Shared memory file (auto)
│   └── open_instruct.db-wal     # Write-ahead log (auto)
└── ...
```

---

## Entity Relationship Diagram

```
┌─────────────────┐
│    courses      │
├─────────────────┤
│ id (PK)         │───┐
│ topic           │    │
│ target_audience │    │
│ num_objectives  │    │
│ created_at      │    │
│ updated_at      │    │
│ course_json     │    │
└─────────────────┘    │
                       │ 1
                       │
                       │ N
                       │
              ┌────────▼─────────┐
              │   objectives     │
              ├──────────────────┤
              │ id (PK)          │───┐
              │ course_id (FK)   │    │
              │ bloom_level      │    │
              │ verb             │    │
              │ content          │    │
              │ objective_order  │    │
              └──────────────────┘    │
                                       │ 1
                                       │
                                       │ N
                                       │
                       ┌───────────────▼───────────┐
                       │         quizzes           │
                       ├──────────────────────────┤
                       │ id (PK)                   │
                       │ objective_id (FK)         │
                       │ stem                      │
                       │ correct_answer            │
                       │ distractors (JSON)        │
                       │ explanation               │
                       │ difficulty                │
                       │ created_at                │
                       └──────────────────────────┘

┌─────────────────┐
│    cache        │
├─────────────────┤
│ id (PK)         │
│ prompt_hash     │──┐
│ response_json   │  │ For LLM response caching
│ created_at      │  │
│ expires_at      │──┘
└─────────────────┘
```

---

## Table Definitions

### Table 1: courses

Stores generated course structures.

```sql
CREATE TABLE courses (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    target_audience TEXT NOT NULL,
    num_objectives INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    course_json TEXT NOT NULL
);
```

**Column Details**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | TEXT | PRIMARY KEY | Unique course ID (e.g., `course_abc123`) |
| `topic` | TEXT | NOT NULL | Course topic |
| `target_audience` | TEXT | NOT NULL | Target learners |
| `num_objectives` | INTEGER | NOT NULL | Number of objectives (5-10) |
| `created_at` | TIMESTAMP | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp |
| `course_json` | TEXT | NOT NULL | Full course as JSON (includes all objectives) |

**Indexes**:
```sql
CREATE INDEX idx_courses_created_at ON courses(created_at DESC);
CREATE INDEX idx_courses_topic ON courses(topic);
```

---

### Table 2: objectives

Stores individual learning objectives.

```sql
CREATE TABLE objectives (
    id TEXT PRIMARY KEY,
    course_id TEXT NOT NULL,
    bloom_level TEXT NOT NULL,
    verb TEXT NOT NULL,
    content TEXT NOT NULL,
    objective_order INTEGER NOT NULL,
    explanation TEXT,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);
```

**Column Details**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | TEXT | PRIMARY KEY | Objective ID (e.g., `LO-001`) |
| `course_id` | TEXT | FOREIGN KEY | Parent course |
| `bloom_level` | TEXT | NOT NULL | Bloom's level (Remember, Understand, etc.) |
| `verb` | TEXT | NOT NULL | Action verb from approved list |
| `content` | TEXT | NOT NULL | Learning outcome description |
| `objective_order` | INTEGER | NOT NULL | Order within course (1, 2, 3...) |
| `explanation` | TEXT | NULLABLE | Optional verb explanation |

**Indexes**:
```sql
CREATE INDEX idx_objectives_course_id ON objectives(course_id);
CREATE INDEX idx_objectives_bloom_level ON objectives(bloom_level);
CREATE INDEX idx_objectives_order ON objectives(course_id, objective_order);
```

---

### Table 3: quizzes

Stores quiz questions for objectives.

```sql
CREATE TABLE quizzes (
    id TEXT PRIMARY KEY,
    objective_id TEXT NOT NULL,
    stem TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    distractors TEXT NOT NULL,
    explanation TEXT NOT NULL,
    difficulty TEXT NOT NULL DEFAULT 'medium',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (objective_id) REFERENCES objectives(id) ON DELETE CASCADE
);
```

**Column Details**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | TEXT | PRIMARY KEY | Quiz ID (e.g., `quiz_xyz789`) |
| `objective_id` | TEXT | FOREIGN KEY | Associated objective |
| `stem` | TEXT | NOT NULL | Question text |
| `correct_answer` | TEXT | NOT NULL | Correct option |
| `distractors` | TEXT | NOT NULL | JSON array of 3 wrong options |
| `explanation` | TEXT | NOT NULL | Why answer is correct |
| `difficulty` | TEXT | NOT NULL | `easy`, `medium`, or `hard` |
| `created_at` | TIMESTAMP | NOT NULL | Creation timestamp |

**distractors Format**:
```json
["Wrong option 1", "Wrong option 2", "Wrong option 3"]
```

**Indexes**:
```sql
CREATE INDEX idx_quizzes_objective_id ON quizzes(objective_id);
CREATE INDEX idx_quizzes_difficulty ON quizzes(difficulty);
```

---

### Table 4: cache

Stores LLM responses for repeated prompts.

```sql
CREATE TABLE cache (
    id TEXT PRIMARY KEY,
    prompt_hash TEXT NOT NULL UNIQUE,
    response_json TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);
```

**Column Details**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | TEXT | PRIMARY KEY | Cache entry ID |
| `prompt_hash` | TEXT | UNIQUE | SHA256 hash of prompt |
| `response_json` | TEXT | NOT NULL | LLM response as JSON |
| `created_at` | TIMESTAMP | NOT NULL | Cache entry creation |
| `expires_at` | TIMESTAMP | NOT NULL | When to invalidate (7 days default) |

**Hash Function**:
```python
import hashlib

def hash_prompt(topic: str, audience: str, options: dict) -> str:
    """Generate SHA256 hash of prompt parameters."""
    prompt_str = f"{topic}:{audience}:{json.dumps(options, sort_keys=True)}"
    return hashlib.sha256(prompt_str.encode()).hexdigest()
```

**Indexes**:
```sql
CREATE INDEX idx_cache_prompt_hash ON cache(prompt_hash);
CREATE INDEX idx_cache_expires_at ON cache(expires_at);
```

---

### Table 5: generation_logs

Stores logs of LLM generation attempts (for debugging).

```sql
CREATE TABLE generation_logs (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    prompt TEXT,
    raw_output TEXT,
    parsed_json TEXT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    attempt_number INTEGER NOT NULL,
    duration_ms INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Column Details**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | TEXT | PRIMARY KEY | Log entry ID |
| `request_id` | TEXT | NOT NULL | Unique request identifier |
| `topic` | TEXT | NOT NULL | Topic for generation |
| `prompt` | TEXT | NULLABLE | Full prompt sent to LLM |
| `raw_output` | TEXT | NULLABLE | Raw LLM response |
| `parsed_json` | TEXT | NULLABLE | Parsed JSON (if successful) |
| `success` | BOOLEAN | NOT NULL | Whether generation succeeded |
| `error_message` | TEXT | NULLABLE | Error message (if failed) |
| `attempt_number` | INTEGER | NOT NULL | Retry attempt (1, 2, 3...) |
| `duration_ms` | INTEGER | NULLABLE | Generation duration |
| `created_at` | TIMESTAMP | NOT NULL | Log timestamp |

**Indexes**:
```sql
CREATE INDEX idx_logs_request_id ON generation_logs(request_id);
CREATE INDEX idx_logs_created_at ON generation_logs(created_at DESC);
CREATE INDEX idx_logs_success ON generation_logs(success);
```

---

## Indexes

### Complete Index List

```sql
-- Courses
CREATE INDEX idx_courses_created_at ON courses(created_at DESC);
CREATE INDEX idx_courses_topic ON courses(topic);

-- Objectives
CREATE INDEX idx_objectives_course_id ON objectives(course_id);
CREATE INDEX idx_objectives_bloom_level ON objectives(bloom_level);
CREATE INDEX idx_objectives_order ON objectives(course_id, objective_order);

-- Quizzes
CREATE INDEX idx_quizzes_objective_id ON quizzes(objective_id);
CREATE INDEX idx_quizzes_difficulty ON quizzes(difficulty);

-- Cache
CREATE INDEX idx_cache_prompt_hash ON cache(prompt_hash);
CREATE INDEX idx_cache_expires_at ON cache(expires_at);

-- Logs
CREATE INDEX idx_logs_request_id ON generation_logs(request_id);
CREATE INDEX idx_logs_created_at ON generation_logs(created_at DESC);
CREATE INDEX idx_logs_success ON generation_logs(success);
```

### Index Statistics

To see index usage:
```sql
SELECT name, tbl_name, sql
FROM sqlite_master
WHERE type = 'index';
```

---

## Migrations

### Migration System

Using `alembic` for database versioning:

```bash
# Initialize alembic
cd backend
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Migration 001: Initial Schema

```python
# alembic/versions/001_initial_schema.py

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'courses',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('topic', sa.Text(), nullable=False),
        sa.Column('target_audience', sa.Text(), nullable=False),
        sa.Column('num_objectives', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('course_json', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'objectives',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('course_id', sa.Text(), nullable=False),
        sa.Column('bloom_level', sa.Text(), nullable=False),
        sa.Column('verb', sa.Text(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('objective_order', sa.Integer(), nullable=False),
        sa.Column('explanation', sa.Text()),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ... create other tables ...

def downgrade():
    op.drop_table('objectives')
    op.drop_table('courses')
    # ... drop other tables ...
```

### Migration 002: Add Caching

```python
# alembic/versions/002_add_caching.py

def upgrade():
    op.create_table(
        'cache',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('prompt_hash', sa.Text(), nullable=False),
        sa.Column('response_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('prompt_hash')
    )
    op.create_index('idx_cache_prompt_hash', 'cache', ['prompt_hash'])
    op.create_index('idx_cache_expires_at', 'cache', ['expires_at'])

def downgrade():
    op.drop_table('cache')
```

---

## Queries

### Common Query Patterns

#### 1. Get Course with Objectives

```python
# src/db/queries.py

import sqlite3
from typing import List, Dict
from pathlib import Path

DB_PATH = Path("backend/data/open_instruct.db")

def get_course_with_objectives(course_id: str) -> Dict:
    """Get course and all its objectives."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # Get course
    cursor.execute(
        """
        SELECT * FROM courses WHERE id = ?
        """,
        (course_id,)
    )
    course = cursor.fetchone()

    if not course:
        return None

    # Get objectives
    cursor.execute(
        """
        SELECT * FROM objectives
        WHERE course_id = ?
        ORDER BY objective_order ASC
        """,
        (course_id,)
    )
    objectives = cursor.fetchall()

    conn.close()

    return {
        "course": dict(course),
        "objectives": [dict(obj) for obj in objectives]
    }
```

#### 2. Cache Check & Store

```python
import json
from datetime import datetime, timedelta

def get_cached_response(prompt_hash: str) -> Dict:
    """Check cache for non-expired response."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT response_json, expires_at
        FROM cache
        WHERE prompt_hash = ? AND expires_at > ?
        """,
        (prompt_hash, datetime.now())
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        return json.loads(result["response_json"])
    return None

def store_cached_response(prompt_hash: str, response: Dict, ttl_days: int = 7):
    """Store response in cache."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    expires_at = datetime.now() + timedelta(days=ttl_days)

    cursor.execute(
        """
        INSERT INTO cache (id, prompt_hash, response_json, expires_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            f"cache_{prompt_hash[:16]}",
            prompt_hash,
            json.dumps(response),
            expires_at
        )
    )

    conn.commit()
    conn.close()
```

#### 3. Search Courses

```python
def search_courses(search_term: str, limit: int = 20) -> List[Dict]:
    """Search courses by topic."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, topic, target_audience, num_objectives, created_at
        FROM courses
        WHERE topic LIKE ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (f"%{search_term}%", limit)
    )

    results = cursor.fetchall()
    conn.close()

    return [dict(row) for row in results]
```

#### 4. Get Quiz by Objective

```python
def get_quiz_for_objective(objective_id: str) -> Dict:
    """Get quiz question for an objective."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM quizzes
        WHERE objective_id = ?
        """,
        (objective_id,)
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        quiz = dict(result)
        # Parse distractors JSON
        quiz["distractors"] = json.loads(quiz["distractors"])
        return quiz
    return None
```

#### 5. Log Generation Attempt

```python
def log_generation(
    request_id: str,
    topic: str,
    prompt: str,
    raw_output: str,
    parsed_json: Dict,
    success: bool,
    error_message: str,
    attempt_number: int,
    duration_ms: int
):
    """Log generation attempt for debugging."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO generation_logs (
            id, request_id, topic, prompt, raw_output, parsed_json,
            success, error_message, attempt_number, duration_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            f"log_{request_id}_{attempt_number}",
            request_id,
            topic,
            prompt,
            raw_output,
            json.dumps(parsed_json) if parsed_json else None,
            success,
            error_message,
            attempt_number,
            duration_ms
        )
    )

    conn.commit()
    conn.close()
```

---

## Backup & Restore

### Backup Database

```bash
# Simple file copy
cp backend/data/open_instruct.db backups/open_instruct_$(date +%Y%m%d).db

# Using SQLite dump
sqlite3 backend/data/open_instruct.db .dump > backups/open_instruct_backup.sql

# Compressed backup
gzip -c backend/data/open_instruct.db > backups/open_instruct_$(date +%Y%m%d).db.gz
```

### Restore Database

```bash
# From file copy
cp backups/open_instruct_20250105.db backend/data/open_instruct.db

# From SQL dump
sqlite3 backend/data/open_instruct.db < backups/open_instruct_backup.sql

# From compressed backup
gunzip -c backups/open_instruct_20250105.db.gz > backend/data/open_instruct.db
```

### Automated Backup Script

```python
# scripts/backup_database.py

import shutil
from datetime import datetime
from pathlib import Path

def backup_database():
    """Backup database with timestamp."""
    db_path = Path("backend/data/open_instruct.db")
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"open_instruct_{timestamp}.db"

    shutil.copy2(db_path, backup_path)
    print(f"Database backed up to: {backup_path}")

    # Keep only last 30 backups
    backups = sorted(backup_dir.glob("open_instruct_*.db"))
    for old_backup in backups[:-30]:
        old_backup.unlink()
        print(f"Deleted old backup: {old_backup}")

if __name__ == "__main__":
    backup_database()
```

---

## Performance Tuning

### PRAGMA Settings

```python
# src/db/connection.py

import sqlite3
from pathlib import Path

def get_connection():
    """Get optimized database connection."""
    conn = sqlite3.connect(Path("backend/data/open_instruct.db"))

    # Performance optimizations
    conn.execute("PRAGMA journal_mode = WAL")  # Write-ahead logging
    conn.execute("PRAGMA synchronous = NORMAL")  # Faster commits
    conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
    conn.execute("PRAGMA temp_store = MEMORY")  # Memory temp store

    return conn
```

### Vacuum Database

```sql
-- Rebuild database and reclaim space
VACUUM;

-- Analyze tables for query optimization
ANALYZE;
```

---

## Monitoring

### Database Statistics Query

```python
def get_database_stats():
    """Get database statistics for monitoring."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # Table row counts
    tables = ["courses", "objectives", "quizzes", "cache", "generation_logs"]
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        stats[f"{table}_count"] = cursor.fetchone()[0]

    # Database size
    db_path = Path(DB_PATH)
    stats["file_size_bytes"] = db_path.stat().st_size
    stats["file_size_mb"] = stats["file_size_bytes"] / (1024 * 1024)

    # Cache hit rate
    cursor.execute("SELECT COUNT(*) FROM cache")
    total_cache_entries = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM cache WHERE expires_at > datetime('now')")
    active_cache_entries = cursor.fetchone()[0]

    stats["cache_hit_rate"] = active_cache_entries / total_cache_entries if total_cache_entries > 0 else 0

    conn.close()
    return stats
```

---

## Next Steps

1. **Create database initialization script**
2. **Implement query functions** in `src/db/queries.py`
3. **Add migration system** using Alembic
4. **Set up automated backups**
5. **Add database monitoring** to health check endpoint

Remember: **SQLite is perfect for MVP**. If you need multi-user concurrency later, migrate to PostgreSQL.
