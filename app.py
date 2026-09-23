"""Burhanuddin Malik — personal website server.

One small Python program that serves:
  /            the public website
  /admin       the private management portal (owner only)
  /private     the read-only viewer portal (viewers + owner preview)
  /api/...     the data behind all three
"""
import csv, datetime as dt, hashlib, hmac, io, json, os, re, secrets, shutil, sqlite3, threading, time, zipfile
from urllib.parse import urlparse

from flask import Flask, Response, abort, g, jsonify, redirect, request, send_file, send_from_directory, session
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash

from seed import seed_items

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("DATA_DIR", os.path.join(BASE, "data"))
DB_PATH = os.path.join(DATA, "site.db")
UP_PUB = os.path.join(DATA, "uploads", "public")
UP_PRIV = os.path.join(DATA, "uploads", "private")
BK = os.path.join(DATA, "backups")
STATIC = os.path.join(BASE, "static")
for d in (UP_PUB, UP_PRIV, BK):
    os.makedirs(d, exist_ok=True)

PUBLIC_KINDS = ["project", "gallery", "journey", "achievement", "post"]
ARCHIVE = {"detail": "Full Details", "special": "Special Achievements", "artwork": "Private Artwork",
           "appreciation": "Appreciation / Testimonials", "reflection": "Lessons & Reflections",
           "journal": "Personal Journal", "file": "Files / Documents / Photos"}
PRIVATE_KINDS = list(ARCHIVE)
ALL_KINDS = PUBLIC_KINDS + PRIVATE_KINDS
KIND_LABEL = {"detail": "Full detail", "project": "Project", "gallery": "Artwork", "journey": "Journey milestone",
              "achievement": "Achievement", "post": "Blog post", "special": "Special achievement",
              "artwork": "Private artwork", "appreciation": "Appreciation entry",
              "reflection": "Reflection", "journal": "Journal entry", "file": "File"}
PUBLIC_SETTINGS = [
    "instagram", "whatsapp", "email", "hero_photo", "about_photo", "about_growth_photo",
    "home_name", "home_tagline", "home_intro",
    "home_btn1_label", "home_btn1_link", "home_btn2_label", "home_btn2_link",
    "home_feat_title", "home_band_title", "home_band_text",
    "home_quote", "home_quote_body", "home_blog_title", "home_contact_title",
    "about_title", "about_who_text", "about_interests", "about_growth_text",
    "about_creativity_text", "about_curiosity_text", "about_drives_text",
    "about_education_items", "about_education_path", "about_learning_items",
    "theme_default", "theme_enabled",
    "linkedin", "github", "twitter", "contact_heading", "contact_intro", "contact_other_links"
]
DEFAULT_ROLE_SECTIONS = {"A": PRIVATE_KINDS[:], "B": ["special", "appreciation", "reflection"], "C": ["special"]}
LV = {"A": 3, "B": 2, "C": 1}
ACCESS_RANK = {"C": 1, "B": 2, "A": 3, "O": 99}


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today():
    return dt.datetime.now(dt.timezone.utc).date()


def secret():
    s = os.environ.get("SECRET_KEY")
    if s:
        return s
    p = os.path.join(DATA, "secret.key")
    if not os.path.exists(p):
        with open(p, "w") as f:
            f.write(secrets.token_hex(32))
        os.chmod(p, 0o600)
    return open(p).read().strip()


app = Flask(__name__, static_folder=None)
if os.environ.get("TRUST_PROXY", "1") == "1":
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
app.config.update(
    SECRET_KEY=secret(), SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("HTTPS", "0") == "1",
    MAX_CONTENT_LENGTH=25 * 1024 * 1024, PERMANENT_SESSION_LIFETIME=dt.timedelta(days=7))

# ------------------------------------------------------------------ database
SCHEMA = """
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, name TEXT, email TEXT DEFAULT '', role TEXT, pw TEXT,
  sections TEXT DEFAULT '[]', active INTEGER DEFAULT 1, created TEXT, updated TEXT DEFAULT '', last_login TEXT);
CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY, kind TEXT, slug TEXT, title TEXT, data TEXT DEFAULT '{}',
  status TEXT DEFAULT 'published', access TEXT DEFAULT 'A', pos INTEGER DEFAULT 0, created TEXT, updated TEXT);
CREATE INDEX IF NOT EXISTS ix_items ON items(kind, status);
CREATE TABLE IF NOT EXISTS hits(id INTEGER PRIMARY KEY, ts TEXT, day TEXT, vid TEXT, path TEXT, kind TEXT, slug TEXT,
  src TEXT, device TEXT, secs REAL DEFAULT 0, sid TEXT);
CREATE INDEX IF NOT EXISTS ix_hits_day ON hits(day);
CREATE INDEX IF NOT EXISTS ix_hits_sid ON hits(sid);
CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY, ts TEXT, design INT, content INT, navigation INT, overall INT, comment TEXT);
CREATE TABLE IF NOT EXISTS contacts(id INTEGER PRIMARY KEY, ts TEXT, name TEXT, email TEXT, message TEXT, read INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS activity(id INTEGER PRIMARY KEY, ts TEXT, actor TEXT, action TEXT, obj TEXT, area TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS passcodes(id INTEGER PRIMARY KEY, label TEXT, role TEXT, pw TEXT, sections TEXT DEFAULT '[]',
  active INTEGER DEFAULT 1, ver TEXT, created TEXT, last_used TEXT, uses INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE IF NOT EXISTS backups(id INTEGER PRIMARY KEY, ts TEXT, name TEXT UNIQUE, kind TEXT, size INT, status TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS media(id INTEGER PRIMARY KEY, name TEXT UNIQUE, original_name TEXT, ext TEXT, size INT, is_private INT DEFAULT 0,
  title TEXT DEFAULT '', caption TEXT DEFAULT '', alt TEXT DEFAULT '', project TEXT DEFAULT '', pos INTEGER DEFAULT 0, created TEXT);
CREATE INDEX IF NOT EXISTS ix_media_ext ON media(ext);
"""


def connect():
    c = sqlite3.connect(DB_PATH, timeout=15)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA foreign_keys=ON")
    return c


def db():
    if "db" not in g:
        g.db = connect()
    return g.db


@app.teardown_appcontext
def _close(_):
    d = g.pop("db", None)
    if d:
        d.close()


def qa(sql, *a):
    return [dict(r) for r in db().execute(sql, a).fetchall()]


def q1(sql, *a):
    r = db().execute(sql, a).fetchone()
    return dict(r) if r else None


def ex(sql, *a):
    c = db().execute(sql, a)
    db().commit()
    return c


def sync_media(c):
    for is_priv, folder in ((0, UP_PUB), (1, UP_PRIV)):
        if os.path.exists(folder):
            for fname in os.listdir(folder):
                fpath = os.path.join(folder, fname)
                if os.path.isfile(fpath) and NAME_RE.match(fname):
                    if not c.execute("SELECT 1 FROM media WHERE name=?", (fname,)).fetchone():
                        sz = os.path.getsize(fpath)
                        ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
                        c.execute("INSERT OR IGNORE INTO media(name, original_name, ext, size, is_private, created) VALUES(?,?,?,?,?,?)",
                                  (fname, fname, ext, sz, is_priv, now()))


def init_db():
    c = connect()
    c.executescript(SCHEMA)
    for col, ctype in (("title", "TEXT DEFAULT ''"), ("caption", "TEXT DEFAULT ''"), ("alt", "TEXT DEFAULT ''"), ("project", "TEXT DEFAULT ''"), ("pos", "INTEGER DEFAULT 0")):
        try:
            c.execute(f"ALTER TABLE media ADD COLUMN {col} {ctype}")
        except sqlite3.OperationalError:
            pass
    for col, ctype in (("updated", "TEXT DEFAULT ''"), ("email", "TEXT DEFAULT ''")):
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col} {ctype}")
        except sqlite3.OperationalError:
            pass
    env_pw = os.environ.get("OWNER_PASSWORD", "").strip()
    if not c.execute("SELECT 1 FROM users WHERE role='owner'").fetchone():
        pw = env_pw or secrets.token_urlsafe(12)
        c.execute("INSERT INTO users(username,name,role,pw,sections,created) VALUES('owner','Burhanuddin','owner',?,'[]',?)",
                  (generate_password_hash(pw), now()))
        if not env_pw:
            print("=" * 60 + f"\n FIRST RUN. Owner login:\n   username: owner\n   password: {pw}\n"
                  " Change it in Admin > Settings.\n" + "=" * 60, flush=True)
    elif env_pw:
        c.execute("UPDATE users SET pw=? WHERE role='owner'", (generate_password_hash(env_pw),))
    if not c.execute("SELECT 1 FROM items LIMIT 1").fetchone():
        for it in seed_items():
            c.execute("INSERT INTO items(kind,slug,title,data,status,access,pos,created,updated) VALUES(?,?,?,?,?,?,?,?,?)",
                      (it["kind"], it["slug"], it["title"], json.dumps(it["data"], ensure_ascii=False),
                       "published", "A", it.get("pos", 0), now(), now()))
    sync_media(c)
    c.commit()
    sync_backups(c)
    c.close()


