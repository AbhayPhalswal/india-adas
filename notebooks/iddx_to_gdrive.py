# %% [markdown]
# # IDD-X → Google Drive (server-to-server, no local disk)
#
# Pulls `iddx.tar.gz` (171.4 GB) from india-data.org in 25 MiB chunks — several in parallel —
# and streams it into a Google Drive folder using Drive's resumable upload. Nothing is stored on
# Colab's disk. Fully resumable: if Colab disconnects, re-run **every cell from the top** — it
# continues where it stopped.
#
# **Before you start** (in Chrome, logged in at india-data.org):
# 1. Press **F12** → **Network** tab → reload the page
# 2. Click any request to `india-data.org` (e.g. `user-details`)
# 3. Right-click it → **Copy** → **Copy as cURL (bash)**
# 4. Paste the whole thing into the `PASTE` box in Cell 2
#
# india-data's access token expires every **15 minutes**. The transfer cell handles that itself:
# it re-uses refreshed cookies the server sends back, tries the site's refresh endpoint, and if
# both fail it **pauses and asks you to paste a fresh cURL** (log in again at india-data.org first
# if the site logged you out). You never need to re-run cells for that.
#
# **How to open this in Colab:** push to GitHub and open
# colab.research.google.com/github/AbhayPhalswal/india-adas/blob/main/notebooks/iddx_to_gdrive.ipynb

# %% [markdown]
# ## Cell 1 — Google sign-in (for Drive upload) + mount Drive (for the tiny resume-state file)

# %%
from google.colab import auth, drive
auth.authenticate_user()
drive.mount('/content/drive')

import google.auth
from google.auth.transport.requests import Request as GRequest
creds, _ = google.auth.default()
creds.refresh(GRequest())
print('Google auth OK')

# %% [markdown]
# ## Cell 2 — paste the cURL from Chrome (or just the raw Cookie header value)

# %%
PASTE = r"""
PASTE HERE
"""

import re, requests

def extract_cookie(s):
    s = s.strip()
    if s.lower().startswith('curl'):
        m = (re.search(r"-b\s+(['\"])(.*?)\1", s, re.S)
             or re.search(r"-H\s+(['\"])cookie:\s*(.*?)\1", s, re.S | re.I))
        if not m:
            raise SystemExit("No cookie found in the pasted cURL — use 'Copy as cURL (bash)', not (cmd)")
        return m.group(2).strip()
    return s

def cookie_jar_from_string(s):
    jar = requests.cookies.RequestsCookieJar()
    for part in s.split(';'):
        if '=' in part:
            k, v = part.strip().split('=', 1)
            jar.set(k.strip(), v.strip(), domain='india-data.org', path='/')
    return jar

COOKIE = extract_cookie(PASTE)
assert COOKIE and 'PASTE HERE' not in COOKIE, 'Paste the cURL / cookie first'
names = [p.strip().split('=', 1)[0] for p in COOKIE.split(';') if '=' in p]
print(f'Cookie captured: {", ".join(names)}')
assert 'access-token-dfs' in names, 'That cookie has no access-token-dfs — copy the cURL from a request made while logged in'

# %% [markdown]
# ## Cell 3 — settings + an 82-byte test request to prove the cookie works

# %%
import time, json, os, datetime, threading
from concurrent.futures import ThreadPoolExecutor

DOWNLOAD_URL = 'https://india-data.org/du/download/v1/download-file'
FILE_NAME    = '99124475-fc84-46dc-9dad-f5e34c18f9e0/c884d2d3-14b3-48c3-a6a3-733b0c2ee210/DATASET-FILE/20250609055823695_iddx.tar.gz'
TOTAL        = 171438714882          # bytes, from the site's file listing
SERVER_CHUNK = 26214400              # the server always returns 25 MiB per Range request

DRIVE_FOLDER_ID = '1786soz91ihA1VtJR2QL_yVh69ge_P8zD'   # your "driving dataset" folder
DRIVE_FILE_NAME = 'iddx.tar.gz'
UPLOAD_CHUNK    = 256 * 1024 * 1024  # must be a multiple of 256 KiB
STATE_PATH      = '/content/drive/MyDrive/.iddx_upload_state.json'

WORKERS = 6   # parallel connections to india-data. Lower to 3–4 if you see lots of "hiccup" lines.

# If you find the site's real refresh request in DevTools (filter the Network tab for "refresh"),
# put its full URL here. Leave empty to let the code try the usual candidates.
REFRESH_URL = ''
REFRESH_CANDIDATES = ['/core/authorization/refresh-token', '/core/authorization/refresh',
                      '/core/authorization/token/refresh', '/core/authorization/refresh-access-token',
                      '/core/authorization/get-access-token', '/core/auth/refresh-token']

