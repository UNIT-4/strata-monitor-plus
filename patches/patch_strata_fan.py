# -*- coding: utf-8 -*-
"""Strata Monitor 内置显卡风扇控制 补丁
用法：python patch_strata_fan.py    （幂等：重复执行自动跳过已打部分）
效果：GET/POST /fan 接口 + 监控页「显卡风扇」卡片（系统默认/中等/激进/自定义滑块）
安全：≥88°C 强制满速、≥83°C 自定义至少90%、Strata 退出自动交还驱动、状态存 fan_state.json 重启恢复
依赖前置补丁：patch_strata_monitor_cn.py（先中文化再打本补丁，本补丁自带中文）
"""
import os
import sys

# ---- 路径自适应：命令行参数 > 环境变量 STRATA_ROOT > 常见位置探测 ----
import os as _os, sys as _sys

def _find_root():
    env = _os.environ.get("STRATA_ROOT")
    if env:
        return env.rstrip("\\/")
    for p in (r"D:\strata-new\Strata", r"D:\strata\Strata", r"C:\strata\Strata",
              _os.path.expanduser(r"~\Strata")):
        q = _os.path.expandvars(p)
        if _os.path.isdir(_os.path.join(q, "serve")):
            return q
    raise SystemExit("找不到 Strata 安装目录：请设环境变量 STRATA_ROOT 或以命令行参数传入其路径")

ROOT = _sys.argv[1] if len(_sys.argv) > 1 else _find_root()


TELEMETRY = os.path.join(ROOT, "serve", "telemetry.py")
SERVER = os.path.join(ROOT, "serve", "server.py")
HTML = os.path.join(ROOT, "serve", "web", "index.html")
APPJS = os.path.join(ROOT, "serve", "web", "app.js")