def setting(k, default=None):
    r = q1("SELECT v FROM settings WHERE k=?", k)
    return r["v"] if r else default


def put_setting(k, v):
    ex("INSERT INTO settings(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", k, v)


def role_sections():
    try:
        d = json.loads(setting("role_sections", "") or "")
        return {k: [s for s in d.get(k, []) if s in ARCHIVE] for k in "ABC"}
    except Exception:
        return DEFAULT_ROLE_SECTIONS


# ------------------------------------------------------------------ auth, security helpers
def me():
    if "_me" not in g:
        uid = session.get("uid")
        g._me = q1("SELECT * FROM users WHERE id=? AND active=1", uid) if uid else None
    return g._me


def is_owner():
    u = me()
    return bool(u and u["role"] == "owner")


def owner_only(f):
    from functools import wraps

    @wraps(f)
    def w(*a, **k):
        if not me():
            return jsonify(error="Please sign in."), 401
        if not is_owner():
            return jsonify(error="Owner access only."), 403
        return f(*a, **k)
    return w


def log(action, obj="", area="", actor=None):
    if actor is None:
        u = me()
        actor = u["username"] if u else "visitor"
    ex("INSERT INTO activity(ts,actor,action,obj,area) VALUES(?,?,?,?,?)", now(), actor, action, str(obj)[:200], area)


_rl = {}


def rl_over(key, n, per):
    t = time.time()
    _rl[key] = [x for x in _rl.get(key, []) if t - x < per]
    return len(_rl[key]) >= n


def rl_add(key):
    _rl.setdefault(key, []).append(time.time())


OPEN_POST = {"/api/login", "/api/logout", "/api/track", "/api/contact", "/api/feedback", "/api/private/unlock"}


@app.before_request
def guard():
    if request.method in ("POST", "PUT", "DELETE", "PATCH") and request.path.startswith("/api/") and request.path not in OPEN_POST:
        if session.get("uid") and not hmac.compare_digest(request.headers.get("X-CSRF", ""), session.get("csrf", "")):
            abort(403)


@app.after_request
def headers(r):
    r.headers["X-Content-Type-Options"] = "nosniff"
    r.headers["X-Frame-Options"] = "SAMEORIGIN"
    r.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    r.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if os.environ.get("HTTPS", "0") == "1":
        r.headers["Strict-Transport-Security"] = "max-age=31536000"
    if request.path.startswith(("/api/admin", "/api/private", "/api/me")):
        r.headers["Cache-Control"] = "no-store"
    return r


@app.errorhandler(ValueError)
def _bad(e):
    return jsonify(error=str(e)), 400


@app.errorhandler(401)
def _401(e):
    return jsonify(error="Authentication required."), 401


@app.errorhandler(403)
def _403(e):
    return jsonify(error="Not allowed. Refresh the page and try again."), 403


@app.errorhandler(404)
def _404(e):
    if request.path.startswith("/api/"):
        return jsonify(error="Endpoint not found."), 404
    return html("index.html"), 404


@app.errorhandler(413)
def _413(e):
    return jsonify(error="That file is too large (25 MB maximum)."), 413


@app.errorhandler(500)
def _500(e):
    return jsonify(error="An internal server error occurred. Please try again later."), 500



@app.post("/api/login")
def login():
    j = request.get_json(silent=True) or {}
    un = str(j.get("username", "")).strip().lower()[:60]
    pw = str(j.get("password", ""))[:200]
    key = f"login:{request.remote_addr}:{un}"
    key_ip = f"login_ip:{request.remote_addr}"
    if rl_over(key, 6, 900) or rl_over(key_ip, 25, 900):
        log("Sign-in blocked after too many attempts", un, "security", actor="security")
        return jsonify(error="Too many attempts. Please wait 15 minutes and try again."), 429
    u = q1("SELECT * FROM users WHERE username=? AND active=1", un)
    ok = check_password_hash(u["pw"] if u else DUMMY, pw) and bool(u)
    if not ok:
        rl_add(key)
        rl_add(key_ip)
        log("Failed sign-in", un, "security", actor="security")
        return jsonify(error="Wrong username or password."), 401
    session.clear()
    session.permanent = True
    session["uid"] = u["id"]
    session["csrf"] = secrets.token_urlsafe(24)
    ex("UPDATE users SET last_login=? WHERE id=?", now(), u["id"])
    log("Signed in", u["username"], "security", actor=u["username"])
    return jsonify(role=u["role"], name=u["name"], csrf=session["csrf"])


DUMMY = generate_password_hash("not-a-real-password")


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)


@app.get("/api/me")
def whoami():
    u = me() or passcode_user()
    if not u:
        return jsonify(role=None)
    return jsonify(role=u["role"], name=u["name"], csrf=session.get("csrf"))


@app.post("/api/admin/password")
@owner_only
def change_password():
    j = request.get_json(silent=True) or {}
    key = f"admin_pw:{me()['id']}"
    if rl_over(key, 5, 900):
        return jsonify(error="Too many failed attempts. Please wait 15 minutes and try again."), 429
    if not check_password_hash(me()["pw"], str(j.get("current", ""))):
        rl_add(key)
        raise ValueError("Current password is wrong.")
    new = str(j.get("new", ""))
    if len(new) < 10:
        raise ValueError("New password must be at least 10 characters.")
    ex("UPDATE users SET pw=? WHERE id=?", generate_password_hash(new), me()["id"])
    log("Owner password changed", "", "security")
    return jsonify(ok=True)


# ------------------------------------------------------------------ items (all content)
def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:80] or "item"


def unique_slug(kind, base, skip_id=None):
    s, n = base, 1
    while q1("SELECT 1 FROM items WHERE kind=? AND slug=? AND id!=?", kind, s, skip_id or -1):
        n += 1
        s = f"{base}-{n}"
    return s


def item_out(r):
    r = dict(r)
    r["data"] = json.loads(r["data"] or "{}")
    return r


def clean_item(j, kind):
    title = str(j.get("title", "")).strip()[:200]
    if not title:
        raise ValueError("Please add a title.")
    data = j.get("data") or {}
    if not isinstance(data, dict) or len(json.dumps(data)) > 300000:
        raise ValueError("The content is too large or invalid.")
    status = j.get("status") if j.get("status") in ("draft", "published", "unpublished") else "draft"
    access = j.get("access") if j.get("access") in ACCESS_RANK else "A"
    try:
        pos = int(j.get("pos") or 0)
    except (TypeError, ValueError):
        pos = 0
    return title, data, status, access, pos


def area_of(kind):
    return "archive" if kind in PRIVATE_KINDS else ("blog" if kind == "post" else "portfolio")


@app.get("/api/admin/items")
@owner_only
def items_list():
    kind = request.args.get("kind", "")
    if kind not in ALL_KINDS:
        raise ValueError("Unknown content type.")
    qs = request.args.get("q", "").strip().lower()
    rows = [item_out(r) for r in db().execute("SELECT * FROM items WHERE kind=? ORDER BY pos, id DESC", (kind,))]
    if qs:
        rows = [r for r in rows if qs in (r["title"] + json.dumps(r["data"], ensure_ascii=False)).lower()]
    return jsonify(items=rows)


@app.get("/api/admin/items/<int:i>")
@owner_only
def item_get(i):
    r = q1("SELECT * FROM items WHERE id=?", i)
    if not r:
        abort(404)
    return jsonify(item_out(r))


@app.post("/api/admin/items")
@owner_only
def item_create():
    j = request.get_json(silent=True) or {}
    kind = j.get("kind")
    if kind not in ALL_KINDS:
        raise ValueError("Unknown content type.")
    title, data, status, access, pos = clean_item(j, kind)
    slug = unique_slug(kind, slugify(j.get("slug") or title))
    c = ex("INSERT INTO items(kind,slug,title,data,status,access,pos,created,updated) VALUES(?,?,?,?,?,?,?,?,?)",
           kind, slug, title, json.dumps(data, ensure_ascii=False), status, access, pos, now(), now())
    log(f"{KIND_LABEL[kind]} added", title, area_of(kind))
    if kind == "post" and status == "published":
        log("Blog post published", title, "blog")
    return jsonify(id=c.lastrowid, slug=slug)


@app.put("/api/admin/items/<int:i>")
@owner_only
def item_update(i):
    old = q1("SELECT * FROM items WHERE id=?", i)
    if not old:
        abort(404)
    j = request.get_json(silent=True) or {}
    title, data, status, access, pos = clean_item(j, old["kind"])
    slug = unique_slug(old["kind"], slugify(j.get("slug") or old["slug"] or title), i)
    ex("UPDATE items SET slug=?,title=?,data=?,status=?,access=?,pos=?,updated=? WHERE id=?",
       slug, title, json.dumps(data, ensure_ascii=False), status, access, pos, now(), i)
    log(f"{KIND_LABEL[old['kind']]} updated", title, area_of(old["kind"]))
    if old["kind"] == "post" and old["status"] != status:
        log("Blog post published" if status == "published" else "Blog post unpublished", title, "blog")
    return jsonify(id=i, slug=slug)


