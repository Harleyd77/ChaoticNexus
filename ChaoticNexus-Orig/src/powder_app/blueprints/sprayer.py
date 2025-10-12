from __future__ import annotations

import json
import os
from datetime import datetime

from flask import Blueprint, abort, jsonify, redirect, render_template, request, url_for

from ..core.config import UPLOADS_DIR
from ..core.db import db_execute, db_query_all, db_query_one, get_db
from ..core.security import has_perm, is_admin, require_admin
from ..core.utils import slugify

bp = Blueprint("sprayer", __name__)


def _now_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def _ensure_sprayer_schema_sqlite() -> None:
    db = get_db()
    db.executescript(
        """
        PRAGMA foreign_keys=ON;
        CREATE TABLE IF NOT EXISTS job_powders (
          job_id    INTEGER NOT NULL,
          powder_id INTEGER NOT NULL,
          role      TEXT DEFAULT 'primary',
          est_kg    REAL,
          PRIMARY KEY (job_id, powder_id, role),
          FOREIGN KEY (job_id)    REFERENCES jobs(id)    ON DELETE CASCADE,
          FOREIGN KEY (powder_id) REFERENCES powders(id) ON DELETE RESTRICT
        );
        CREATE INDEX IF NOT EXISTS idx_job_powders_powder ON job_powders(powder_id);
        CREATE INDEX IF NOT EXISTS idx_job_powders_job    ON job_powders(job_id);

        CREATE TABLE IF NOT EXISTS spray_batch (
          id               INTEGER PRIMARY KEY AUTOINCREMENT,
          powder_id        INTEGER NOT NULL,
          role             TEXT DEFAULT 'primary',
          operator         TEXT,
          note             TEXT,
          started_at       TEXT NOT NULL DEFAULT (datetime('now')),
          ended_at         TEXT,
          start_weight_kg  REAL NOT NULL,
          end_weight_kg    REAL,
          used_kg          REAL,
          duration_min     REAL,
          FOREIGN KEY (powder_id) REFERENCES powders(id)
        );
        CREATE INDEX IF NOT EXISTS idx_spray_batch_powder ON spray_batch(powder_id);

        CREATE TABLE IF NOT EXISTS spray_batch_jobs (
          batch_id   INTEGER NOT NULL,
          job_id     INTEGER NOT NULL,
          time_min         REAL,
          start_ts         TEXT,
          end_ts           TEXT,
          elapsed_seconds  REAL DEFAULT 0,
          running_since    TEXT,
          PRIMARY KEY (batch_id, job_id),
          FOREIGN KEY (batch_id) REFERENCES spray_batch(id) ON DELETE CASCADE,
          FOREIGN KEY (job_id)    REFERENCES jobs(id)       ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_spray_batch_jobs_job ON spray_batch_jobs(job_id);

        CREATE TABLE IF NOT EXISTS powder_usage (
          id         INTEGER PRIMARY KEY AUTOINCREMENT,
          powder_id  INTEGER NOT NULL,
          job_id     INTEGER,
          used_kg    REAL NOT NULL,
          note       TEXT,
          created_at TEXT NOT NULL DEFAULT (datetime('now')),
          FOREIGN KEY (powder_id) REFERENCES powders(id),
          FOREIGN KEY (job_id)    REFERENCES jobs(id)
        );
        """
    )

    cols = [row["name"] for row in db.execute("PRAGMA table_info(powders)")]
    if "on_hand_kg" not in cols:
        db.execute("ALTER TABLE powders ADD COLUMN on_hand_kg REAL DEFAULT 0")
    if "last_weighed_kg" not in cols:
        db.execute("ALTER TABLE powders ADD COLUMN last_weighed_kg REAL")
    if "last_weighed_at" not in cols:
        db.execute("ALTER TABLE powders ADD COLUMN last_weighed_at TEXT")
    db.commit()

    db.execute(
        """
          INSERT OR IGNORE INTO job_powders (job_id, powder_id, role)
          SELECT j.id, p.id, 'primary'
          FROM jobs j
          JOIN powders p
            ON LOWER(TRIM(j.color)) = LOWER(TRIM(p.powder_color))
          WHERE COALESCE(j.color,'') <> ''
        """
    )
    db.commit()

    db.executescript(
        """
        DROP VIEW IF EXISTS spray_batches_view;
        CREATE VIEW spray_batches_view AS
        SELECT
          sb.id AS batch_id, p.powder_color, p.manufacturer, sb.role, sb.operator,
          sb.started_at, sb.ended_at, sb.start_weight_kg, sb.end_weight_kg, sb.used_kg, sb.duration_min
        FROM spray_batch sb
        JOIN powders p ON p.id = sb.powder_id;

        DROP VIEW IF EXISTS job_spray_time_view;
        CREATE VIEW job_spray_time_view AS
        SELECT
          j.id AS job_id, j.company AS job_name, j.color,
          p.manufacturer AS supplier,
          sb.started_at AS batch_started, sb.ended_at AS batch_ended,
          sb.start_weight_kg, sb.end_weight_kg, sb.used_kg, sb.duration_min,
          sbj.start_ts AS job_start, sbj.end_ts AS job_end,
          CASE WHEN sbj.start_ts IS NOT NULL AND sbj.end_ts IS NOT NULL
               THEN ROUND((julianday(sbj.end_ts)-julianday(sbj.start_ts))*24*60,1)
               ELSE NULL END AS job_minutes
        FROM spray_batch_jobs sbj
        JOIN spray_batch sb ON sb.id = sbj.batch_id
        JOIN jobs j         ON j.id  = sbj.job_id
        JOIN powders p      ON p.id  = sb.powder_id;
        """
    )
    db.commit()

    sbj_cols = [row['name'] for row in db.execute('PRAGMA table_info(spray_batch_jobs)')]
    if 'elapsed_seconds' not in sbj_cols:
        db.execute('ALTER TABLE spray_batch_jobs ADD COLUMN elapsed_seconds REAL DEFAULT 0')
        db.execute('UPDATE spray_batch_jobs SET elapsed_seconds = COALESCE(time_min, 0) * 60.0 WHERE elapsed_seconds IS NULL OR (elapsed_seconds = 0 AND COALESCE(time_min, 0) > 0)')
    if 'running_since' not in sbj_cols:
        db.execute('ALTER TABLE spray_batch_jobs ADD COLUMN running_since TEXT')
    db.commit()


