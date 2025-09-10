
import os, sys, re, hashlib, smtplib, ssl, difflib
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup
from pathlib import Path

TARGET_URL = os.environ.get("TARGET_URL", "https://www.softbank.jp/mobile/products/google-pixel-watch/google-pixel-watch-3/")
CSS_SELECTOR = os.environ.get("CSS_SELECTOR")  # 例: "main" や ".p-productDetail__detail"
STATE_FILE = Path(".state/pixel_watch_3.hash")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
TO_EMAIL = os.environ.get("TO_EMAIL", SMTP_USER)

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}

def fetch_content(url: str, selector: str | None) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    # 不要タグ除去
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    if selector:
        nodes = soup.select(selector)
        text = "\n\n".join(n.get_text(" ", strip=True) for n in nodes)
    else:
        text = soup.get_text(" ", strip=True)
    # 空白正規化
    text = re.sub(r"\s+", " ", text)
    return text

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_prev() -> str | None:
    if STATE_FILE.exists():
        return STATE_FILE.read_text(encoding="utf-8").strip() or None
    return None

def save_hash(h: str) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(h, encoding="utf-8")

def send_mail(subject: str, body: str):
    if not (SMTP_USER and SMTP_PASS and TO_EMAIL):
        print("SMTP credentials missing. Skip email.", file=sys.stderr)
        return
    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = TO_EMAIL
    ctx = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls(context=ctx)
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
    print("Email sent to", TO_EMAIL)

def main():
    text = fetch_content(TARGET_URL, CSS_SELECTOR)
    cur = sha256(text)
    prev = load_prev()
    print("Current hash:", cur)
    print("Previous hash:", prev)

    if prev and prev != cur:
        # 簡易 diff（先頭から数十行程度）
        diff = difflib.unified_diff(
            prev.splitlines(), cur.splitlines(), lineterm=""
        )
        # 実際にはハッシュなので本文 diff は扱いづらい。通知本文には URL と注意書きを記載。
        body = f"""SoftBank Pixel Watch 3 ページに更新を検出しました。
URL: {TARGET_URL}

このメールは GitHub Actions から自動送信されています。
"""
        send_mail("【監視】SoftBank Pixel Watch 3 ページが更新", body)

    save_hash(cur)

if __name__ == "__main__":
    main()