@app.delete("/api/admin/items/<int:i>")
@owner_only
def item_delete(i):
    old = q1("SELECT * FROM items WHERE id=?", i)
    if not old:
        abort(404)
    ex("DELETE FROM items WHERE id=?", i)
    log(f"{KIND_LABEL[old['kind']]} deleted", old["title"], area_of(old["kind"]))
    return jsonify(ok=True)


# ------------------------------------------------------------------ uploads
IMG_EXT = {"jpg", "jpeg", "png", "webp", "gif"}
DOC_EXT = {"pdf", "doc", "docx", "txt", "xlsx", "csv", "pptx"}


def is_image(head, ext):
    return ((ext in ("jpg", "jpeg") and head[:3] == b"\xff\xd8\xff") or (ext == "png" and head[:4] == b"\x89PNG")
            or (ext == "gif" and head[:4] == b"GIF8") or (ext == "webp" and head[:4] == b"RIFF" and head[8:12] == b"WEBP"))


@app.post("/api/admin/upload")
@owner_only
def upload():
    f = request.files.get("file")
    if not f or not f.filename:
        raise ValueError("Choose a file first.")
    private = request.form.get("private") == "1"
    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    if ext in IMG_EXT:
        if not is_image(f.stream.read(16), ext):
            raise ValueError("That file doesn't look like a real image.")
        f.stream.seek(0)
    elif ext in DOC_EXT and private:
        pass
    else:
        raise ValueError("This file type isn't allowed. Images (jpg, png, webp, gif) are allowed everywhere; documents (pdf, docx, xlsx, txt, csv, pptx) only in the private archive.")
    name = secrets.token_hex(16) + "." + ext
    f.save(os.path.join(UP_PRIV if private else UP_PUB, name))
    size = os.path.getsize(os.path.join(UP_PRIV if private else UP_PUB, name))
    orig_name = f.filename[:120]
    ex("INSERT OR REPLACE INTO media(name, original_name, ext, size, is_private, created) VALUES(?,?,?,?,?,?)",
       name, orig_name, ext, size, 1 if private else 0, now())
    log("File uploaded", orig_name, "archive" if private else "portfolio")
    return jsonify(url=(f"/api/private/file/{name}" if private else f"/uploads/{name}"), name=orig_name, size=size)


NAME_RE = re.compile(r"^[a-f0-9]{32}\.[a-z0-9]{2,5}$")


@app.get("/uploads/<name>")
def public_file(name):
    if not NAME_RE.match(name):
        abort(404)
    r = send_from_directory(UP_PUB, name, max_age=2592000)
    return r


# ------------------------------------------------------------------ media library & tools
@app.get("/api/admin/media")
@owner_only
def media_list():
    q = request.args.get("q", "").strip().lower()
    m_type = request.args.get("type", "all")
    vis = request.args.get("visibility", "all")
    sort = request.args.get("sort", "newest")

    sql = "SELECT * FROM media WHERE 1=1"
    params = []
    if q:
        sql += " AND (LOWER(original_name) LIKE ? OR LOWER(name) LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])
    if m_type == "images":
        sql += " AND ext IN ('jpg', 'jpeg', 'png', 'webp', 'gif')"
    elif m_type == "docs":
        sql += " AND ext NOT IN ('jpg', 'jpeg', 'png', 'webp', 'gif')"
    if vis == "public":
        sql += " AND is_private=0"
    elif vis == "private":
        sql += " AND is_private=1"

    if sort == "oldest":
        sql += " ORDER BY id ASC"
    elif sort == "name":
        sql += " ORDER BY original_name ASC"
    elif sort == "size":
        sql += " ORDER BY size DESC"
    else:
        sql += " ORDER BY id DESC"

    rows = qa(sql, *params)
    items = []
    for r in rows:
        items.append({
            "id": r["id"],
            "name": r["name"],
            "original_name": r["original_name"] or r["name"],
            "title": r.get("title") or "",
            "caption": r.get("caption") or "",
            "alt": r.get("alt") or "",
            "project": r.get("project") or "",
            "pos": r.get("pos") or 0,
            "ext": r["ext"],
            "size": r["size"],
            "is_private": bool(r["is_private"]),
            "created": r["created"],
            "url": f"/api/private/file/{r['name']}" if r["is_private"] else f"/uploads/{r['name']}"
        })
    return jsonify(items=items)


@app.put("/api/admin/media/<name>")
@owner_only
def media_update(name):
    if not NAME_RE.match(name):
        abort(404)
    j = request.get_json(silent=True) or {}
    title = str(j.get("title", "")).strip()[:200]
    caption = str(j.get("caption", "")).strip()[:500]
    alt = str(j.get("alt", "")).strip()[:300]
    proj = str(j.get("project", "")).strip()[:100]
    ex("UPDATE media SET title=?, caption=?, alt=?, project=? WHERE name=?", title, caption, alt, proj, name)
    log("Media updated", (title or name)[:100], "portfolio")
    return jsonify(ok=True)


@app.get("/api/admin/media/<name>/usage")
@owner_only
def media_usage(name):
    if not NAME_RE.match(name):
        abort(404)
    rows = qa("SELECT id, kind, title, slug FROM items WHERE data LIKE ?", f"%{name}%")
    s_rows = qa("SELECT k FROM settings WHERE v LIKE ?", f"%{name}%")
    uses = []
    for r in rows:
        uses.append({"type": "item", "kind": r["kind"], "title": r["title"], "id": r["id"], "slug": r["slug"]})
    for s in s_rows:
        uses.append({"type": "setting", "key": s["k"]})
    return jsonify(name=name, count=len(uses), uses=uses)


@app.delete("/api/admin/media/<name>")
@owner_only
def media_delete(name):
    if not NAME_RE.match(name):
        abort(404)
    m = q1("SELECT * FROM media WHERE name=?", name)
    for folder in (UP_PUB, UP_PRIV):
        p = os.path.join(folder, name)
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass
    ex("DELETE FROM media WHERE name=?", name)
    log("Media deleted", (m["original_name"] if m else name)[:100], "portfolio")
    return jsonify(ok=True)


@app.post("/api/admin/reorder")
@owner_only
def items_reorder():
    j = request.get_json(silent=True) or {}
    kind = str(j.get("kind", ""))
    ids = j.get("ids", [])
    if not isinstance(ids, list):
        raise ValueError("ids must be a list of item IDs.")
    for pos, item_id in enumerate(ids):
        ex("UPDATE items SET pos=? WHERE id=? AND kind=?", pos, item_id, kind)
    log(f"Reordered {kind} items", f"{len(ids)} items", area_of(kind))
    return jsonify(ok=True)


@app.get("/api/admin/search")
@owner_only
def admin_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify(items=[], media=[])
    like = f"%{q}%"
    rows = qa("SELECT id, kind, slug, title, status, access, updated, data FROM items WHERE title LIKE ? OR slug LIKE ? OR data LIKE ? ORDER BY updated DESC LIMIT 50", like, like, like)
    items = []
    for r in rows:
        d = json.loads(r["data"] or "{}")
        items.append({
            "id": r["id"],
            "kind": r["kind"],
            "slug": r["slug"],
            "title": r["title"],
            "status": r["status"],
            "access": r["access"],
            "updated": r["updated"],
            "subtitle": d.get("cat") or d.get("category") or d.get("year") or d.get("period") or ""
        })
    m_rows = qa("SELECT * FROM media WHERE name LIKE ? OR original_name LIKE ? ORDER BY created DESC LIMIT 20", like, like)
    media = [{**dict(m), "url": f"/api/private/file/{m['name']}" if m["is_private"] else f"/uploads/{m['name']}"} for m in m_rows]
    return jsonify(items=items, media=media)


# ------------------------------------------------------------------ public content
def flat(r):
    d = json.loads(r["data"] or "{}")
    return {"id": r["id"], "slug": r["slug"], "title": r["title"], "status": r["status"], "pos": r["pos"],
            "created": r["created"], **d}


@app.get("/api/content")
def content():
    prev = is_owner() and request.args.get("preview") == "1"
    rows = qa("SELECT * FROM items WHERE kind IN ('project','gallery','journey','achievement','post') ORDER BY pos, id")
    out = {k: [] for k in ("project", "gallery", "journey", "achievement", "post")}
    for r in rows:
        if r["status"] != "published" and not prev:
            continue
        x = flat(r)
        if r["kind"] == "post":
            x.pop("body", None)
        out[r["kind"]].append(x)
    out["post"].sort(key=lambda p: p.get("date") or p["created"], reverse=True)
    st = {k: setting(k, "") for k in PUBLIC_SETTINGS}
    return jsonify(projects=out["project"], gallery=out["gallery"], journey=out["journey"],
                   achievements=out["achievement"], posts=out["post"], settings=st, preview=prev)