def _ensure_sprayer_schema_pg() -> None:
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS job_powders (
          job_id    INTEGER NOT NULL,
          powder_id INTEGER NOT NULL,
          role      TEXT DEFAULT 'primary',
          est_kg    REAL,
          PRIMARY KEY (job_id, powder_id, role),
          FOREIGN KEY (job_id)    REFERENCES jobs(id)    ON DELETE CASCADE,
          FOREIGN KEY (powder_id) REFERENCES powders(id) ON DELETE RESTRICT
        )
        """
    )
    db.execute("CREATE INDEX IF NOT EXISTS idx_job_powders_powder ON job_powders(powder_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_job_powders_job ON job_powders(job_id)")
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS spray_batch (
          id               SERIAL PRIMARY KEY,
          powder_id        INTEGER NOT NULL,
          role             TEXT DEFAULT 'primary',
          operator         TEXT,
          note             TEXT,
          started_at       TEXT NOT NULL DEFAULT to_char(CURRENT_TIMESTAMP,'YYYY-MM-DD HH24:MI:SS'),
          ended_at         TEXT,
          start_weight_kg  REAL NOT NULL,
          end_weight_kg    REAL,
          used_kg          REAL,
          duration_min     REAL,
          FOREIGN KEY (powder_id) REFERENCES powders(id)
        )
        """
    )
    db.execute("CREATE INDEX IF NOT EXISTS idx_spray_batch_powder ON spray_batch(powder_id)")
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS spray_batch_jobs (
          batch_id   INTEGER NOT NULL,
          job_id     INTEGER NOT NULL,
          time_min         REAL,
          start_ts         TEXT,
          end_ts           TEXT,
          elapsed_seconds  REAL DEFAULT 0,
          running_since    TEXT,
          PRIMARY KEY (batch_id, job_id),
          FOREIGN KEY (batch_id) REFERENCES spray_batch(id) ON DELETE CASCADE,
          FOREIGN KEY (job_id)    REFERENCES jobs(id)       ON DELETE CASCADE
        )
        """
    )
    db.execute("CREATE INDEX IF NOT EXISTS idx_spray_batch_jobs_job ON spray_batch_jobs(job_id)")
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS powder_usage (
          id         SERIAL PRIMARY KEY,
          powder_id  INTEGER NOT NULL,
          job_id     INTEGER,
          used_kg    REAL NOT NULL,
          note       TEXT,
          created_at TEXT NOT NULL DEFAULT to_char(CURRENT_TIMESTAMP,'YYYY-MM-DD HH24:MI:SS'),
          FOREIGN KEY (powder_id) REFERENCES powders(id),
          FOREIGN KEY (job_id)    REFERENCES jobs(id)
        )
        """
    )
    db.execute("ALTER TABLE spray_batch_jobs ADD COLUMN IF NOT EXISTS elapsed_seconds REAL DEFAULT 0")
    db.execute("ALTER TABLE spray_batch_jobs ADD COLUMN IF NOT EXISTS running_since TEXT")
    db.execute("UPDATE spray_batch_jobs SET elapsed_seconds = COALESCE(elapsed_seconds, COALESCE(time_min, 0) * 60.0) WHERE elapsed_seconds IS NULL OR (elapsed_seconds = 0 AND COALESCE(time_min, 0) > 0)")
    db.execute("ALTER TABLE powders ADD COLUMN IF NOT EXISTS on_hand_kg REAL")
    db.execute("ALTER TABLE powders ADD COLUMN IF NOT EXISTS last_weighed_kg REAL")
    db.execute("ALTER TABLE powders ADD COLUMN IF NOT EXISTS last_weighed_at TEXT")
    db.execute("ALTER TABLE powders ADD COLUMN IF NOT EXISTS additional_info TEXT")
    db.execute(
        """
          INSERT INTO job_powders (job_id, powder_id, role)
          SELECT j.id, p.id, 'primary'
          FROM jobs j
          JOIN powders p ON LOWER(TRIM(j.color)) = LOWER(TRIM(p.powder_color))
          WHERE COALESCE(j.color,'') <> ''
          ON CONFLICT DO NOTHING
        """
    )
    db.commit()


