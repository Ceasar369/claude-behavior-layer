#!/usr/bin/env python3
"""push.py — the buzz: my phone told when a session is done.

1100 on my phone's home screen asks once, from a tap on the rail's bell,
to be told. What my phone hands back, its subscription, is kept here, in
.claude/state/push/, with 1100's own key, made the first time one is
asked for. Neither ever leaves this Mac but to Apple.

A session is done when its rail number turns from green to red: its turn
ended, and nothing it runs reads as work. 1100's colour watch,
page.reddened's, sees it for as long as 1100 runs, and buzz() buzzes:
"Session 01 is done", or "Session 01 needs you" when a dialog or a
browser waits on me. Under it,
the session's name and its move, so I read where it stands from any app,
or the Lock Screen. A tap opens its transcript. A session gone, or one
starting, buzzes nothing.

Each buzz is sealed for my phone alone (RFC 8291) and signed as 1100's
(RFC 8292), then handed to Apple's push service, which wakes the phone. A
phone that has dropped its subscription is forgotten.

  push.py test     one buzz to every phone kept, to try it

Imported by 1100, or run to try.
"""

import base64
import json
import os
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import project  # noqa: E402
import registry  # noqa: E402
import transcripts  # noqa: E402

STATE = os.path.join(registry.ROOT, ".claude", "state", "push")
KEY = os.path.join(STATE, "key.pem")
PHONES = os.path.join(STATE, "phones.json")

# How long Apple keeps a buzz for a phone it cannot reach, in seconds.
KEEP = 3600

# A buzz naming no title of its own wears the project's name.
TITLE = project.NAME

# 1100's service worker, at /sw.js. It shows each buzz, and a tap on one
# opens what it names: home, if it runs, is told; else home opens there.
# It never touches a page's own requests.
WORKER = r"""self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('push', e => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch (x) {}
  e.waitUntil(self.registration.showNotification(d.title || %s,
    {body: d.body || '', data: {url: d.url || '/'}}));
});
self.addEventListener('notificationclick', e => {
  e.notification.close();
  const url = new URL((e.notification.data || {}).url || '/', self.location.origin).href;
  e.waitUntil(self.clients.matchAll({type: 'window', includeUncontrolled: true}).then(all => {
    if (all[0]) { all[0].postMessage({open: url}); return all[0].focus(); }
    return self.clients.openWindow(url);
  }));
});
""" % json.dumps(TITLE)


def b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def point(key) -> bytes:
    """A public key as the 65 bytes the standards send."""
    return key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)


# ---- 1100's key, and the phones it tells -------------------------------------------

def own_key():
    """1100's signing key, made once, readable by me alone."""
    try:
        with open(KEY, "rb") as f:
            return serialization.load_pem_private_key(f.read(), None)
    except (OSError, ValueError):
        pass
    key = ec.generate_private_key(ec.SECP256R1())
    os.makedirs(STATE, exist_ok=True)
    fd = os.open(KEY, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                  serialization.NoEncryption()))
    return key


def public() -> str:
    """1100's public key, as a page hands it to the phone's subscribe."""
    return b64(point(own_key().public_key()))


def phones() -> list:
    try:
        with open(PHONES) as f:
            got = json.load(f)
        return got if isinstance(got, list) else []
    except (OSError, ValueError):
        return []


def save(kept: list) -> None:
    registry.write_whole(PHONES, json.dumps(kept, indent=1))


def keep(form: dict) -> str:
    """A phone's subscription, posted by home once I allow the buzz, and on
    each load after. One sentence when it cannot be kept."""
    try:
        sub = json.loads((form.get("sub") or [""])[0])
        endpoint, keys = sub["endpoint"], sub["keys"]
        unb64(keys["p256dh"]), unb64(keys["auth"])
    except (ValueError, KeyError, TypeError):
        return "The phone's subscription could not be read."
    if urllib.parse.urlsplit(endpoint).scheme != "https":
        return "The phone's subscription could not be read."
    origin = (form.get("origin") or [""])[0]
    kept = [p for p in phones() if p.get("endpoint") != endpoint]
    kept.append({"endpoint": endpoint, "keys": {"p256dh": keys["p256dh"], "auth": keys["auth"]},
                 "origin": origin if origin.startswith("https://") else ""})
    save(kept)
    return ""