@app.get("/api/post/<slug>")
def post_get(slug):
    r = q1("SELECT * FROM items WHERE kind='post' AND slug=?", slug)
    if not r or (r["status"] != "published" and not (is_owner() and request.args.get("preview") == "1")):
        abort(404)
    return jsonify(flat(r))


# ------------------------------------------------------------------ analytics (privacy-friendly)
BOT = re.compile(r"bot|crawl|spider|slurp|headless|preview|monitor|curl|python-requests|wget", re.I)
SLUG_RE = re.compile(r"^[a-z0-9-]{1,120}$")


def classify(ref, src):
    s = (src or "").lower()
    if s in ("instagram", "ig"):
        return "Instagram"
    if s in ("whatsapp", "wa"):
        return "WhatsApp"
    if s in ("google", "search"):
        return "Google/search"
    h = (urlparse(ref).hostname or "").lower() if ref else ""
    if not h or h == request.host.split(":")[0]:
        return "Direct"
    if "instagram" in h:
        return "Instagram"
    if "whatsapp" in h or h == "wa.me":
        return "WhatsApp"
    if any(x in h for x in ("google.", "bing.", "duckduckgo", "yahoo.", "ecosia", "brave.")):
        return "Google/search"
    return "Other"


@app.post("/api/track")
def track():
    j = request.get_json(silent=True) or {}
    ua = request.headers.get("User-Agent", "")
    if BOT.search(ua) or is_owner():
        return "", 204
    sid = str(j.get("sid", ""))[:32]
    if not re.match(r"^[a-z0-9]{6,32}$", sid):
        return "", 204
    if j.get("ev") == "time":
        try:
            secs = min(max(float(j.get("secs", 0)), 0), 1800)
        except (TypeError, ValueError):
            return "", 204
        ex("UPDATE hits SET secs=? WHERE sid=? AND secs<?", secs, sid, secs)
        return "", 204
    if rl_over("track:" + request.remote_addr, 120, 60):
        return "", 204
    rl_add("track:" + request.remote_addr)
    day = today().isoformat()
    salt = hmac.new(app.config["SECRET_KEY"].encode(), day.encode(), hashlib.sha256).hexdigest()
    vid = hashlib.sha256((salt + request.remote_addr + ua).encode()).hexdigest()[:16]  # never stored with IP
    kind = j.get("kind") if j.get("kind") in ("project", "post", "art") else ""
    slug = j.get("slug") if isinstance(j.get("slug"), str) and SLUG_RE.match(j.get("slug", "")) else ""
    try:
        w = int(j.get("w", 0))
    except (TypeError, ValueError):
        w = 0
    mobile_ua = re.search("mobile|android|iphone", ua, re.I)
    if re.search(r"ipad|tablet", ua, re.I) or (not mobile_ua and 600 <= w < 1024):
        dev = "Tablet"
    elif mobile_ua or 0 < w < 600:
        dev = "Mobile"
    else:
        dev = "Desktop"
    src = "Internal" if j.get("nav") else classify(str(j.get("ref", ""))[:300], str(j.get("src", ""))[:30])
    ex("INSERT INTO hits(ts,day,vid,path,kind,slug,src,device,sid) VALUES(?,?,?,?,?,?,?,?,?)",
       now(), day, vid, str(j.get("path", "/"))[:200], kind, slug, src, dev, sid)
    return "", 204


def date_range():
    r = request.args.get("range", "30d")
    t = today()
    if r == "today":
        a = b = t
    elif r in ("7d", "30d", "90d"):
        a, b = t - dt.timedelta(days=int(r[:-1]) - 1), t
    elif r == "custom":
        try:
            a, b = dt.date.fromisoformat(request.args.get("from", "")), dt.date.fromisoformat(request.args.get("to", ""))
        except ValueError:
            raise ValueError("Pick a valid start and end date.")
        if a > b:
            a, b = b, a
    else:
        a, b = dt.date(2000, 1, 1), t
    return r, a, b


def title_map():
    m = {}
    for r in qa("SELECT kind,slug,title,data FROM items WHERE kind IN ('project','gallery','post')"):
        d = json.loads(r["data"] or "{}")
        m[(r["kind"], r["slug"])] = (r["title"], d.get("cat") or d.get("category") or "")
    return m


@app.get("/api/admin/analytics")
@owner_only
def analytics():
    r, a, b = date_range()
    A, B = a.isoformat(), b.isoformat()
    c = db()
    base = "FROM hits WHERE day BETWEEN ? AND ? AND kind!='art'"
    views = c.execute(f"SELECT COUNT(*) {base}", (A, B)).fetchone()[0]
    visitors = c.execute(f"SELECT COALESCE(SUM(n),0) FROM (SELECT COUNT(DISTINCT vid) n {base} GROUP BY day)", (A, B)).fetchone()[0]
    daily = {row[0]: dict(day=row[0], views=row[1], visitors=row[2]) for row in
             c.execute(f"SELECT day,COUNT(*),COUNT(DISTINCT vid) {base} GROUP BY day", (A, B))}
    if r != "all":
        d = a
        while d <= b:
            daily.setdefault(d.isoformat(), dict(day=d.isoformat(), views=0, visitors=0))
            d += dt.timedelta(days=1)
    tm = title_map()

    def top(kind, n=8):
        rows = c.execute("SELECT slug,COUNT(*) n FROM hits WHERE day BETWEEN ? AND ? AND kind=? AND slug!='' GROUP BY slug ORDER BY n DESC LIMIT ?", (A, B, kind, n)).fetchall()
        tk = {"art": "gallery"}.get(kind, kind)
        return [dict(slug=x[0], title=(tm.get((tk, x[0])) or tm.get(("project", x[0])) or (x[0], ""))[0], views=x[1]) for x in rows]

    khat = 0
    for kind in ("project", "art"):
        for x in c.execute("SELECT kind,slug,COUNT(*) n FROM hits WHERE day BETWEEN ? AND ? AND kind=? GROUP BY slug", (A, B, kind)):
            cat = (tm.get(({"art": "gallery"}.get(x[0], x[0]), x[1])) or tm.get(("project", x[1])) or ("", ""))[1]
            khat += x[2] if cat == "Khat" else 0
    proj_eng = c.execute("SELECT COUNT(*),AVG(NULLIF(secs,0)) FROM hits WHERE day BETWEEN ? AND ? AND kind='project'", (A, B)).fetchone()
    post_eng = c.execute("SELECT COUNT(*),AVG(NULLIF(secs,0)) FROM hits WHERE day BETWEEN ? AND ? AND kind='post'", (A, B)).fetchone()
    avg_page = c.execute(f"SELECT AVG(secs) {base} AND secs>0", (A, B)).fetchone()[0]
    avg_site = c.execute(f"SELECT AVG(t) FROM (SELECT SUM(secs) t {base} GROUP BY day,vid HAVING t>0)", (A, B)).fetchone()[0]
    prev = None
    if r != "all":
        n = (b - a).days + 1
        pa, pb = (a - dt.timedelta(days=n)).isoformat(), (a - dt.timedelta(days=1)).isoformat()
        prev = c.execute(f"SELECT COUNT(*) {base}", (pa, pb)).fetchone()[0]
    return jsonify(
        range=r, **{"from": A, "to": B}, views=views, visitors=visitors, prev_views=prev, daily=sorted(daily.values(), key=lambda x: x["day"]),
        pages=[dict(path=x[0], views=x[1]) for x in c.execute(f"SELECT path,COUNT(*) n {base} GROUP BY path ORDER BY n DESC LIMIT 10", (A, B))],
        projects=top("project"), artworks=top("art"), articles=top("post"), khat_views=khat,
        sources=[dict(name=x[0], visits=x[1]) for x in c.execute(f"SELECT src,COUNT(*) n {base} AND src!='Internal' GROUP BY src ORDER BY n DESC", (A, B))],
        devices=[dict(name=x[0], visits=x[1]) for x in c.execute(f"SELECT device,COUNT(DISTINCT day||vid) n {base} GROUP BY device ORDER BY n DESC", (A, B))],
        engagement=dict(avg_time_site=avg_site, avg_time_page=avg_page,
                        featured=dict(views=proj_eng[0], avg_time=proj_eng[1]), blog=dict(views=post_eng[0], avg_time=post_eng[1])))


