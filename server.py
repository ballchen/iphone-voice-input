import os
import sys
import json
import socket
import threading
import time
import ipaddress
from pathlib import Path

from flask import Flask, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
from pynput.keyboard import Controller, Key
from PIL import Image, ImageDraw
import qrcode
import pystray

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------
BASE_DIR = Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else Path(__file__).parent
WEB_DIR = BASE_DIR / "web"
ICON_DIR = WEB_DIR / "icons"
PORT = 8765

# ------------------------------------------------------------------
# Flask + SocketIO
# ------------------------------------------------------------------
app = Flask(__name__, static_folder=str(WEB_DIR))
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
keyboard = Controller()


def _is_candidate_ip(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    if addr.version != 4:
        return False
    return not (addr.is_loopback or addr.is_link_local or addr.is_multicast or addr.is_unspecified)


def get_local_ips() -> list[str]:
    found = []
    seen = set()

    def add_ip(ip: str):
        if not _is_candidate_ip(ip):
            return
        if ip in seen:
            return
        seen.add(ip)
        found.append(ip)

    # Route-based probing often finds the currently active NIC address.
    for probe_target in (("8.8.8.8", 80), ("1.1.1.1", 80)):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(probe_target)
            add_ip(s.getsockname()[0])
        except Exception:
            pass
        finally:
            s.close()

    try:
        _, _, host_ips = socket.gethostbyname_ex(socket.gethostname())
        for ip in host_ips:
            add_ip(ip)
    except Exception:
        pass

    try:
        infos = socket.getaddrinfo(socket.gethostname(), None, family=socket.AF_INET)
        for info in infos:
            add_ip(info[4][0])
    except Exception:
        pass

    return found


def get_local_ip() -> str:
    ips = get_local_ips()
    return ips[0] if ips else "127.0.0.1"


# ------------------------------------------------------------------
# Generate app icons at startup
# ------------------------------------------------------------------
def generate_icons():
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    for size in (192, 512):
        path = ICON_DIR / f"icon-{size}.png"
        if path.exists():
            continue
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Rounded background
        draw.rounded_rectangle([0, 0, size, size], radius=size // 5, fill="#4F46E5")

        # Microphone body
        cx = size // 2
        mw = size // 8
        mh = size // 3
        top = size // 6
        draw.rounded_rectangle(
            [cx - mw, top, cx + mw, top + mh],
            radius=mw,
            fill="white",
        )

        # Microphone stand arc
        arc_r = mw * 2
        arc_top = top + mh - arc_r
        sw = max(2, size // 24)
        draw.arc(
            [cx - arc_r, arc_top, cx + arc_r, arc_top + arc_r * 2],
            start=0, end=180,
            fill="white", width=sw,
        )

        # Pole + base
        pole_y1 = arc_top + arc_r
        pole_y2 = pole_y1 + mw
        draw.line([cx, pole_y1, cx, pole_y2], fill="white", width=sw)
        draw.line([cx - mw, pole_y2, cx + mw, pole_y2], fill="white", width=sw)

        img.save(str(path))


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory(str(WEB_DIR), "index.html")


@app.route("/api/status")
def status():
    ips = get_local_ips()
    urls = [f"http://{ip}:{PORT}" for ip in ips]
    return jsonify({"status": "running", "ip": (ips[0] if ips else "127.0.0.1"), "ips": ips, "urls": urls, "port": PORT})


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(str(WEB_DIR), path)


# ------------------------------------------------------------------
# WebSocket
# ------------------------------------------------------------------
@socketio.on("connect")
def on_connect():
    print("[WS] client connected")


@socketio.on("disconnect")
def on_disconnect():
    print("[WS] client disconnected")


@socketio.on("type_text")
def on_type_text(data):
    text = data.get("text", "").strip()
    if not text:
        return
    time.sleep(0.05)          # Let the focus return to target window
    keyboard.type(text)
    if data.get("newline"):
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
    emit("typed", {"ok": True})


# ------------------------------------------------------------------
# Server thread
# ------------------------------------------------------------------
def run_server():
    socketio.run(
        app,
        host="0.0.0.0",
        port=PORT,
        use_reloader=False,
        log_output=False,
    )


# ------------------------------------------------------------------
# System tray
# ------------------------------------------------------------------
def make_tray_image(size=64) -> Image.Image:
    img = Image.new("RGB", (size, size), "#4F46E5")
    draw = ImageDraw.Draw(img)
    cx = size // 2
    mw, mh = size // 8, size // 3
    top = size // 6
    draw.rounded_rectangle([cx - mw, top, cx + mw, top + mh], radius=mw, fill="white")
    return img


def create_tray_icon():
    ips = get_local_ips()
    primary_ip = ips[0] if ips else "127.0.0.1"
    primary_url = f"http://{primary_ip}:{PORT}"

    def show_qr_for_url(url: str):
        def _show_qr(icon, item):
            qr = qrcode.make(url)
            qr.show()
        return _show_qr

    def copy_url(icon, item):
        import subprocess
        subprocess.run("clip", input=primary_url.encode(), check=True, shell=True)

    def copy_all_urls(icon, item):
        import subprocess
        lines = [f"http://{ip}:{PORT}" for ip in ips] if ips else [primary_url]
        payload = ("\r\n".join(lines)).encode()
        subprocess.run("clip", input=payload, check=True, shell=True)

    def on_quit(icon, item):
        icon.stop()
        os._exit(0)

    qr_items = []
    if ips:
        for ip in ips:
            url = f"http://{ip}:{PORT}"
            qr_items.append(pystray.MenuItem(f"Show QR Code ({ip})", show_qr_for_url(url)))
    else:
        qr_items.append(pystray.MenuItem("Show QR Code", show_qr_for_url(primary_url)))

    menu = pystray.Menu(
        pystray.MenuItem(f"Voice Input  —  {primary_url}", None, enabled=False),
        *qr_items,
        pystray.MenuItem("Copy URL", copy_url),
        pystray.MenuItem("Copy All URLs", copy_all_urls),
        pystray.MenuItem("Quit", on_quit),
    )
    tray = pystray.Icon(
        "VoiceInput",
        make_tray_image(),
        f"Voice Input  {primary_url}",
        menu,
    )
    tray.run()


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------
if __name__ == "__main__":
    generate_icons()

    t = threading.Thread(target=run_server, daemon=True)
    t.start()

    ips = get_local_ips()
    if ips:
        print("[*] Server URLs:")
        for ip in ips:
            print(f"    http://{ip}:{PORT}")
    else:
        print(f"[*] Server: http://127.0.0.1:{PORT}")
    time.sleep(0.8)   # Wait for Flask to bind

    create_tray_icon()
