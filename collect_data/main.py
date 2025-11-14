import argparse
import os
import re
import sys
from pathlib import Path
from hashlib import md5
from urllib.parse import urlparse, unquote, urlsplit
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

#!/usr/bin/env python3
# main.py
# Télécharge le contenu des URLs fournies (fichier ou liste d'arguments)
# Usage:
#   python main.py urls.txt
#   python main.py https://example.com https://example.org -o downloads


DEFAULT_USER_AGENT = "Mozilla/5.0 (compatible; site-downloader/1.0; +https://example.local)"
INVALID_FILENAME_RE = re.compile(r'[^A-Za-z0-9._-]+')


def make_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 503, 504)):
    s = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(["GET", "HEAD", "OPTIONS"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    s.headers.update({"User-Agent": DEFAULT_USER_AGENT})
    return s


def sanitize_filename(url: str, content_type: str | None = None) -> str:
    """
    Génère un nom de fichier sûr basé sur l'URL et le content-type.
    Si le nom dérivé de l'URL est trop long ou vide, on utilise un hash.
    """
    parts = urlsplit(url)
    netloc = parts.netloc or "unknown"
    path = unquote(parts.path or "")
    if path.endswith("/"):
        path = path + "index"
    base = (netloc + path).strip("/")
    base = INVALID_FILENAME_RE.sub("-", base)
    base = base[:200]  # limiter la longueur
    if not base:
        base = "file"
    # déterminer extension
    ext = ""
    if content_type:
        if "html" in content_type:
            ext = ".html"
        elif "json" in content_type:
            ext = ".json"
        elif "xml" in content_type:
            ext = ".xml"
        elif "javascript" in content_type or "ecmascript" in content_type:
            ext = ".js"
        elif "css" in content_type:
            ext = ".css"
        elif "image/" in content_type:
            mime_ext = content_type.split("/", 1)[1].split(";", 1)[0]
            ext = f".{mime_ext}"
        # otherwise keep ext empty
    if not Path(base).suffix and ext:
        filename = base + ext
    else:
        filename = base
    # si trop long ou étrange, utiliser hash suffix
    if len(filename) > 240:
        filename = filename[:120] + "-" + md5(url.encode("utf-8")).hexdigest()[:12]
        if ext:
            filename += ext
    return filename


def download_url(session: requests.Session, url: str, outdir: Path, timeout: int = 20) -> tuple[str, int]:
    """
    Télécharge l'URL et écrit le contenu dans outdir.
    Retourne (chemin_fichier, HTTP_status_code)
    """
    try:
        r = session.get(url, stream=True, timeout=timeout, allow_redirects=True)
    except requests.RequestException as e:
        raise RuntimeError(f"Erreur requête pour {url}: {e}")

    status = r.status_code
    if status >= 400:
        r.close()
        raise RuntimeError(f"Erreur HTTP {status} pour {url}")

    content_type = r.headers.get("Content-Type", "")
    filename = sanitize_filename(url, content_type)
    outpath = outdir / filename

    # S'il existe déjà, on ajoute un suffixe numérique
    if outpath.exists():
        stem = outpath.stem
        suffix = outpath.suffix
        i = 1
        while (outdir / f"{stem}-{i}{suffix}").exists():
            i += 1
        outpath = outdir / f"{stem}-{i}{suffix}"

    # Écrire en binaire
    try:
        with open(outpath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    finally:
        r.close()

    return str(outpath), status


def main():
    parser = argparse.ArgumentParser(description="Télécharger le contenu d'un site depuis des URL (fichier ou liste).")
    parser.add_argument("inputs", nargs="+", help="Fichier contenant les URLs (une par ligne) ou URLs directes.")
    parser.add_argument("-o", "--outdir", default="downloads", help="Répertoire de sortie (par défaut: downloads)")
    parser.add_argument("-t", "--timeout", type=int, default=20, help="Timeout en secondes par requête")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Construire la liste d'URLs: si un input est un fichier existant, lire ses lignes
    urls = []
    for item in args.inputs:
        p = Path(item)
        if p.exists() and p.is_file():
            with p.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    urls.append(line)
        else:
            urls.append(item)

    if not urls:
        print("Aucune URL fournie.", file=sys.stderr)
        sys.exit(1)

    session = make_session()
    failures = 0
    for u in urls:
        print(f"Téléchargement: {u}")
        try:
            path, status = download_url(session, u, outdir, timeout=args.timeout)
            print(f"  -> {path} (HTTP {status})")
        except Exception as e:
            failures += 1
            print(f"  Erreur: {e}", file=sys.stderr)

    if failures:
        print(f"Terminé avec {failures} échecs.", file=sys.stderr)
        sys.exit(2)
    else:
        print("Terminé.")
        sys.exit(0)


if __name__ == "__main__":
    main()