# ------------------------------------------------------------------ contact + feedback (public, anonymous)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@app.post("/api/contact")
def contact():
    j = request.get_json(silent=True) or {}
    if j.get("website"):  # honeypot: real people never fill this in
        return jsonify(ok=True)
    name, email, msg = str(j.get("name", "")).strip()[:100], str(j.get("email", "")).strip()[:200], str(j.get("message", "")).strip()[:4000]
    if not name or not msg or not EMAIL_RE.match(email):
        raise ValueError("Please fill in your name, a valid email and a message.")
    if rl_over("contact:" + request.remote_addr, 5, 3600):
        return jsonify(error="You've sent a few messages already. Please try again later."), 429
    rl_add("contact:" + request.remote_addr)
    ex("INSERT INTO contacts(ts,name,email,message) VALUES(?,?,?,?)", now(), name, email, msg)
    return jsonify(ok=True)


@app.post("/api/feedback")
def feedback():
    j = request.get_json(silent=True) or {}
    r = j.get("ratings") or {}

    def rate(k):
        v = r.get(k)
        return int(v) if isinstance(v, (int, float)) and 1 <= v <= 5 else None
    vals = [rate("Design"), rate("Content"), rate("Navigation"), rate("Overall Experience")]
    comment = str(j.get("comment", "")).strip()[:1000]
    if not any(vals) and not comment:
        raise ValueError("Please give at least one rating or a comment.")
    if rl_over("fb:" + request.remote_addr, 5, 3600):
        return jsonify(error="Thanks, we already received your feedback. Please try again later."), 429
    rl_add("fb:" + request.remote_addr)
    ex("INSERT INTO feedback(ts,design,content,navigation,overall,comment) VALUES(?,?,?,?,?,?)", now(), *vals, comment)
    return jsonify(ok=True)


@app.get("/api/admin/feedback")
@owner_only
def feedback_admin():
    a = db().execute("SELECT COUNT(*),AVG(design),AVG(content),AVG(navigation),AVG(overall) FROM feedback").fetchone()
    return jsonify(total=a[0], avg=dict(design=a[1], content=a[2], navigation=a[3], overall=a[4]),
                   trend=[dict(day=x[0], overall=x[1], count=x[2]) for x in db().execute(
                       "SELECT substr(ts,1,10) d,AVG(overall),COUNT(*) FROM feedback GROUP BY d ORDER BY d")],
                   items=qa("SELECT * FROM feedback ORDER BY id DESC LIMIT 300"))


@app.get("/api/admin/contacts")
@owner_only
def contacts_admin():
    return jsonify(items=qa("SELECT * FROM contacts ORDER BY id DESC LIMIT 500"))


@app.put("/api/admin/contacts/<int:i>")
@owner_only
def contacts_read(i):
    ex("UPDATE contacts SET read=? WHERE id=?", 1 if (request.get_json(silent=True) or {}).get("read", True) else 0, i)
    return jsonify(ok=True)


@app.delete("/api/admin/contacts/<int:i>")
@owner_only
def contacts_delete(i):
    ex("DELETE FROM contacts WHERE id=?", i)
    log("Message deleted", str(i), "portfolio")
    return jsonify(ok=True)


# ------------------------------------------------------------------ viewers + private archive
PC_HOURS = 72  # default access-password sign-in hours


def passcode_user():
    """A visitor who unlocked the private archive with primary password or shared access passcode."""
    pid = session.get("pc")
    if not pid or time.time() > session.get("pc_exp", 0):
        return None
    if pid == "primary":
        if session.get("pc_ver") != setting("archive_password_ver", "1"):
            return None
        role = session.get("pc_role", setting("archive_default_role", "B"))
        if role not in LV:
            role = "B"
        secs = role_sections().get(role, PRIVATE_KINDS[:])
        return dict(id=-999, username="pass:primary", name=session.get("pc_label", "Archive Viewer"), role=role, sections=json.dumps(secs), active=1)
    if isinstance(pid, int):
        r = q1("SELECT * FROM passcodes WHERE id=? AND active=1", pid)
        if not r or r["ver"] != session.get("pc_ver"):
            return None
        return dict(id=-r["id"], username="pass:" + r["label"], name=r["label"], role=r["role"], sections=r["sections"], active=1)
    return None


@app.post("/api/private/unlock")
def unlock():
    arch_status = setting("archive_status", "enabled")
    if arch_status == "disabled" and not is_owner():
        return jsonify(error="The private archive is currently disabled."), 403
    if arch_status == "maintenance" and not is_owner():
        return jsonify(error="The private archive is temporarily offline for maintenance."), 403

    j = request.get_json(silent=True) or {}
    pw = str(j.get("password", ""))[:200]
    key = "unlock:" + request.remote_addr
    if rl_over(key, 6, 900):
        log("Access-password attempts blocked", "", "security", actor="security")
        return jsonify(error="Too many attempts. Please wait 15 minutes and try again."), 429

    hours = int(setting("archive_session_hours", "72") or 72)

    # 1. Primary Archive Password Check
    arch_hash = setting("archive_password_hash")
    if arch_hash and check_password_hash(arch_hash, pw):
        def_role = setting("archive_default_role", "B")
        if def_role not in LV:
            def_role = "B"
        session.clear()
        session.permanent = True
        session["pc"] = "primary"
        session["pc_ver"] = setting("archive_password_ver", "1")
        session["pc_role"] = def_role
        session["pc_label"] = "Archive Access"
        session["pc_exp"] = time.time() + hours * 3600
        session["csrf"] = secrets.token_urlsafe(24)
        log("Archive unlocked with primary password", "", "archive", actor="archive password")
        return jsonify(role=def_role, name="Private Archive Viewer", csrf=session["csrf"])

    # 2. Shared Passcodes Check
    hit = None
    for r in qa("SELECT * FROM passcodes WHERE active=1"):
        if check_password_hash(r["pw"], pw) and not hit:
            hit = r
    if hit:
        session.clear()
        session.permanent = True
        session["pc"] = hit["id"]
        session["pc_ver"] = hit["ver"]
        session["pc_role"] = hit["role"]
        session["pc_label"] = hit["label"]
        session["pc_exp"] = time.time() + hours * 3600
        session["csrf"] = secrets.token_urlsafe(24)
        ex("UPDATE passcodes SET last_used=?, uses=uses+1 WHERE id=?", now(), hit["id"])
        log("Archive unlocked with passcode", hit["label"], "archive", actor=hit["label"])
        return jsonify(role=hit["role"], name=hit["label"], csrf=session["csrf"])

    # Neither matched
    check_password_hash(DUMMY, pw)
    rl_add(key)
    log("Wrong archive password attempt", "", "security", actor="security")
    return jsonify(error="That password isn't right."), 401


def viewer_ctx(u):
    """What can this signed-in person see? Returns (rank, allowed sections, is_full_owner, label)."""
    if u["role"] == "owner":
        al, au = request.args.get("as_level"), request.args.get("as_user")
        ap = request.args.get("as_pass")
        if ap and ap.isdigit():
            p = q1("SELECT * FROM passcodes WHERE id=?", int(ap))
            if p:
                return LV[p["role"]], [s for s in json.loads(p["sections"] or "[]") if s in ARCHIVE], False, f"Access password “{p['label']}” (Level {p['role']})"
        if al in LV:
            return LV[al], role_sections()[al], False, f"Level {al} (default access)"
        if au and au.isdigit():
            v = q1("SELECT * FROM users WHERE id=? AND role IN ('A','B','C')", int(au))
            if v:
                return LV[v["role"]], [s for s in json.loads(v["sections"] or "[]") if s in ARCHIVE], False, f"{v['name']} (Level {v['role']})"
        return 99, PRIVATE_KINDS, True, "Owner"
    return LV[u["role"]], [s for s in json.loads(u["sections"] or "[]") if s in ARCHIVE], False, f"Level {u['role']}"


def can_see(item, rank, sections, full):
    if full:
        return True
    return item["status"] == "published" and item["kind"] in sections and rank >= ACCESS_RANK.get(item["access"], 99)


@app.get("/api/private/items")
def private_items():
    u = me() or passcode_user()
    if not u:
        return jsonify(error="Please sign in."), 401

    arch_status = setting("archive_status", "enabled")
    if arch_status == "disabled" and u.get("role") != "owner":
        return jsonify(error="The private archive is currently disabled."), 403
    if arch_status == "maintenance" and u.get("role") != "owner":
        return jsonify(error="The private archive is temporarily offline for maintenance."), 403

    rank, sections, full, label = viewer_ctx(u)
    rows = [item_out(r) for r in db().execute("SELECT * FROM items WHERE kind IN (%s) ORDER BY pos, id DESC" % ",".join("?" * len(PRIVATE_KINDS)), PRIVATE_KINDS)]
    vis = [r for r in rows if can_see(r, rank, sections, full)]
    title = setting("archive_title") or "Private Archive | Burhanuddin Malik"
    welcome = setting("archive_welcome") or "A curated collection of behind-the-scenes work, personal reflections, and milestone documentation."
    return jsonify(title=title, welcome=welcome, status=arch_status,
                   label=label, owner=u["role"] == "owner", name=u["name"],
                   sections=[dict(key=k, label=ARCHIVE[k]) for k in PRIVATE_KINDS if k in sections], items=vis)


