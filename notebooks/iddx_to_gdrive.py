# %% [markdown]
# # IDD-X → Google Drive (server-to-server, no local disk)
#
# Pulls `iddx.tar.gz` (171.4 GB) from india-data.org in 25 MiB chunks and streams it into a
# Google Drive folder using Drive's resumable upload. Nothing is stored on Colab's disk.
# Fully resumable: if Colab disconnects, re-run **every cell from the top** — it continues where it stopped.
#
# **Before you start** (in Chrome, logged in at india-data.org):
# 1. Press **F12** → **Network** tab → reload the page
# 2. Click any request to `india-data.org` (e.g. `user-details`)
# 3. Right-click it → **Copy** → **Copy as cURL (bash)**
# 4. Paste the whole thing into the `PASTE` box in Cell 2
#
# The session cookie is HttpOnly, so this is the only way to get it. If the download stops with
# "cookie not accepted" later, repeat these steps — sessions expire.
#
# **How to open this in Colab:** File → Upload notebook → pick this .py file
# (Colab reads the `# %%` cell markers), or paste each cell into a fresh notebook.

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

import re
def extract_cookie(s):
    s = s.strip()
    if s.lower().startswith('curl'):
        m = (re.search(r"-b\s+(['\"])(.*?)\1", s, re.S)
             or re.search(r"-H\s+(['\"])cookie:\s*(.*?)\1", s, re.S | re.I))
        if not m:
            raise SystemExit("No cookie found in the pasted cURL — use 'Copy as cURL (bash)', not (cmd)")
        return m.group(2).strip()
    return s

COOKIE = extract_cookie(PASTE)
assert COOKIE and 'PASTE HERE' not in COOKIE, 'Paste the cURL / cookie first'
print(f'Cookie captured ({len(COOKIE)} chars)')

# %% [markdown]
# ## Cell 3 — settings + an 82-byte test request to prove the cookie works

# %%
import requests, time, json, os, datetime

DOWNLOAD_URL = 'https://india-data.org/du/download/v1/download-file'
FILE_NAME    = '99124475-fc84-46dc-9dad-f5e34c18f9e0/c884d2d3-14b3-48c3-a6a3-733b0c2ee210/DATASET-FILE/20250609055823695_iddx.tar.gz'
TOTAL        = 171438714882          # bytes, from the site's file listing
SERVER_CHUNK = 26214400              # the server always returns 25 MiB per Range request

DRIVE_FOLDER_ID = '1786soz91ihA1VtJR2QL_yVh69ge_P8zD'   # your "driving dataset" folder
DRIVE_FILE_NAME = 'iddx.tar.gz'
UPLOAD_CHUNK    = 256 * 1024 * 1024  # must be a multiple of 256 KiB
STATE_PATH      = '/content/drive/MyDrive/.iddx_upload_state.json'

sess = requests.Session()
sess.headers.update({'fileName': FILE_NAME, 'app-name': 'DFS', 'Cookie': COOKIE,
                     'User-Agent': 'Mozilla/5.0'})

r = sess.get(DOWNLOAD_URL, headers={'Range': f'bytes={TOTAL-82}-'}, timeout=60)
print(r.status_code, r.headers.get('content-range'), len(r.content), 'bytes')
assert r.status_code == 206 and len(r.content) == 82, 'Cookie not accepted — copy a fresh cURL and re-run Cell 2'
print('Cookie OK — server is serving the file')

# %% [markdown]
# ## Cell 4 — the transfer (re-run this cell to resume after any disconnect)

# %%
class RemoteFile:
    """Reads the india-data file by Range requests; behaves like a sequential file."""
    def __init__(self):
        self.pos = 0
        self.buf = bytearray()   # bytes starting at self.pos

    def _fetch(self, offset):
        for attempt in range(10):
            try:
                r = sess.get(DOWNLOAD_URL, headers={'Range': f'bytes={offset}-'}, timeout=180)
                if r.status_code in (401, 403):
                    raise SystemExit('Cookie expired / not accepted — get a fresh cURL, re-run Cells 2, 3, 4')
                if r.status_code != 206:
                    raise IOError(f'status {r.status_code}: {r.text[:200]}')
                start = int(r.headers['content-range'].split()[1].split('-')[0])
                if start != offset:
                    raise IOError(f'server returned offset {start}, wanted {offset}')
                return r.content
            except (requests.RequestException, IOError, KeyError) as e:
                wait = min(90, 3 * 2 ** attempt)
                print(f'  download hiccup at {offset:,}: {e} — retry in {wait}s')
                time.sleep(wait)
        raise RuntimeError('download: gave up after 10 attempts')

    def seek(self, offset):
        if offset != self.pos:
            self.pos, self.buf = offset, bytearray()

    def read(self, n):
        while len(self.buf) < n and self.pos + len(self.buf) < TOTAL:
            self.buf += self._fetch(self.pos + len(self.buf))
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

remote = RemoteFile()
remote.seek(next_off)
t0, done0 = time.time(), next_off

while next_off < TOTAL:
    chunk = remote.read(UPLOAD_CHUNK)
    end = next_off + len(chunk) - 1
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
                remote.seek(got); next_off = got; resync = True
            break
        if r.status_code in (200, 201):
            next_off = TOTAL; break
        if r.status_code in (404, 410):
            raise SystemExit('Upload session expired — delete the state file and re-run Cell 4 to start over')
        print(f'  Drive returned {r.status_code}: {r.text[:200]} — retrying'); time.sleep(min(90, 3 * 2 ** attempt))
    else:
        raise RuntimeError('upload: gave up after 10 attempts')
    if resync:
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