sess = requests.Session()
sess.cookies = cookie_jar_from_string(COOKIE)
sess.headers.update({'fileName': FILE_NAME, 'app-name': 'DFS', 'User-Agent': 'Mozilla/5.0',
                     'Referer': 'https://india-data.org/dataset-details/99124475-fc84-46dc-9dad-f5e34c18f9e0'})
# allow WORKERS simultaneous connections to the same host
adapter = requests.adapters.HTTPAdapter(pool_connections=WORKERS + 2, pool_maxsize=WORKERS + 2)
sess.mount('https://', adapter)

r = sess.get(DOWNLOAD_URL, headers={'Range': f'bytes={TOTAL-82}-'}, timeout=60)
print(r.status_code, r.headers.get('content-range'), len(r.content), 'bytes')
assert r.status_code == 206 and len(r.content) == 82, 'Cookie not accepted — copy a fresh cURL and re-run Cell 2'
print('Cookie OK — server is serving the file')

# %% [markdown]
# ## Cell 4 — the transfer (re-run this cell to resume after any disconnect)

# %%
class AuthNeeded(Exception): pass
class NeedPaste(Exception): pass

_refresh_lock = threading.Lock()

def try_refresh():
    """Ask india-data for a new access token. True if the access-token cookie changed."""
    global REFRESH_URL
    with _refresh_lock:
        before = sess.cookies.get('access-token-dfs')
        urls = [REFRESH_URL] if REFRESH_URL else ['https://india-data.org' + c for c in REFRESH_CANDIDATES]
        for u in urls:
            for method in ('post', 'get'):
                try:
                    r = sess.request(method, u, timeout=30)
                except requests.RequestException:
                    continue
                if r.status_code < 400 and sess.cookies.get('access-token-dfs') not in (None, before):
                    REFRESH_URL = u
                    print(f'  token refreshed via {method.upper()} {u}')
                    return True
        return False

def repaste():
    """Main thread only (input() does not work from worker threads)."""
    s = input('\nindia-data session expired. In Chrome: reload india-data.org (log in again if needed), '
              'copy a fresh cURL (bash) from the Network tab, paste it here and press Enter:\n')
    sess.cookies = cookie_jar_from_string(extract_cookie(s))
    print('  new cookie loaded, continuing')


class RemoteFile:
    """Reads the india-data file with parallel Range requests; behaves like a sequential file."""
    def __init__(self):
        self.pos = 0
        self.buf = bytearray()   # bytes starting at self.pos
        self.pool = ThreadPoolExecutor(max_workers=WORKERS)

    def _fetch_once(self, offset):
        """One 25 MiB chunk from offset. Raises AuthNeeded on 401/403."""
        for attempt in range(6):
            try:
                r = sess.get(DOWNLOAD_URL, headers={'Range': f'bytes={offset}-'}, timeout=180)
            except requests.RequestException:
                time.sleep(min(60, 2 * 2 ** attempt)); continue
            if r.status_code in (401, 403):
                raise AuthNeeded(offset)
            if r.status_code == 206:
                try:
                    start = int(r.headers['content-range'].split()[1].split('-')[0])
                except (KeyError, ValueError):
                    start = -1
                full = len(r.content) == SERVER_CHUNK or offset + len(r.content) == TOTAL
                if start == offset and full:
                    return r.content
            time.sleep(min(60, 2 * 2 ** attempt))   # 429 / 5xx / short or misaligned chunk → retry
        raise IOError(f'chunk at {offset:,} failed after 6 attempts')

    def _fetch_many(self, offsets):
        """Fetch chunks in parallel; returns them in the same order as offsets."""
        got = {}
        for _ in range(30):
            todo = [o for o in offsets if o not in got]
            if not todo:
                break
            futs = {o: self.pool.submit(self._fetch_once, o) for o in todo}
            auth_needed = False
            for o, f in futs.items():
                try:
                    got[o] = f.result()
                except AuthNeeded:
                    auth_needed = True
                except Exception as e:
                    print(f'  download hiccup at {o:,}: {e}')
            if auth_needed:
                print('  auth rejected — refreshing token')
                if not try_refresh():
                    raise NeedPaste()        # main thread will prompt you, then retry this read
            elif len(got) < len(offsets):
                time.sleep(5)
        else:
            raise RuntimeError('download: gave up after 30 rounds')
        return [got[o] for o in offsets]

    def seek(self, offset):
        if offset != self.pos:
            self.pos, self.buf = offset, bytearray()

    def read(self, n):
        need_end = min(self.pos + n, TOTAL)
        start = self.pos + len(self.buf)
        offsets = list(range(start, need_end, SERVER_CHUNK))
        if offsets:
            for chunk in self._fetch_many(offsets):   # buf untouched if this raises → safe to retry
                self.buf += chunk
        out = bytes(self.buf[:n]); del self.buf[:n]
        self.pos += len(out)
        return out


def bearer():
    if (not creds.valid) or (creds.expiry and (creds.expiry - datetime.datetime.utcnow()).total_seconds() < 300):
        creds.refresh(GRequest())
    return {'Authorization': f'Bearer {creds.token}'}