@app.get("/api/private/file/<name>")
def private_file(name):
    u = me() or passcode_user()
    if not u:
        abort(401)
    arch_status = setting("archive_status", "enabled")
    if arch_status in ("disabled", "maintenance") and u.get("role") != "owner":
        abort(403)
    if not NAME_RE.match(name) or not os.path.exists(os.path.join(UP_PRIV, name)):
        abort(404)
    rank, sections, full, _ = viewer_ctx(u)
    rows = [item_out(r) for r in db().execute("SELECT * FROM items WHERE kind IN (%s) AND data LIKE ?" % ",".join("?" * len(PRIVATE_KINDS)), PRIVATE_KINDS + [f"%{name}%"])]
    if not full:
        if not any(can_see(r, rank, sections, False) for r in rows):
            abort(404)
    ext = name.rsplit(".", 1)[1].lower()
    dl_requested = request.args.get("dl") == "1"
    allow_dl = full or any((r.get("data", {}).get("allow_download") or False) for r in rows)
    as_attachment = (ext not in IMG_EXT and dl_requested and allow_dl)
    resp = send_from_directory(UP_PRIV, name, as_attachment=as_attachment)
    resp.headers["Cache-Control"] = "private, no-store"
    return resp


# ------------------------------------------------------------------ archive admin settings
@app.get("/api/admin/archive/settings")
@owner_only
def archive_settings_get():
    stats = {
        "total_items": q1("SELECT COUNT(*) c FROM items WHERE kind IN (%s)" % ",".join("?" * len(PRIVATE_KINDS)), *PRIVATE_KINDS)["c"],
        "published_items": q1("SELECT COUNT(*) c FROM items WHERE kind IN (%s) AND status='published'" % ",".join("?" * len(PRIVATE_KINDS)), *PRIVATE_KINDS)["c"],
        "draft_items": q1("SELECT COUNT(*) c FROM items WHERE kind IN (%s) AND status!='published'" % ",".join("?" * len(PRIVATE_KINDS)), *PRIVATE_KINDS)["c"],
        "active_viewers": q1("SELECT COUNT(*) c FROM users WHERE role!='owner' AND active=1")["c"],
        "disabled_viewers": q1("SELECT COUNT(*) c FROM users WHERE role!='owner' AND active=0")["c"],
        "active_passcodes": q1("SELECT COUNT(*) c FROM passcodes WHERE active=1")["c"],
    }
    return jsonify(
        status=setting("archive_status", "enabled"),
        title=setting("archive_title", "Private Archive | Burhanuddin Malik"),
        welcome=setting("archive_welcome", "A curated collection of behind-the-scenes work, personal reflections, and milestone documentation."),
        session_hours=int(setting("archive_session_hours", "72") or 72),
        default_role=setting("archive_default_role", "B"),
        has_password=bool(setting("archive_password_hash")),
        password_changed_at=setting("archive_password_changed_at", ""),
        stats=stats,
        archive_sections=ARCHIVE,
        recent_activity=qa("SELECT * FROM activity WHERE area IN ('archive','viewers','security') ORDER BY id DESC LIMIT 20")
    )


@app.put("/api/admin/archive/settings")
@owner_only
def archive_settings_put():
    j = request.get_json(silent=True) or {}
    if "status" in j and j["status"] in ("enabled", "maintenance", "disabled"):
        put_setting("archive_status", j["status"])
    if "title" in j:
        put_setting("archive_title", str(j["title"]).strip()[:120])
    if "welcome" in j:
        put_setting("archive_welcome", str(j["welcome"]).strip()[:1000])
    if "session_hours" in j:
        put_setting("archive_session_hours", str(max(1, min(720, int(j["session_hours"] or 72)))))
    if "default_role" in j and j["default_role"] in LV:
        put_setting("archive_default_role", j["default_role"])
    log("Archive settings updated", j.get("status", ""), "archive")
    return jsonify(ok=True)


@app.post("/api/admin/archive/password")
@owner_only
def archive_password_post():
    j = request.get_json(silent=True) or {}
    new_pw = str(j.get("new_password", ""))
    confirm_pw = str(j.get("confirm_password", ""))
    if len(new_pw) < 8:
        raise ValueError("Password must be at least 8 characters.")
    if new_pw != confirm_pw:
        raise ValueError("Password confirmation does not match.")
    put_setting("archive_password_hash", generate_password_hash(new_pw))
    ts = now()
    put_setting("archive_password_changed_at", ts)
    put_setting("archive_password_ver", secrets.token_hex(8))
    log("Archive password changed", "All existing archive sessions revoked", "security")
    return jsonify(ok=True, changed_at=ts)


def viewer_out(u):
    return dict(id=u["id"], username=u["username"], name=u["name"], role=u["role"], active=bool(u["active"]),
                sections=json.loads(u["sections"] or "[]"), created=u["created"], last_login=u["last_login"])


def valid_sections(v):
    return [s for s in (v or []) if s in ARCHIVE]


@app.get("/api/admin/viewers")
@owner_only
def viewers_list():
    return jsonify(items=[viewer_out(u) for u in qa("SELECT * FROM users WHERE role!='owner' ORDER BY id")],
                   role_sections=role_sections(), archive=ARCHIVE)


@app.post("/api/admin/viewers")
@owner_only
def viewers_create():
    j = request.get_json(silent=True) or {}
    un = str(j.get("username", "")).strip().lower()
    if not re.match(r"^[a-z0-9._-]{3,30}$", un):
        raise ValueError("Username: 3-30 letters, numbers, dots, dashes.")
    if q1("SELECT 1 FROM users WHERE username=?", un):
        raise ValueError("That username is already taken.")
    role = j.get("role")
    if role not in LV:
        raise ValueError("Choose Level A, B or C.")
    pw = str(j.get("password") or "") or secrets.token_urlsafe(9)
    if len(pw) < 8:
        raise ValueError("Password must be at least 8 characters.")
    secs = valid_sections(j.get("sections")) if j.get("sections") is not None else role_sections()[role]
    c = ex("INSERT INTO users(username,name,role,pw,sections,created) VALUES(?,?,?,?,?,?)",
           un, str(j.get("name", "")).strip()[:80] or un, role, generate_password_hash(pw), json.dumps(secs), now())
    log("Viewer created", f"{un} (Level {role})", "viewers")
    return jsonify(id=c.lastrowid, password=pw)


@app.put("/api/admin/viewers/<int:i>")
@owner_only
def viewers_update(i):
    u = q1("SELECT * FROM users WHERE id=? AND role!='owner'", i)
    if not u:
        abort(404)
    j = request.get_json(silent=True) or {}
    role = j.get("role", u["role"])
    if role not in LV:
        raise ValueError("Choose Level A, B or C.")
    secs = valid_sections(j["sections"]) if "sections" in j else json.loads(u["sections"] or "[]")
    active = 1 if j.get("active", bool(u["active"])) else 0
    ex("UPDATE users SET name=?,role=?,sections=?,active=? WHERE id=?",
       str(j.get("name", u["name"])).strip()[:80], role, json.dumps(secs), active, i)
    if role != u["role"] or secs != json.loads(u["sections"] or "[]") or active != u["active"]:
        log("Viewer permission changed", f"{u['username']} (Level {role})", "viewers")
    if j.get("password"):
        if len(str(j["password"])) < 8:
            raise ValueError("Password must be at least 8 characters.")
        ex("UPDATE users SET pw=? WHERE id=?", generate_password_hash(str(j["password"])), i)
        log("Viewer password reset", u["username"], "viewers")
    return jsonify(ok=True)


@app.delete("/api/admin/viewers/<int:i>")
@owner_only
def viewers_delete(i):
    u = q1("SELECT * FROM users WHERE id=? AND role!='owner'", i)
    if not u:
        abort(404)
    ex("DELETE FROM users WHERE id=?", i)
    log("Viewer deleted", u["username"], "viewers")
    return jsonify(ok=True)


def passcode_out(r):
    return dict(id=r["id"], label=r["label"], role=r["role"], active=bool(r["active"]), sections=json.loads(r["sections"] or "[]"),
                created=r["created"], last_used=r["last_used"], uses=r["uses"])


def pw_in_use(pw, skip=None):
    return any(check_password_hash(r["pw"], pw) for r in qa("SELECT * FROM passcodes WHERE id!=?", skip or -1))


@app.get("/api/admin/passcodes")
@owner_only
def passcodes_list():
    return jsonify(items=[passcode_out(r) for r in qa("SELECT * FROM passcodes ORDER BY id")])


