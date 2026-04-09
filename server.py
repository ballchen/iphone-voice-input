import os
import sys
import socket
import threading
import time
import ipaddress
import traceback
from datetime import datetime
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
RUNTIME_DIR = Path(os.getenv("LOCALAPPDATA", str(Path.home()))) / "VoiceInput"
LOG_FILE = RUNTIME_DIR / "voiceinput.log"

# ------------------------------------------------------------------
# Flask + SocketIO
# ------------------------------------------------------------------
app = Flask(__name__, static_folder=str(WEB_DIR))
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
keyboard = Controller()
server_start_error = None


def _set_clipboard_text_windows(text: str):
    import ctypes

    CF_UNICODETEXT = 13
    GMEM_MOVEABLE = 0x0002

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    for _ in range(10):
        if user32.OpenClipboard(None):
            break
        time.sleep(0.01)
    else:
        raise RuntimeError("OpenClipboard failed")
    try:
        if not user32.EmptyClipboard():
            raise RuntimeError("EmptyClipboard failed")

        data = ctypes.create_unicode_buffer(text)
        size = ctypes.sizeof(data)
        hmem = kernel32.GlobalAlloc(GMEM_MOVEABLE, size)
        if not hmem:
            raise RuntimeError("GlobalAlloc failed")

        locked = kernel32.GlobalLock(hmem)
        if not locked:
            kernel32.GlobalFree(hmem)
            raise RuntimeError("GlobalLock failed")
        try:
            ctypes.memmove(locked, ctypes.addressof(data), size)
        finally:
            kernel32.GlobalUnlock(hmem)

        if not user32.SetClipboardData(CF_UNICODETEXT, hmem):
            kernel32.GlobalFree(hmem)
            raise RuntimeError("SetClipboardData failed")
    finally:
        user32.CloseClipboard()


def _get_clipboard_text_windows() -> str:
    import ctypes

    CF_UNICODETEXT = 13

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    for _ in range(10):
        if user32.OpenClipboard(None):
            break
        time.sleep(0.01)
    else:
        return ""
    try:
        hdata = user32.GetClipboardData(CF_UNICODETEXT)
        if not hdata:
            return ""
        locked = kernel32.GlobalLock(hdata)
        if not locked:
            return ""
        try:
            return ctypes.wstring_at(locked)
        finally:
            kernel32.GlobalUnlock(hdata)
    finally:
        user32.CloseClipboard()


def paste_text_ime_safe(text: str):
    original = _get_clipboard_text_windows()
    _set_clipboard_text_windows(text)
    keyboard.press(Key.ctrl)
    keyboard.press("v")
    keyboard.release("v")
    keyboard.release(Key.ctrl)
    # Give the target app a moment to consume clipboard content before restore.
    time.sleep(0.03)
    _set_clipboard_text_windows(original)


def log_line(message: str):
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")


def is_local_server_listening() -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.6)
    try:
        return s.connect_ex(("127.0.0.1", PORT)) == 0
    finally:
        s.close()


def show_start_error_dialog(message: str):
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, message, "Voice Input Startup Error", 0x10)
    except Exception:
        pass


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
    return jsonify(
        {
            "status": "running",
            "ip": (ips[0] if ips else "127.0.0.1"),
            "ips": ips,
            "urls": urls,
            "port": PORT,
            "server_error": server_start_error,
            "log_file": str(LOG_FILE),
        }
    )


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(str(WEB_DIR), path)


@app.route("/favicon.ico")
def favicon():
    # Keep browser console clean for default favicon probing.
    return ("", 204)


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
    paste_ok = False
    if sys.platform == "win32":
        try:
            # Paste is IME-safe: avoids Zhuyin/Pinyin conversion issues.
            paste_text_ime_safe(text)
            paste_ok = True
        except Exception as exc:
            log_line(f"IME-safe paste fallback triggered: {type(exc).__name__}: {exc}")
    if not paste_ok:
        keyboard.type(text)
    if data.get("newline"):
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
    emit("typed", {"ok": True})


# ------------------------------------------------------------------
# Server thread
# ------------------------------------------------------------------
def run_server():
    global server_start_error
    try:
        log_line(f"Starting HTTP server on 0.0.0.0:{PORT}")
        socketio.run(
            app,
            host="0.0.0.0",
            port=PORT,
            use_reloader=False,
            log_output=False,
            allow_unsafe_werkzeug=True,
        )
    except Exception as exc:
        server_start_error = f"{type(exc).__name__}: {exc}"
        print(f"[!] Server failed to start: {server_start_error}")
        log_line(f"Server failed to start: {server_start_error}")
        log_line(traceback.format_exc())
        traceback.print_exc()


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

    def open_local_test_page(icon, item):
        import webbrowser
        webbrowser.open(f"http://127.0.0.1:{PORT}")

    def open_log_folder(icon, item):
        if sys.platform == "win32":
            os.startfile(str(RUNTIME_DIR))
            return
        import webbrowser
        webbrowser.open(str(RUNTIME_DIR))

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
        pystray.MenuItem("Open Local Test Page", open_local_test_page),
        pystray.MenuItem("Open Log Folder", open_log_folder),
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
    log_line("VoiceInput process starting")
    generate_icons()

    t = threading.Thread(target=run_server, daemon=True)
    t.start()

    ips = get_local_ips()
    if ips:
        print("[*] Server URLs:")
        for ip in ips:
            print(f"    http://{ip}:{PORT}")
            log_line(f"Candidate LAN URL: http://{ip}:{PORT}")
    else:
        print(f"[*] Server: http://127.0.0.1:{PORT}")
        log_line("No LAN IP candidates found; fallback to localhost only")
    time.sleep(1.2)   # Wait for Flask to bind
    if not server_start_error and not is_local_server_listening():
        server_start_error = (
            f"Server did not bind on 127.0.0.1:{PORT}. "
            "Possible causes: firewall rules, another process occupying port, or startup exception."
        )
    if server_start_error:
        err = f"HTTP server startup failed.\n\n{server_start_error}\n\nLog file:\n{LOG_FILE}"
        print("[!] HTTP server did not start correctly. Check logs.")
        log_line(f"Startup health check failed: {server_start_error}")
        show_start_error_dialog(err)

    create_tray_icon()