def load_state():
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_state(s):
    with open(STATE_PATH, 'w') as f:
        json.dump(s, f)

def new_session():
    r = requests.post('https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable',
                      headers={**bearer(), 'Content-Type': 'application/json; charset=UTF-8',
                               'X-Upload-Content-Type': 'application/gzip',
                               'X-Upload-Content-Length': str(TOTAL)},
                      json={'name': DRIVE_FILE_NAME, 'parents': [DRIVE_FOLDER_ID]}, timeout=60)
    r.raise_for_status()
    return r.headers['Location']

def query_session(uri):
    """Returns next byte offset to send, or None if the session is dead."""
    r = requests.put(uri, headers={**bearer(), 'Content-Length': '0', 'Content-Range': f'bytes */{TOTAL}'}, timeout=60)
    if r.status_code in (200, 201):
        return TOTAL
    if r.status_code == 308:
        rng = r.headers.get('Range')          # 'bytes=0-N' or absent
        return int(rng.split('-')[1]) + 1 if rng else 0
    return None

# ---- resume or start ----
state = load_state()
uri = state.get('session_uri')
next_off = query_session(uri) if uri else None
if next_off is None:
    uri = new_session(); next_off = 0
    save_state({'session_uri': uri, 'started': time.strftime('%Y-%m-%d %H:%M:%S')})
    print('Started a new Drive upload session')
else:
    print(f'Resuming at {next_off/1e9:.2f} GB ({100*next_off/TOTAL:.1f}%)')
print(f'{WORKERS} parallel download connections; next block prefetches while the current one uploads')

remote = RemoteFile()
remote.seek(next_off)
t0, done0 = time.time(), next_off
last_refresh = time.time()

prefetch = ThreadPoolExecutor(max_workers=1)
pending = prefetch.submit(remote.read, UPLOAD_CHUNK)

while next_off < TOTAL:
    # proactive refresh every 12 min once we know a working refresh URL (token lives 15 min)
    if REFRESH_URL and time.time() - last_refresh > 12 * 60:
        try_refresh(); last_refresh = time.time()

    try:
        chunk = pending.result()
    except NeedPaste:
        repaste()
        pending = prefetch.submit(remote.read, UPLOAD_CHUNK)
        continue
    end = next_off + len(chunk) - 1
    # start downloading the next block while this one uploads
    pending = prefetch.submit(remote.read, UPLOAD_CHUNK) if end + 1 < TOTAL else None

    resync = False
    for attempt in range(10):
        try:
            r = requests.put(uri, headers={**bearer(), 'Content-Length': str(len(chunk)),
                                           'Content-Range': f'bytes {next_off}-{end}/{TOTAL}'},
                             data=chunk, timeout=900)
        except requests.RequestException as e:
            print(f'  upload hiccup: {e}'); time.sleep(min(90, 3 * 2 ** attempt)); continue
        if r.status_code == 308:
            got = int(r.headers['Range'].split('-')[1]) + 1 if 'Range' in r.headers else query_session(uri)
            if got != end + 1:                 # partial — resync
                print(f'  Drive accepted up to {got:,}; re-sending from there')
                resync = True; next_off = got
            break
        if r.status_code in (200, 201):
            next_off = TOTAL; break
        if r.status_code in (404, 410):
            raise SystemExit('Upload session expired — delete the state file and re-run Cell 4 to start over')
        print(f'  Drive returned {r.status_code}: {r.text[:200]} — retrying'); time.sleep(min(90, 3 * 2 ** attempt))
    else:
        raise RuntimeError('upload: gave up after 10 attempts')

    if resync:
        if pending is not None:
            try: pending.result()          # let the prefetch finish, then throw it away
            except Exception: pass
        remote.seek(next_off)
        pending = prefetch.submit(remote.read, UPLOAD_CHUNK)
        continue
    if next_off != TOTAL:
        next_off = end + 1
    el = time.time() - t0; rate = (next_off - done0) / el / 1e6 if el else 0
    eta = (TOTAL - next_off) / (rate * 1e6) / 3600 if rate else 0
    print(f'{next_off/1e9:8.2f} GB  {100*next_off/TOTAL:5.1f}%  {rate:5.1f} MB/s  ETA {eta:4.1f} h')

print('\nDONE — iddx.tar.gz is in your Drive folder. Check it shows 171.4 GB.')

# %% [markdown]
# ## Afterwards
#
# - The tar.gz stays in Drive; extract only what you need, on a machine with space, or stream-extract:
#   `tar -xzf iddx.tar.gz --wildcards 'some/subfolder/*'`
# - The dataset README is one line: *Read here for all the details on IDD-X: https://idd-x.github.io/*
# - Licence: academic / non-commercial, attribute IIIT Hyderabad + the IDD-X authors.
# - You can delete `/MyDrive/.iddx_upload_state.json` once the upload is finished.