@app.post("/api/admin/passcodes")
@owner_only
def passcodes_create():
    j = request.get_json(silent=True) or {}
    label = str(j.get("label", "")).strip()[:80]
    if not label:
        raise ValueError("Give this password a label, like “Family” or “Mentors”.")
    role = j.get("role")
    if role not in LV:
        raise ValueError("Choose Level A, B or C.")
    pw = str(j.get("password") or "") or secrets.token_urlsafe(9)
    if len(pw) < 8:
        raise ValueError("The password must be at least 8 characters.")
    if pw_in_use(pw):
        raise ValueError("Another access password already uses that. Choose a different one.")
    secs = valid_sections(j.get("sections")) if j.get("sections") is not None else role_sections()[role]
    c = ex("INSERT INTO passcodes(label,role,pw,sections,ver,created) VALUES(?,?,?,?,?,?)",
           label, role, generate_password_hash(pw), json.dumps(secs), secrets.token_hex(8), now())
    log("Access password created", f"{label} (Level {role})", "viewers")
    return jsonify(id=c.lastrowid, password=pw)


@app.put("/api/admin/passcodes/<int:i>")
@owner_only
def passcodes_update(i):
    r = q1("SELECT * FROM passcodes WHERE id=?", i)
    if not r:
        abort(404)
    j = request.get_json(silent=True) or {}
    role = j.get("role", r["role"])
    if role not in LV:
        raise ValueError("Choose Level A, B or C.")
    secs = valid_sections(j["sections"]) if "sections" in j else json.loads(r["sections"] or "[]")
    active = 1 if j.get("active", bool(r["active"])) else 0
    ver = r["ver"]
    if not active and r["active"]:
        ver = secrets.token_hex(8)  # ends anyone currently signed in with it
    ex("UPDATE passcodes SET label=?,role=?,sections=?,active=?,ver=? WHERE id=?",
       str(j.get("label", r["label"])).strip()[:80] or r["label"], role, json.dumps(secs), active, ver, i)
    if role != r["role"] or secs != json.loads(r["sections"] or "[]") or active != r["active"]:
        log("Access password permissions changed", r["label"], "viewers")
    if j.get("password"):
        pw = str(j["password"])
        if len(pw) < 8:
            raise ValueError("The password must be at least 8 characters.")
        if pw_in_use(pw, i):
            raise ValueError("Another access password already uses that. Choose a different one.")
        ex("UPDATE passcodes SET pw=?, ver=? WHERE id=?", generate_password_hash(pw), secrets.token_hex(8), i)
        log("Access password changed (everyone signed in with it was signed out)", r["label"], "viewers")
    return jsonify(ok=True)


@app.delete("/api/admin/passcodes/<int:i>")
@owner_only
def passcodes_delete(i):
    r = q1("SELECT * FROM passcodes WHERE id=?", i)
    if not r:
        abort(404)
    ex("DELETE FROM passcodes WHERE id=?", i)
    log("Access password deleted", r["label"], "viewers")
    return jsonify(ok=True)


# ------------------------------------------------------------------ overview, activity, settings
@app.get("/api/admin/overview")
@owner_only
def overview():
    def n(sql, *a):
        return db().execute(sql, a).fetchone()[0]
    return jsonify(
        projects=n("SELECT COUNT(*) FROM items WHERE kind='project'"),
        artworks=n("SELECT COUNT(*) FROM items WHERE kind IN ('gallery','artwork')"),
        gallery=n("SELECT COUNT(*) FROM items WHERE kind='gallery'"),
        achievements=n("SELECT COUNT(*) FROM items WHERE kind IN ('achievement','special')"),
        milestones=n("SELECT COUNT(*) FROM items WHERE kind='journey'"),
        journal=n("SELECT COUNT(*) FROM items WHERE kind='journal'"),
        files=n("SELECT COUNT(*) FROM items WHERE kind='file'"),
        media=n("SELECT COUNT(*) FROM media"),
        posts=n("SELECT COUNT(*) FROM items WHERE kind='post' AND status='published'"),
        drafts=n("SELECT COUNT(*) FROM items WHERE kind='post' AND status!='published'"),
        unread=n("SELECT COUNT(*) FROM contacts WHERE read=0"),
        viewers=n("SELECT COUNT(*) FROM users WHERE role!='owner'"),
        recent=qa("SELECT * FROM activity WHERE area IN ('portfolio','blog','content','items','settings','backup') ORDER BY id DESC LIMIT 40"),
        archive=qa("SELECT * FROM activity WHERE area IN ('archive','security','viewers') ORDER BY id DESC LIMIT 40"),
        access=qa("SELECT * FROM activity WHERE area IN ('viewers','settings') ORDER BY id DESC LIMIT 10"),
        archive_status=setting("archive_status", "enabled"),
        last_backup=q1("SELECT ts, name FROM backups ORDER BY id DESC LIMIT 1"))


@app.get("/api/admin/activity")
@owner_only
def activity():
    area = request.args.get("area", "")
    if area:
        return jsonify(items=qa("SELECT * FROM activity WHERE area=? ORDER BY id DESC LIMIT 400", area))
    return jsonify(items=qa("SELECT * FROM activity ORDER BY id DESC LIMIT 400"))


@app.get("/api/admin/settings")
@owner_only
def settings_get():
    return jsonify(values={k: setting(k, "") for k in PUBLIC_SETTINGS}, role_sections=role_sections(),
                   retention_daily_days=int(setting("retention_daily_days", "90") or 90), archive=ARCHIVE,
                   external_backup=bool(os.environ.get("BACKUP_S3_BUCKET")))


@app.put("/api/admin/settings")
@owner_only
def settings_put():
    j = request.get_json(silent=True) or {}
    vals = j.get("values") if "values" in j and isinstance(j["values"], dict) else j
    for k in PUBLIC_SETTINGS:
        if k in vals:
            v = vals[k]
            if isinstance(v, (dict, list)):
                v = json.dumps(v, ensure_ascii=False)
            else:
                v = str(v).strip()[:50000]
            if v and k in ("instagram", "whatsapp", "linkedin", "github", "twitter") and not re.match(r"^https?://", v):
                raise ValueError(f"{k.title()} must be a full link starting with https://")
            put_setting(k, v)
    if isinstance(j.get("role_sections"), dict):
        put_setting("role_sections", json.dumps({k: valid_sections(j["role_sections"].get(k)) for k in "ABC"}))
    if "retention_daily_days" in j:
        put_setting("retention_daily_days", str(max(0, int(j["retention_daily_days"] or 0))))
    log("Settings changed", ", ".join(list(vals.keys())[:5]), "settings")
    return jsonify(ok=True)


# ------------------------------------------------------------------ exports
def safe(v):
    if isinstance(v, str) and v[:1] in ("=", "+", "-", "@"):
        return "'" + v
    return v


def export_rows(name):
    if name == "analytics":
        return ["Day", "Page views", "Visitors"], [[r["day"], r["views"], r["visitors"]] for r in json.loads(analytics().get_data())["daily"]]
    if name == "traffic":
        rows = db().execute("SELECT day,path,kind,slug,src,device,secs FROM hits ORDER BY id").fetchall()
        return ["Day", "Path", "Type", "Item", "Source", "Device", "Seconds on page"], [list(r) for r in rows]
    if name == "feedback":
        rows = db().execute("SELECT ts,design,content,navigation,overall,comment FROM feedback ORDER BY id").fetchall()
        return ["Time", "Design", "Content", "Navigation", "Overall", "Comment"], [list(r) for r in rows]
    if name == "messages":
        rows = db().execute("SELECT ts,name,email,message FROM contacts ORDER BY id").fetchall()
        return ["Time", "Name", "Email", "Message"], [list(r) for r in rows]
    if name == "archive":
        rows = []
        for r in db().execute("SELECT * FROM items WHERE kind IN (%s) ORDER BY kind,created" % ",".join("?" * len(PRIVATE_KINDS)), PRIVATE_KINDS):
            d = json.loads(r["data"] or "{}")
            rows.append([ARCHIVE[r["kind"]], r["title"], d.get("date") or d.get("year") or "", r["status"], r["access"],
                         d.get("text") or d.get("details") or "", d.get("image") or d.get("file") or ""])
        return ["Section", "Title", "Date", "Status", "Access", "Text", "File"], rows
    if name == "viewers":
        rows = [[u["username"], u["name"], u["role"], ", ".join(ARCHIVE.get(s, s) for s in json.loads(u["sections"] or "[]")),
                 "yes" if u["active"] else "no", u["created"], u["last_login"] or ""] for u in qa("SELECT * FROM users WHERE role!='owner'")]
        return ["Username", "Name", "Level", "Sections", "Active", "Created", "Last sign-in"], rows
    abort(404)