# ---- one buzz ------------------------------------------------------------------------

def sealed(phone: dict, words: bytes) -> bytes:
    """The words, sealed for this phone alone: RFC 8291's aes128gcm."""
    theirs = unb64(phone["keys"]["p256dh"])
    secret = unb64(phone["keys"]["auth"])
    mine = ec.generate_private_key(ec.SECP256R1())
    shared = mine.exchange(ec.ECDH(), ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), theirs))
    ours = point(mine.public_key())
    ikm = HKDF(hashes.SHA256(), 32, secret, b"WebPush: info\x00" + theirs + ours).derive(shared)
    salt = os.urandom(16)
    cek = HKDF(hashes.SHA256(), 16, salt, b"Content-Encoding: aes128gcm\x00").derive(ikm)
    nonce = HKDF(hashes.SHA256(), 12, salt, b"Content-Encoding: nonce\x00").derive(ikm)
    body = AESGCM(cek).encrypt(nonce, words + b"\x02", None)
    return salt + struct.pack(">I", 4096) + bytes([len(ours)]) + ours + body


def signed(endpoint: str, contact: str) -> str:
    """1100's signature for one push service: RFC 8292's VAPID header."""
    key = own_key()
    aud = "{0.scheme}://{0.netloc}".format(urllib.parse.urlsplit(endpoint))
    head = b64(json.dumps({"typ": "JWT", "alg": "ES256"}, separators=(",", ":")).encode())
    claims = b64(json.dumps({"aud": aud, "exp": int(time.time()) + 12 * 3600, "sub": contact},
                            separators=(",", ":")).encode())
    r, s = decode_dss_signature(key.sign(f"{head}.{claims}".encode(), ec.ECDSA(hashes.SHA256())))
    jwt = f"{head}.{claims}.{b64(r.to_bytes(32, 'big') + s.to_bytes(32, 'big'))}"
    return f"vapid t={jwt}, k={public()}"


def send(title: str, body: str, url: str) -> list:
    """One buzz to every phone kept. What each push service answered, in
    order. A phone whose subscription is gone, 404 or 410, is forgotten."""
    words = json.dumps({"title": title, "body": body, "url": url}).encode()
    kept, answers = phones(), []
    for phone in kept:
        contact = phone.get("origin") or "https://localhost"
        ask = urllib.request.Request(phone["endpoint"], data=sealed(phone, words), method="POST", headers={
            "Authorization": signed(phone["endpoint"], contact), "Content-Encoding": "aes128gcm",
            "Content-Type": "application/octet-stream", "TTL": str(KEEP), "Urgency": "high"})
        try:
            with urllib.request.urlopen(ask, timeout=15) as r:
                answers.append(r.status)
        except urllib.error.HTTPError as e:
            answers.append(e.code)
            if e.code in (404, 410):
                phone["gone"] = True
        except (urllib.error.URLError, OSError):
            answers.append(0)
    if any(p.get("gone") for p in kept):
        save([p for p in kept if not p.get("gone")])
    return answers


# ---- when a session is done ----------------------------------------------------------

def said(nn: str, name: str) -> str:
    """A buzz's words under its title: the session's name, then its move."""
    path = (registry.entries().get(nn) or {}).get("transcript", "")
    move = transcripts.last_said(path)[2] if path else ""
    return f"{name}: {move}" if move else name


def buzz(link):
    """1100's buzz, as an act for page.reddened's watch: a session whose
    number was green and is now red buzzes once. `link` gives the address
    that opens a session's transcript."""
    return lambda nn, word, name: phones() and send(
        f"Session {nn} {'needs you' if word == 'waiting' else 'is done'}", said(nn, name), link(nn))


def main() -> None:
    if sys.argv[1:] == ["test"]:
        if not phones():
            print("No phone has allowed the buzz yet. Tap the bell on 1100's rail first.")
            return
        print(send(TITLE, "A test buzz from 1100.", "/"))
        return
    print(__doc__)


if __name__ == "__main__":
    main()