GOV_CODE = '''

# ================= 显卡风扇调节器（本地补丁：Monitor 面板用） =================
import atexit as _atexit
import json as _json

FAN_STATE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fan_state.json")
_FAN_CRIT_C, _FAN_WARN_C = 88.0, 83.0
_FAN_CURVE_MID = [(0, 30), (40, 40), (50, 50), (60, 62), (70, 75), (78, 85)]
_FAN_CURVE_HOT = [(0, 35), (38, 50), (48, 65), (58, 82), (68, 100)]


def _fan_curve(curve, temp):
    t = 30
    for start, pct in curve:
        if temp >= start:
            t = pct
    return t


class FanGovernor:
    """Manual GPU fan control with guard rails. auto = hands the card back to the driver."""

    def __init__(self):
        self.lib = self.dev = None
        self.lo, self.hi = 30, 100
        self.mode, self.pct = "auto", 60
        self.last_sent = None
        self.lock = threading.Lock()
        self._stop = threading.Event()
        names = ["nvml.dll", os.path.join(os.environ.get("ProgramFiles", r"C:\\Program Files"),
                                          "NVIDIA Corporation", "NVSMI", "nvml.dll")] if os.name == "nt" \\
            else ["libnvidia-ml.so.1", "libnvidia-ml.so"]
        for n in names:
            try:
                self.lib = ctypes.CDLL(n)
                break
            except OSError:
                continue
        if self.lib is not None:
            try:
                init = getattr(self.lib, "nvmlInit_v2", None) or self.lib.nvmlInit
                if init() != 0:
                    self.lib = None
                else:
                    h = ctypes.c_void_p()
                    get = getattr(self.lib, "nvmlDeviceGetHandleByIndex_v2", None) or self.lib.nvmlDeviceGetHandleByIndex
                    if get(ctypes.c_uint(0), ctypes.byref(h)) != 0:
                        self.lib = None
                    else:
                        self.dev = h
            except (AttributeError, OSError):
                self.lib = None
        if self.dev is not None:
            lo, hi = ctypes.c_uint(), ctypes.c_uint()
            try:
                if self.lib.nvmlDeviceGetMinMaxFanSpeed(self.dev, ctypes.byref(lo), ctypes.byref(hi)) == 0:
                    self.lo, self.hi = lo.value, hi.value
            except (AttributeError, OSError):
                pass
        try:
            with open(FAN_STATE_PATH, encoding="utf-8") as f:
                st = _json.load(f)
            if st.get("mode") in ("auto", "mid", "hot", "custom"):
                self.mode = st["mode"]
            self.pct = max(self.lo, min(self.hi, int(st.get("pct", 60))))
        except (OSError, ValueError):
            pass
        if self.supported():
            if self.mode != "auto":
                self._enforce()
            _atexit.register(self.release)
            threading.Thread(target=self._loop, daemon=True).start()

    def supported(self):
        return self.lib is not None and self.dev is not None

    def _temp(self):
        v = ctypes.c_uint()
        try:
            return float(v.value) if self.lib.nvmlDeviceGetTemperature(self.dev, ctypes.c_uint(0), ctypes.byref(v)) == 0 else None
        except (AttributeError, OSError):
            return None

    def _fan(self):
        v = ctypes.c_uint()
        try:
            fn = getattr(self.lib, "nvmlDeviceGetFanSpeed_v2", None)
            if fn and fn(self.dev, ctypes.c_uint(0), ctypes.byref(v)) == 0:
                return int(v.value)
            fn = self.lib.nvmlDeviceGetFanSpeed
            if fn(self.dev, ctypes.byref(v)) == 0:
                return int(v.value)
        except (AttributeError, OSError):
            pass
        return None

    def _policy(self):
        v = ctypes.c_uint()
        try:
            if self.lib.nvmlDeviceGetFanControlPolicy_v2(self.dev, ctypes.c_uint(0), ctypes.byref(v)) == 0:
                return int(v.value)
        except (AttributeError, OSError):
            pass
        return None

    def _set(self, pct):
        try:
            self.lib.nvmlDeviceSetFanSpeed_v2(self.dev, ctypes.c_uint(0), ctypes.c_uint(max(self.lo, min(self.hi, int(pct)))))
            self.last_sent = pct
        except (AttributeError, OSError):
            pass

    def _auto(self):
        try:
            self.lib.nvmlDeviceSetFanControlPolicy(self.dev, ctypes.c_uint(0), ctypes.c_uint(0))
            self.last_sent = None
        except (AttributeError, OSError):
            pass

    def target(self, temp):
        if self.mode == "mid":
            return _fan_curve(_FAN_CURVE_MID, temp)
        if self.mode == "hot":
            return _fan_curve(_FAN_CURVE_HOT, temp)
        if self.mode == "custom":
            return max(self.pct, 90) if temp >= _FAN_WARN_C else self.pct
        return None

    def _enforce(self):
        t = self._temp()
        if t is None:
            return
        if self.mode == "auto":
            return
        want = self.hi if t >= _FAN_CRIT_C else self.target(t)
        if want is not None and want != self.last_sent:
            self._set(want)

    def _loop(self):
        while not self._stop.is_set():
            try:
                with self.lock:
                    self._enforce()
            except Exception:  # noqa: BLE001 - the governor must never take the server down
                pass
            self._stop.wait(3.0)

    def apply(self, mode, pct=None):
        if mode not in ("auto", "mid", "hot", "custom"):
            raise ValueError("mode 需为 auto / mid / hot / custom")
        with self.lock:
            self.mode = mode
            if pct is not None:
                self.pct = max(self.lo, min(self.hi, int(pct)))
            if mode == "auto":
                self._auto()
            else:
                self._enforce()
        try:
            with open(FAN_STATE_PATH, "w", encoding="utf-8") as f:
                _json.dump({"mode": self.mode, "pct": self.pct}, f)
        except OSError:
            pass
        return self.view()

    def release(self):
        if self.supported() and self.mode != "auto":
            self._auto()

    def view(self):
        t = self._temp()
        return {"supported": True, "mode": self.mode, "pct": self.pct, "min": self.lo, "max": self.hi,
                "current": self._fan(), "temp": t, "driver_auto": self._policy() == 0,
                "crit_c": _FAN_CRIT_C, "target": self.target(t) if t is not None else None}


_fan_governor = None
_fan_governor_lock = threading.Lock()


def fan_governor():
    """The one governor per process, or None when no NVIDIA/NVML card is present."""
    global _fan_governor
    with _fan_governor_lock:
        if _fan_governor is None:
            _fan_governor = FanGovernor()
        return _fan_governor if _fan_governor.supported() else None
'''