def _ensure_sprayer_schema() -> None:
    _ensure_sprayer_schema_pg()


try:
    _ensure_sprayer_schema()
except Exception:
    pass


def _parse_ts(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def _seconds_to_minutes(seconds):
    if not seconds:
        return 0.0
    return round(seconds / 60.0, 3)


def _select_batch_jobs(db, batch_id, job_ids=None):
    if job_ids:
        job_ids = [int(j) for j in job_ids if j is not None]
        job_ids = sorted(set(job_ids))
        if not job_ids:
            return []
    sql = (
        "SELECT job_id, start_ts, end_ts, running_since, elapsed_seconds, time_min "
        "FROM spray_batch_jobs WHERE batch_id=?"
    )
    params = [batch_id]
    if job_ids:
        placeholders = ','.join('?' for _ in job_ids)
        sql += f" AND job_id IN ({placeholders})"
        params.extend(job_ids)
    return list(db.execute(sql, tuple(params)).fetchall())


def _start_jobs(db, batch_id, job_ids=None, now_dt=None):
    rows = _select_batch_jobs(db, batch_id, job_ids)
    if not rows:
        return set()
    now_dt = now_dt or datetime.utcnow()
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    started = set()
    for row in rows:
        job_id = row['job_id']
        if row['end_ts']:
            continue
        if row['running_since']:
            continue
        if row['start_ts'] is None:
            db.execute(
                "UPDATE spray_batch_jobs SET start_ts = ? WHERE batch_id=? AND job_id=? AND start_ts IS NULL",
                (now_str, batch_id, job_id),
            )
        db.execute(
            "UPDATE spray_batch_jobs SET running_since = ? WHERE batch_id=? AND job_id=? AND running_since IS NULL AND end_ts IS NULL",
            (now_str, batch_id, job_id),
        )
        started.add(job_id)
    return started


def _pause_jobs(db, batch_id, job_ids=None, now_dt=None):
    rows = _select_batch_jobs(db, batch_id, job_ids)
    if not rows:
        return set()
    now_dt = now_dt or datetime.utcnow()
    paused = set()
    for row in rows:
        running_since = row['running_since']
        if not running_since:
            continue
        job_id = row['job_id']
        elapsed = row['elapsed_seconds'] or 0.0
        started = _parse_ts(running_since)
        if started:
            elapsed += max(0.0, (now_dt - started).total_seconds())
        minutes = _seconds_to_minutes(elapsed)
        db.execute(
            "UPDATE spray_batch_jobs SET running_since=NULL, elapsed_seconds=?, time_min=? WHERE batch_id=? AND job_id=?",
            (elapsed, minutes, batch_id, job_id),
        )
        paused.add(job_id)
    return paused


def _stop_jobs(db, batch_id, job_ids=None, now_dt=None):
    rows = _select_batch_jobs(db, batch_id, job_ids)
    if not rows:
        return set()
    now_dt = now_dt or datetime.utcnow()
    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    _pause_jobs(db, batch_id, job_ids, now_dt)
    rows = _select_batch_jobs(db, batch_id, job_ids)
    stopped = set()
    for row in rows:
        job_id = row['job_id']
        elapsed = row['elapsed_seconds'] or 0.0
        minutes = _seconds_to_minutes(elapsed)
        db.execute(
            "UPDATE spray_batch_jobs SET time_min=? WHERE batch_id=? AND job_id=?",
            (minutes, batch_id, job_id),
        )
        db.execute(
            "UPDATE spray_batch_jobs SET end_ts = COALESCE(end_ts, ?) WHERE batch_id=? AND job_id=?",
            (now_str, batch_id, job_id),
        )
        stopped.add(job_id)
    return stopped




@bp.get("/sprayer/hitlist")
def sprayer_hit_list():
    if not has_perm("see_job_screen"):
        return redirect(url_for("nav"))
    db = get_db()
    powders = db.execute(
        "SELECT id, powder_color, manufacturer, in_stock FROM powders ORDER BY LOWER(powder_color)"
    ).fetchall()
    jobs = db.execute(
        """
        SELECT DISTINCT j.id, j.company, j.color, j.due_by, j.description, j.priority,
                        jp.powder_id, p.powder_color, p.manufacturer,
                        CASE j.priority
                          WHEN 'Emergency' THEN 1
                          WHEN 'Rush' THEN 2
                          WHEN 'Semi Rush' THEN 3
                          ELSE 4
                        END AS pr_sort,
                        CASE WHEN j.due_by IS NULL OR j.due_by='' THEN 1 ELSE 0 END AS due_null
          FROM jobs j
          JOIN job_powders jp ON jp.job_id = j.id
          JOIN powders p ON p.id = jp.powder_id
         WHERE COALESCE(j.archived,0) = 0
           AND (j.completed_at IS NULL OR TRIM(j.completed_at)='')
           AND j.on_screen = 1
         ORDER BY pr_sort, due_null, j.due_by ASC, p.powder_color ASC, j.id DESC
        """
    ).fetchall()
    return render_template("sprayer/hitlist.html", jobs=jobs, powders=powders, is_admin=is_admin())


@bp.get("/sprayer/batches")
def sprayer_batches():
    if not has_perm("see_job_screen") and not is_admin():
        return redirect(url_for("nav"))
    db = get_db()
    powders = db.execute(
        "SELECT id, powder_color, manufacturer, in_stock AS on_hand_kg FROM powders ORDER BY LOWER(powder_color)"
    ).fetchall()
    open_batches = db.execute(
        """
        SELECT sb.*, p.powder_color, p.manufacturer
          FROM spray_batch sb JOIN powders p ON p.id=sb.powder_id
         WHERE sb.ended_at IS NULL
         ORDER BY sb.started_at DESC
        """
    ).fetchall()
    recent = db.execute(
        """
        SELECT sb.*, p.powder_color, p.manufacturer
          FROM spray_batch sb JOIN powders p ON p.id=sb.powder_id
         WHERE sb.ended_at IS NOT NULL
         ORDER BY sb.ended_at DESC
         LIMIT 20
        """
    ).fetchall()
    return render_template("sprayer/batches.html",
                           powders=powders, open_batches=open_batches, recent=recent,
                           is_admin=is_admin())


@bp.post("/sprayer/batches/start")
def sprayer_batches_start():
    if not is_admin():
        abort(403)
    powder_id = int(request.form.get("powder_id", 0))
    role = (request.form.get("role") or "primary").strip()
    operator = (request.form.get("operator") or "").strip()
    note = (request.form.get("note") or "").strip()
    try:
        start_weight_kg = float(request.form.get("start_weight_kg", "0") or "0")
    except Exception:
        return abort(400, "Invalid start weight")
    if powder_id <= 0 or start_weight_kg <= 0:
        return abort(400, "Powder and positive start weight required")
    db = get_db()
    row = db.execute(
        """INSERT INTO spray_batch (powder_id, role, operator, note, start_weight_kg)
              VALUES (?,?,?,?,?) RETURNING id""",
        (powder_id, role, operator, note, start_weight_kg),
    ).fetchone()
    batch_id = row["id"] if row else None
    if not batch_id:
        abort(500, "Failed to create batch")
    return redirect(url_for("sprayer.sprayer_batch_detail", batch_id=batch_id))


@bp.get("/sprayer/batches/<int:batch_id>")
def sprayer_batch_detail(batch_id: int):
    db = get_db()
    batch = db.execute("SELECT * FROM spray_batch WHERE id=?", (batch_id,)).fetchone()
    if not batch:
        abort(404)
    powder = db.execute("SELECT powder_color, manufacturer FROM powders WHERE id=?", (batch["powder_id"],)).fetchone()
    job_rows = db.execute(
        """
        SELECT j.*, sbj.time_min, sbj.start_ts, sbj.end_ts, sbj.elapsed_seconds, sbj.running_since
          FROM spray_batch_jobs sbj
          JOIN jobs j ON j.id = sbj.job_id
         WHERE sbj.batch_id=?
         ORDER BY sbj.job_id DESC
        """,
        (batch_id,),
    ).fetchall()
    now_dt = datetime.utcnow()
    attached = []
    for row in job_rows:
        job = dict(row)
        running_since = job.get("running_since")
        elapsed_seconds = job.get("elapsed_seconds") or 0.0
        if not elapsed_seconds and job.get("time_min"):
            try:
                elapsed_seconds = float(job["time_min"]) * 60.0
            except (TypeError, ValueError):
                pass
        started = _parse_ts(running_since)
        if started:
            elapsed_seconds += max(0.0, (now_dt - started).total_seconds())
        job["elapsed_seconds"] = elapsed_seconds
        job["elapsed_minutes"] = round(elapsed_seconds / 60.0, 1) if elapsed_seconds else 0.0
        job["is_running"] = bool(running_since) and job.get("end_ts") is None
        job["is_complete"] = job.get("end_ts") is not None
        job["is_paused"] = bool(job.get("start_ts")) and not job["is_running"] and not job["is_complete"]
        attached.append(job)
    candidates = db.execute(
        """
        SELECT j.id, j.company, j.color, j.due_by
          FROM jobs j
         WHERE COALESCE(j.archived,0)=0
           AND (j.completed_at IS NULL OR TRIM(j.completed_at)='')
           AND j.on_screen=1
           AND NOT EXISTS (
             SELECT 1 FROM spray_batch_jobs sbj
             WHERE sbj.batch_id=? AND sbj.job_id=j.id
           )
         ORDER BY j.id DESC
        """,
        (batch_id,),
    ).fetchall()
    return render_template(
        "sprayer/batch.html",
        batch=batch,
        sb=batch,
        powder=powder,
        attached=attached,
        jobs=attached,
        candidates=candidates,
        is_admin=is_admin(),
    )


@bp.get("/sprayer/candidates.json")
def sprayer_candidates_json():
    db = get_db()
    rows = db.execute(
        """
        SELECT j.id, j.company, j.color, j.due_by, j.priority
          FROM jobs j
         WHERE COALESCE(j.archived,0)=0
           AND (j.completed_at IS NULL OR TRIM(j.completed_at)='')
         ORDER BY j.on_screen DESC, j.priority ASC, j.due_by ASC NULLS LAST, j.id DESC
        """
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@bp.get("/sprayer/hitlist.json")
def sprayer_hitlist_json():
    db = get_db()
    rows = db.execute(
        """
        SELECT j.id, j.company, j.color, j.due_by, j.description, j.priority
          FROM jobs j
         WHERE COALESCE(j.archived,0)=0
           AND (j.completed_at IS NULL OR TRIM(j.completed_at)='')
           AND j.on_screen=1
         ORDER BY j.priority ASC, j.due_by ASC NULLS LAST, j.id DESC
        """
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@bp.post("/sprayer/batches/<int:batch_id>/add_job")
def sprayer_batch_add_job(batch_id: int):
    guard = require_admin()
    if guard:
        return guard
    job_ids: list[int] = []
    for val in request.form.getlist("job_id"):
        try:
            job_ids.append(int(val))
        except Exception:
            pass
    if not job_ids:
        abort(400)
    db = get_db()
    if not db.execute("SELECT 1 FROM spray_batch WHERE id=?", (batch_id,)).fetchone():
        abort(404)
    for jid in job_ids:
        db.execute("INSERT OR IGNORE INTO spray_batch_jobs (batch_id, job_id) VALUES (?,?)", (batch_id, jid))
    db.commit()
    return redirect(url_for("sprayer.sprayer_batch_detail", batch_id=batch_id))


@bp.post("/sprayer/batches/<int:batch_id>/job/<int:job_id>/start")
def sprayer_job_start(batch_id: int, job_id: int):
    if not is_admin():
        abort(403)
    db = get_db()
    db.execute("INSERT OR IGNORE INTO spray_batch_jobs (batch_id, job_id) VALUES (?,?)", (batch_id, job_id))
    _start_jobs(db, batch_id, [job_id])
    db.commit()
    return jsonify(ok=True)


@bp.post("/sprayer/batches/<int:batch_id>/job/<int:job_id>/end")
def sprayer_job_end(batch_id: int, job_id: int):
    if not is_admin():
        abort(403)
    db = get_db()
    _stop_jobs(db, batch_id, [job_id])
    db.commit()
    return jsonify(ok=True)


@bp.post("/sprayer/batches/<int:batch_id>/start_all")
def sprayer_batch_start_all(batch_id: int):
    if not is_admin():
        abort(403)
    db = get_db()
    started = _start_jobs(db, batch_id)
    db.commit()
    return jsonify(ok=True, started=len(started))


@bp.post("/sprayer/batches/<int:batch_id>/pause_all")
def sprayer_batch_pause_all(batch_id: int):
    if not is_admin():
        abort(403)
    db = get_db()
    paused = _pause_jobs(db, batch_id)
    db.commit()
    return jsonify(ok=True, paused=len(paused))


@bp.post("/sprayer/batches/<int:batch_id>/resume_all")
def sprayer_batch_resume_all(batch_id: int):
    if not is_admin():
        abort(403)
    db = get_db()
    resumed = _start_jobs(db, batch_id)
    db.commit()
    return jsonify(ok=True, resumed=len(resumed))


@bp.post("/sprayer/batches/<int:batch_id>/stop_all")
def sprayer_batch_stop_all(batch_id: int):
    if not is_admin():
        abort(403)
    db = get_db()
    stopped = _stop_jobs(db, batch_id)
    db.commit()
    return jsonify(ok=True, stopped=len(stopped))


@bp.post("/sprayer/batches/<int:batch_id>/close")
def sprayer_batch_close(batch_id: int):
    if not is_admin():
        abort(403)
    db = get_db()
    sb = db.execute("SELECT * FROM spray_batch WHERE id=?", (batch_id,)).fetchone()
    if not sb:
        abort(404)
    if sb["ended_at"]:
        return redirect(url_for("sprayer.sprayer_batch_detail", batch_id=batch_id))
    try:
        end_weight_kg = float(request.form.get("end_weight_kg", "0") or "0")
    except Exception:
        return abort(400, "Invalid end weight")
    if end_weight_kg < 0:
        return abort(400, "End weight must be >= 0")

    ended_at = datetime.utcnow()
    ended_at_str = ended_at.strftime("%Y-%m-%d %H:%M:%S")
    start_dt = datetime.strptime(sb["started_at"], "%Y-%m-%d %H:%M:%S")
    duration_min = max(0.0, (ended_at - start_dt).total_seconds() / 60.0)
    used_kg = max(0.0, float(sb["start_weight_kg"] or 0) - end_weight_kg)

    _stop_jobs(db, batch_id, now_dt=ended_at)

    rows = db.execute(
        "SELECT job_id, start_ts, end_ts, elapsed_seconds, time_min FROM spray_batch_jobs WHERE batch_id=?",
        (batch_id,),
    ).fetchall()
    job_ids = [r["job_id"] for r in rows]

    job_minutes = {}
    missing_ids = []
    for r in rows:
        seconds_val = r["elapsed_seconds"] or 0.0
        minutes_val = None
        if seconds_val > 0:
            minutes_val = seconds_val / 60.0
        elif r["time_min"] not in (None, 0, 0.0):
            try:
                minutes_val = float(r["time_min"])
                seconds_val = minutes_val * 60.0
            except (TypeError, ValueError):
                minutes_val = None
        if minutes_val is None and r["start_ts"] and r["end_ts"]:
            try:
                st = datetime.strptime(r["start_ts"], "%Y-%m-%d %H:%M:%S")
                en = datetime.strptime(r["end_ts"], "%Y-%m-%d %H:%M:%S")
                seconds_val = max(0.0, (en - st).total_seconds())
                minutes_val = seconds_val / 60.0
            except Exception:
                minutes_val = None
        if minutes_val is not None:
            job_minutes[r["job_id"]] = (minutes_val, seconds_val)
        else:
            missing_ids.append(r["job_id"])

    if missing_ids:
        per = (duration_min / len(job_ids)) if job_ids else 0.0
        seconds_per = per * 60.0
        for jid in missing_ids:
            job_minutes[jid] = (per, seconds_per)

    for jid, (minutes_val, seconds_val) in job_minutes.items():
        db.execute(
            "UPDATE spray_batch_jobs SET time_min=?, elapsed_seconds=? WHERE batch_id=? AND job_id=?",
            (round(minutes_val, 3), round(seconds_val, 3), batch_id, jid),
        )

    db.execute(
        """UPDATE spray_batch
             SET ended_at=?, end_weight_kg=?, used_kg=?, duration_min=?
           WHERE id=?""",
        (ended_at_str, end_weight_kg, used_kg, duration_min, batch_id),
    )

    mark_sprayed = request.form.getlist("mark_sprayed")
    mark_finished = request.form.getlist("mark_finished")
    if mark_finished:
        db.execute(
            f"UPDATE jobs SET completed_at=?, on_screen=0 WHERE id IN ({','.join('?'*len(mark_finished))})",
            (ended_at_str, *mark_finished),
        )

    if used_kg > 0:
        db.execute(
            "INSERT INTO powder_usage (powder_id, job_id, used_kg, note) VALUES (?,?,?,?)",
            (sb["powder_id"], None, used_kg, f"batch #{batch_id}"),
        )
    db.execute(
        """UPDATE powders
             SET in_stock = ?, last_weighed_kg = ?, last_weighed_at = ?
           WHERE id=?""",
        (end_weight_kg, end_weight_kg, ended_at_str, sb["powder_id"]),
    )
    db.commit()
    return redirect(url_for("sprayer.sprayer_batches"))


@bp.post("/sprayer/batches/<int:batch_id>/job/<int:job_id>/remove")
def sprayer_job_remove(batch_id: int, job_id: int):
    if not is_admin():
        abort(403)
    db = get_db()
    db.execute("DELETE FROM spray_batch_jobs WHERE batch_id=? AND job_id=?", (batch_id, job_id))
    db.commit()
    return redirect(url_for("sprayer.sprayer_batch_detail", batch_id=batch_id))