@app.get("/api/admin/export/<name>")
@owner_only
def export(name):
    head, rows = export_rows(name)
    rows = [[safe(c) for c in r] for r in rows]
    fmt = request.args.get("fmt", "csv")
    fname = f"{name}-{today().isoformat()}"
    log("Export downloaded", f"{name}.{fmt}", "settings")
    if fmt == "xlsx":
        try:
            from openpyxl import Workbook
        except ImportError:
            raise ValueError("Excel export isn't installed on this server. Use CSV.")
        wb = Workbook()
        ws = wb.active
        ws.append(head)
        for r in rows:
            ws.append(r)
        bio = io.BytesIO()
        wb.save(bio)
        bio.seek(0)
        return send_file(bio, as_attachment=True, download_name=fname + ".xlsx",
                         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(head)
    w.writerows(rows)
    return Response("\ufeff" + out.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename={fname}.csv"})


# ------------------------------------------------------------------ backups
BK_LOCK = threading.Lock()


def upload_external(path):
    bucket = os.environ.get("BACKUP_S3_BUCKET")
    if not bucket:
        return True, ""
    try:
        import boto3
        s3 = boto3.client("s3", endpoint_url=os.environ.get("BACKUP_S3_ENDPOINT") or None)
        s3.upload_file(path, bucket, os.environ.get("BACKUP_S3_PREFIX", "backups/") + os.path.basename(path))
        return True, "Copied to external storage."
    except Exception as e:
        return False, f"External copy failed: {str(e)[:150]}"


def make_backup(kind="manual", note=""):
    with BK_LOCK:
        ts = dt.datetime.now(dt.timezone.utc)
        name = f"backup-{ts:%Y%m%d-%H%M%S}-{kind}.zip"
        path, tmp = os.path.join(BK, name), os.path.join(DATA, "_snapshot.db")
        c = connect()
        status, msg = "ok", note
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
            dest = sqlite3.connect(tmp)
            c.backup(dest)
            dest.close()
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
                z.write(tmp, "site.db")
                for root, _, files in os.walk(os.path.join(DATA, "uploads")):
                    for f in files:
                        full = os.path.join(root, f)
                        z.write(full, os.path.relpath(full, DATA))
                z.writestr("manifest.json", json.dumps({"created": ts.isoformat(), "kind": kind, "version": 1}))
            os.remove(tmp)
            ok, extra = upload_external(path)
            msg = (msg + " " + extra).strip()
            if not ok:
                status = "warning"
        except Exception as e:
            status, msg = "failed", str(e)[:300]
        size = os.path.getsize(path) if os.path.exists(path) else 0
        c.execute("INSERT INTO backups(ts,name,kind,size,status,note) VALUES(?,?,?,?,?,?)", (now(), name, kind, size, status, msg))
        c.execute("INSERT INTO activity(ts,actor,action,obj,area) VALUES(?,?,?,?,?)", (now(), "system", f"Backup {status}" if status != "ok" else "Backup created", f"{kind}: {name}", "backup"))
        c.commit()
        prune(c)
        c.close()
        return status, name


def prune(c):
    """Daily backups older than the retention setting are removed. Weekly, manual and pre-restore backups are kept."""
    row = c.execute("SELECT v FROM settings WHERE k='retention_daily_days'").fetchone()
    days = int(row[0]) if row else 90
    if days <= 0:
        return
    cut = (today() - dt.timedelta(days=days)).isoformat()
    for r in c.execute("SELECT id,name FROM backups WHERE kind='daily' AND ts<?", (cut,)).fetchall():
        try:
            os.remove(os.path.join(BK, r[1]))
        except OSError:
            pass
        c.execute("DELETE FROM backups WHERE id=?", (r[0],))
    c.commit()


def sync_backups(c):
    """Register any backup zip found in the backups folder that the database doesn't know about."""
    known = {r[0] for r in c.execute("SELECT name FROM backups")}
    for f in sorted(os.listdir(BK)):
        if f.endswith(".zip") and f not in known:
            m = re.match(r"backup-(\d{8})-(\d{6})-([a-z-]+)\.zip", f)
            kind = m.group(3) if m else "imported"
            ts = dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S").strftime("%Y-%m-%dT%H:%M:%SZ") if m else now()
            c.execute("INSERT OR IGNORE INTO backups(ts,name,kind,size,status,note) VALUES(?,?,?,?,?,?)",
                      (ts, f, kind, os.path.getsize(os.path.join(BK, f)), "ok", "Found in backups folder"))
    c.commit()


def scheduler():
    time.sleep(20)
    while True:
        try:
            c = connect()
            t = today()
            monday = (t - dt.timedelta(days=t.weekday())).isoformat()
            has = lambda kind, since: c.execute("SELECT 1 FROM backups WHERE kind=? AND ts>=? AND status!='failed'", (kind, since)).fetchone()
            need_daily, need_weekly = not has("daily", t.isoformat()), not has("weekly", monday)
            c.close()
            if need_daily:
                make_backup("daily")
            if need_weekly:
                make_backup("weekly")
        except Exception as e:
            print("backup scheduler:", e, flush=True)
        time.sleep(1800)


@app.get("/api/admin/backups")
@owner_only
def backups_list():
    return jsonify(items=qa("SELECT * FROM backups ORDER BY id DESC LIMIT 300"),
                   external=bool(os.environ.get("BACKUP_S3_BUCKET")))


@app.post("/api/admin/backups")
@owner_only
def backups_make():
    status, name = make_backup("manual", "Started by owner")
    return jsonify(status=status, name=name)


@app.get("/api/admin/backups/<int:i>/download")
@owner_only
def backups_download(i):
    r = q1("SELECT * FROM backups WHERE id=?", i)
    if not r or not os.path.exists(os.path.join(BK, r["name"])):
        abort(404)
    log("Backup downloaded", r["name"], "backup")
    return send_from_directory(BK, r["name"], as_attachment=True)


@app.post("/api/admin/backups/<int:i>/restore")
@owner_only
def backups_restore(i):
    """Restoring replaces the live database with the backup. It needs: the owner's password, the typed word RESTORE,
    and it always takes a safety backup of the current site first."""
    j = request.get_json(silent=True) or {}
    if rl_over("restore", 5, 900):
        return jsonify(error="Too many attempts."), 429
    rl_add("restore")
    if j.get("confirm") != "RESTORE":
        raise ValueError('Type RESTORE (in capitals) to confirm.')
    if not check_password_hash(me()["pw"], str(j.get("password", ""))):
        raise ValueError("Your password is wrong.")
    r = q1("SELECT * FROM backups WHERE id=?", i)
    path = os.path.join(BK, r["name"]) if r else ""
    if not r or not os.path.exists(path):
        abort(404)
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if "site.db" not in names:
            raise ValueError("This backup file is missing its database.")
        for n in names:
            if n.startswith("/") or ".." in n:
                raise ValueError("This backup file looks unsafe.")
    status, safety = make_backup("pre-restore", f"Automatic safety copy before restoring {r['name']}")
    if status == "failed":
        raise ValueError("Couldn't make a safety backup first, so nothing was restored.")
    tmpdir = os.path.join(DATA, "_restore")
    shutil.rmtree(tmpdir, ignore_errors=True)
    with zipfile.ZipFile(path) as z:
        z.extractall(tmpdir)
    d = g.pop("db", None)
    if d:
        d.close()
    for ext in ("-wal", "-shm"):
        try:
            os.remove(DB_PATH + ext)
        except OSError:
            pass
    os.replace(os.path.join(tmpdir, "site.db"), DB_PATH)
    up = os.path.join(tmpdir, "uploads")
    if os.path.isdir(up):
        shutil.copytree(up, os.path.join(DATA, "uploads"), dirs_exist_ok=True)
    shutil.rmtree(tmpdir, ignore_errors=True)
    c = connect()
    sync_backups(c)
    c.execute("INSERT INTO activity(ts,actor,action,obj,area) VALUES(?,?,?,?,?)", (now(), "owner", "Site restored from backup", r["name"], "backup"))
    c.commit()
    c.close()
    session.clear()
    return jsonify(ok=True, safety=safety, message="Restored. Please sign in again.")


# ------------------------------------------------------------------ pages
def html(name):
    r = send_from_directory(STATIC, name)
    r.headers["Cache-Control"] = "no-cache"
    return r


@app.get("/")
def home():
    return html("index.html")


@app.get("/admin")
@app.get("/admin/")
def admin_page():
    return html("admin.html")


@app.get("/private")
@app.get("/private/")
@app.get("/archive")
@app.get("/archive/")
def private_page():
    return html("private.html")


@app.get("/robots.txt")
def robots():
    return Response("User-agent: *\nDisallow: /admin\nDisallow: /private\nDisallow: /archive\nDisallow: /api/\n", mimetype="text/plain")


@app.get("/healthz")
def healthz():
    return "ok"


PUBLIC_ROUTES = {"about", "journey", "work", "achievements", "blog", "contact"}


@app.get("/<path:p>")
def spa(p):
    first = p.strip("/").split("/")[0]
    if first == "gallery":
        return redirect("/work/gallery", 301)
    if first in PUBLIC_ROUTES:
        return html("index.html")
    if first == "api":
        return jsonify(error="Not found."), 404
    return html("index.html"), 404


init_db()
if not os.environ.get("NO_SCHEDULER"):
    threading.Thread(target=scheduler, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=False)