GET_ROUTE = '''            if path == "/fan":
                from serve import telemetry as _tl
                g = _tl.fan_governor()
                self._json(200, g.view() if g else {"supported": False})
                return
'''

POST_ROUTE = '''            if path == "/fan":
                if not self._own_page("the fan can be changed"):
                    return
                import json as _fjson
                try:
                    want = _fjson.loads(self._body() or b"{}")
                except (ValueError, TypeError):
                    self._json(400, {"error": {"message": "invalid json"}})
                    return
                from serve import telemetry as _tl
                g = _tl.fan_governor()
                if not g:
                    self._json(501, {"error": {"message": "fan control needs an NVIDIA card with NVML"}})
                    return
                try:
                    self._json(200, g.apply(want.get("mode"), want.get("pct")))
                except ValueError as e:
                    self._json(400, {"error": {"message": str(e)}})
                return
'''

CARD_HTML = '''      <div class="st-card" id="fan-card" hidden>
        <div class="req-head"><span class="card-title">显卡风扇</span><span class="muted small" id="fan-now"></span></div>
        <div class="bar-row" style="gap:14px;flex-wrap:wrap">
          <label style="display:flex;align-items:center;gap:4px"><input type="radio" name="fan-mode" value="auto"> 系统默认</label>
          <label style="display:flex;align-items:center;gap:4px"><input type="radio" name="fan-mode" value="mid"> 中等</label>
          <label style="display:flex;align-items:center;gap:4px"><input type="radio" name="fan-mode" value="hot"> 激进</label>
          <label style="display:flex;align-items:center;gap:4px"><input type="radio" name="fan-mode" value="custom"> 自定义</label>
        </div>
        <div class="bar-row" style="align-items:center;gap:10px">
          <input type="range" id="fan-pct" min="30" max="100" value="60" style="flex:1;accent-color:var(--st-accent)">
          <b id="fan-pct-num">60%</b>
          <button class="st-btn st-btn--primary" id="fan-apply" type="button">应用</button>
        </div>
        <p class="muted small" id="fan-hint"></p>
      </div>

      <div class="st-card mcp-card" id="mcp-card" hidden>'''

