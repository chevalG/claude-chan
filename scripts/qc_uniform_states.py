"""校服版实机状态 QC：通过 Claude Code hook 接口切换状态，PrintWindow 抓取桌宠窗口。

    .venv\\Scripts\\python.exe scripts\\qc_uniform_states.py

需要桌宠已经启动（start-claude-chan.bat），端口 47801。输出 qc/uniform-<状态>.png。
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import json
import time
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
QC = ROOT / "qc"
QC.mkdir(exist_ok=True)
URL = "http://127.0.0.1:47801"
u = ctypes.windll.user32


def find_hwnd() -> int | None:
    hwnd = None
    cb = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

    def exe_of(pid: int) -> str:
        h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if not h:
            return ""
        try:
            buf = ctypes.create_unicode_buffer(1024)
            size = wt.DWORD(1024)
            if ctypes.windll.kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
                return buf.value.lower()
            return ""
        finally:
            ctypes.windll.kernel32.CloseHandle(h)

    def enum(h, _):
        nonlocal hwnd
        n = u.GetWindowTextLengthW(h)
        if not n:
            return True
        buf = ctypes.create_unicode_buffer(n + 1)
        u.GetWindowTextW(h, buf, n + 1)
        if buf.value != "Claude-Chan":
            return True
        pid = wt.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(pid))
        exe = exe_of(pid.value)
        if "pythonw" in exe or "claude-chan" in exe and "GPT-Chan" not in exe:
            hwnd = h
        return True

    u.EnumWindows(cb(enum), 0)
    return hwnd


def grab(hwnd: int, path: Path) -> None:
    r = wt.RECT()
    u.GetWindowRect(hwnd, ctypes.byref(r))
    w, h = r.right - r.left, r.bottom - r.top
    hdc = u.GetDC(hwnd)
    mdc = ctypes.windll.gdi32.CreateCompatibleDC(hdc)
    bmp = ctypes.windll.gdi32.CreateCompatibleBitmap(hdc, w, h)
    ctypes.windll.gdi32.SelectObject(mdc, bmp)
    u.PrintWindow(hwnd, mdc, 2)

    class BMI(ctypes.Structure):
        _fields_ = [
            ("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32), ("biHeight", ctypes.c_int32),
            ("biPlanes", ctypes.c_uint16), ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
            ("biSizeImage", ctypes.c_uint32), ("biXPels", ctypes.c_int32), ("biYPels", ctypes.c_int32),
            ("biClrUsed", ctypes.c_uint32), ("biClrImportant", ctypes.c_uint32),
        ]

    bmi = BMI()
    bmi.biSize = ctypes.sizeof(BMI)
    bmi.biWidth = w
    bmi.biHeight = -h
    bmi.biPlanes = 1
    bmi.biBitCount = 32
    buf = ctypes.create_string_buffer(w * h * 4)
    ctypes.windll.gdi32.GetDIBits(mdc, bmp, 0, h, buf, ctypes.byref(bmi), 0)
    Image.frombuffer("RGBA", (w, h), buf, "raw", "BGRA", 0, 1).save(path)
    ctypes.windll.gdi32.DeleteObject(bmp)
    ctypes.windll.gdi32.DeleteDC(mdc)
    u.ReleaseDC(hwnd, hdc)


def send(event: str, extra: dict | None = None) -> None:
    body = {"session_id": "uniform-qc", "cwd": str(ROOT), "hook_event_name": event, **(extra or {})}
    req = urllib.request.Request(URL + "/event", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=5).read()


def state() -> tuple[str, str]:
    with urllib.request.urlopen(URL + "/state", timeout=5) as r:
        d = json.load(r)
    return d["target"]["state"], d["engine"]["current"]


def capture(hwnd: int, name: str, wait: float) -> None:
    time.sleep(wait)
    t, c = state()
    grab(hwnd, QC / f"uniform-{name}.png")
    print(f"{name}: target={t} clip={c}")


def main() -> None:
    hwnd = find_hwnd()
    if not hwnd:
        raise SystemExit("没找到 Claude-Chan 桌宠窗口")
    send("SessionStart")
    capture(hwnd, "idle", 6)
    send("UserPromptSubmit", {"prompt": "qc"})
    capture(hwnd, "thinking", 10)
    send("PreToolUse", {"tool_name": "Read"})
    capture(hwnd, "reading", 10)
    send("PreToolUse", {"tool_name": "Write"})
    capture(hwnd, "writing", 10)
    send("PermissionRequest", {"tool_name": "AskUserQuestion"})
    capture(hwnd, "confirmation", 10)
    send("Notification", {"notification_type": "idle_prompt"})
    time.sleep(1)
    send("UserPromptSubmit", {"prompt": "qc2"})
    time.sleep(2)
    send("Stop")
    capture(hwnd, "complete", 8)
    send("UserPromptSubmit", {"prompt": "qc3"})
    time.sleep(3)
    send("StopFailure")
    capture(hwnd, "error", 6)
    send("UserPromptSubmit", {"prompt": "qc4"})
    time.sleep(1)
    send("Notification", {"notification_type": "idle_prompt"})
    capture(hwnd, "idle-final", 8)
    print("done")


if __name__ == "__main__":
    main()