FAN_JS = '''

// ================= 显卡风扇面板（本地补丁） =================
(function () {
  var card = document.getElementById("fan-card");
  if (!card) return;
  var radios = card.querySelectorAll("input[name=fan-mode]");
  var slider = document.getElementById("fan-pct");
  var pctNum = document.getElementById("fan-pct-num");
  var btn = document.getElementById("fan-apply");
  var now = document.getElementById("fan-now");
  var hint = document.getElementById("fan-hint");
  var lastSig = "";
  function send(mode, pct) {
    btn.disabled = true;
    fetch("fan", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: mode, pct: pct }) })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (x) { if (!x.ok) hint.textContent = "失败：" + ((x.j.error && x.j.error.message) || ""); render(x.j); })
      .catch(function () { hint.textContent = "请求失败"; })
      .finally(function () { btn.disabled = false; });
  }
  function render(v) {
    if (!v || v.supported === false) { card.hidden = true; return; }
    card.hidden = false;
    slider.min = v.min; slider.max = v.max;
    pctNum.textContent = v.pct + "%";
    if (document.activeElement !== slider) slider.value = v.pct;
    for (var i = 0; i < radios.length; i++) radios[i].checked = radios[i].value === v.mode;
    var modeCn = { auto: "系统默认", mid: "中等", hot: "激进", custom: "自定义" }[v.mode] || v.mode;
    now.textContent = "温度 " + (v.temp == null ? "?" : Math.round(v.temp)) + "°C · 当前转速 "
      + (v.current == null ? "?" : v.current) + "% · 模式 " + modeCn;
    hint.textContent = (v.mode === "auto"
      ? "跟随驱动原生调教。中等/激进为温控曲线自动调速；自定义用滑块钉死转速。"
      : "调速中：目标 " + (v.target == null ? "?" : v.target) + "%，保护线 " + v.crit_c + "°C 强制满速；Strata 退出时自动交还驱动。")
      + "（重启 Strata 后需后端补丁生效，若显示 404 请重启服务）";
    var sig = v.mode + "|" + v.pct;
    lastSig = sig;
  }
  function poll() {
    fetch("fan").then(function (r) { return r.ok ? r.json() : { supported: false }; })
      .then(render).catch(function () { if (card.hidden) card.hidden = true; });
  }
  for (var i = 0; i < radios.length; i++) radios[i].addEventListener("change", function () {
    var mode = this.checked ? this.value : null;
    if (mode) send(mode, parseInt(slider.value, 10));
  });
  slider.addEventListener("input", function () { pctNum.textContent = slider.value + "%"; });
  btn.addEventListener("click", function () { send("custom", parseInt(slider.value, 10)); });
  setInterval(poll, 2500);
  poll();
})();
'''

def patch(path, pairs, label):
    with open(path, "r", encoding="utf-8", newline="") as f:
        s = f.read()
    ok = skip = miss = 0
    for old, new in pairs:
        if new in s:
            skip += 1
            continue
        n = s.count(old)
        if n != 1:
            print(f"  [MISS x{n}] {label}: {old[:60]!r}")
            miss += 1
            continue
        s = s.replace(old, new)
        ok += 1
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(s)
    print(f"[{label}] 替换 {ok}，跳过 {skip}，未命中 {miss}")
    return miss == 0

def main():
    tele_src = open(TELEMETRY, encoding="utf-8").read()
    if "class FanGovernor" in tele_src:
        print("[telemetry.py] 已打过，跳过")
        r1 = True
    else:
        r1 = patch(TELEMETRY, [("\nclass Telemetry", GOV_CODE + "\n\nclass Telemetry")], "telemetry.py")
    r2 = patch(SERVER, [('            if path == "/metrics":', GET_ROUTE + '            if path == "/metrics":')], "server.py GET")
    r3 = patch(SERVER, [('            if path in ("/unload", "/load") and not self._control_body():', POST_ROUTE + '            if path in ("/unload", "/load") and not self._control_body():')], "server.py POST")
    r4 = patch(HTML, [('      <div class="st-card mcp-card" id="mcp-card" hidden>', CARD_HTML)], "index.html")
    r5 = patch(APPJS, [("\n", "\n")], "app.js 探针") if False else True
    # app.js：追加到文件末尾
    s = open(APPJS, encoding="utf-8").read()
    if "显卡风扇面板" in s:
        print("[app.js] 已打过，跳过")
        r5 = True
    else:
        with open(APPJS, "a", encoding="utf-8", newline="") as f:
            f.write(FAN_JS)
        print("[app.js] 已追加风扇面板脚本")
        r5 = True
    print("\n结论:", "成功 —— 前端刷新即可看到卡片（未重启后端时显示 404 提示）；重启 strata 后功能全量可用"
          if all([r1, r2, r3, r4, r5]) else "存在未命中项")
    return 0 if all([r1, r2, r3, r4, r5]) else 1

if __name__ == "__main__":
    sys.exit(main())
