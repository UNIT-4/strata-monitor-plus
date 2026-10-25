# -*- coding: utf-8 -*-
"""Strata Monitor 并发槽位状态卡片 补丁（纯前端：后端 /metrics 官方就输出 live.slots，只是没渲染）
用法：python patch_strata_slots.py   （幂等）
效果：监控页新增「并发槽位」卡片——仅当服务以双并发(batch)启动时出现：每槽状态(空闲/读入/生成)、
     提示词读入进度、已生成 tok/s/用时、空闲槽还显示为下一轮暂存的 token 数；含排队与准入计数。
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


HTML = os.path.join(ROOT, "serve", "web", "index.html")
APPJS = os.path.join(ROOT, "serve", "web", "app.js")

CARD = '''      <div class="st-card" id="slot-card" hidden>
        <div class="req-head"><span class="card-title">并发槽位</span><span class="muted small" id="slot-sum"></span></div>
        <div id="slot-rows" style="display:flex;flex-direction:column;gap:8px"></div>
        <p class="muted small" id="slot-note">双并发模式实时状态：空闲槽保留的 token 可被同会话下一轮直接复用；「外部」为独占快车道或排队准入中的请求。</p>
      </div>

      <div class="st-card" id="fan-card" hidden>'''

JS = '''

// ================= 并发槽位面板（本地补丁：渲染官方 live.slots） =================
(function () {
  var card = document.getElementById("slot-card");
  if (!card) return;
  var rows = document.getElementById("slot-rows");
  var sum = document.getElementById("slot-sum");
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  var cn = { idle: "空闲", reading: "读入提示词", decoding: "生成中", generating: "生成中" };
  function bar(p, color) {
    var w = Math.max(0, Math.min(100, p || 0));
    return '<div style="height:5px;border-radius:3px;background:var(--st-line);overflow:hidden"><div style="height:100%;width:'
      + w + '%;background:' + color + '"></div></div>';
  }
  function poll() {
    fetch("metrics").then(function (r) { return r.ok ? r.json() : null; }).then(function (m) {
      var live = m && m.live, slots = live && live.slots;
      if (!slots || !slots.length) { card.hidden = true; return; }
      card.hidden = false;
      var busyN = 0;
      for (var i = 0; i < slots.length; i++) if (slots[i].state !== "idle") busyN++;
      var bits = [busyN + "/" + slots.length + " 槽活跃"];
      if (live.waiting) bits.push("排队 " + live.waiting);
      if (live.outside_slots > 0) bits.push("外部 " + live.outside_slots);
      if (live.running) bits.push("在跑 " + live.running);
      sum.textContent = bits.join(" · ");
      var html = slots.map(function (s) {
        var tone = s.state === "idle" ? "var(--st-ink-muted)" : (s.state === "reading" ? "#378add" : "#e0863a");
        var dot = '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:' + tone + ';margin-right:6px"></span>';
        var extra = [];
        if (s.state === "idle") extra.push(s.held_tokens ? "已暂存 " + s.held_tokens + " token（下一轮可续）" : "空置");
        if (s.prompt_tokens) extra.push("提示词 " + s.prompt_tokens);
        if (s.state === "reading" && s.prompt_read != null) extra.push("已读 " + s.prompt_read + (s.prompt_tokens ? "/" + s.prompt_tokens : ""));
        if (s.state !== "idle" && s.generated != null) extra.push("已生成 " + s.generated);
        if (s.tok_s != null) extra.push((s.tok_s.toFixed ? s.tok_s.toFixed(1) : s.tok_s) + " tok/s");
        if (s.elapsed_s != null && s.state !== "idle") extra.push(s.elapsed_s + "s");
        var pct = (s.state === "reading" && s.prompt_tokens && s.prompt_read != null) ? (100 * s.prompt_read / s.prompt_tokens) : null;
        return '<div style="border:1px solid var(--st-line);border-radius:9px;padding:7px 11px">'
          + '<div style="display:flex;justify-content:space-between;gap:10px;font-size:13px">'
          + '<span>' + dot + '槽 ' + s.slot + ' · ' + (cn[s.state] || esc(s.state)) + '</span>'
          + '<span class="muted" style="font-size:12px">' + esc(extra.join(" · ")) + '</span></div>'
          + (pct != null ? '<div style="margin-top:5px">' + bar(pct, "#378add") + '</div>' : "") + '</div>';
      }).join("");
      if ((live.outside_slots || 0) > 0) {
        var sTone = live.state === "reading" ? "#378add" : "#e0863a";
        var sBits = [];
        if (live.generated != null) sBits.push("已生成 " + live.generated);
        if (live.tok_s != null) sBits.push((+live.tok_s).toFixed(1) + " tok/s");
        if (live.elapsed_s != null) sBits.push(live.elapsed_s + "s");
        var sDot = '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:' + sTone + ';margin-right:6px"></span>';
        var sState = live.state === "reading" ? "读入提示词" : live.state === "generating" ? "生成中" : "活跃";
        html = '<div style="border:1px solid var(--st-line);border-radius:9px;padding:7px 11px;border-left:3px solid ' + sTone + '">'
          + '<div style="display:flex;justify-content:space-between;gap:10px;font-size:13px">'
          + '<span>' + sDot + '快车道 · 独占直通 · ' + sState + '</span>'
          + '<span class="muted" style="font-size:12px">' + sBits.join(" · ") + ' · 不在槽内（引擎最快路径，第二请求到来时自动让位进槽）</span></div></div>' + html;
      }
      rows.innerHTML = html;
    }).catch(function () { });
  }
  setInterval(poll, 1200);
  poll();
})();
'''

def main():
    ok = True
    s = open(HTML, encoding="utf-8").read()
    if 'id="slot-card"' in s:
        print("[index.html] 已有卡片，跳过")
    else:
        old = '      <div class="st-card" id="fan-card" hidden>'
        if s.count(old) != 1:
            print("[index.html] MISS: 找不到风扇卡锚点（请先打 patch_strata_fan.py）"); ok = False
        else:
            open(HTML, "w", encoding="utf-8", newline="").write(s.replace(old, CARD))
            print("[index.html] 已插入并发槽位卡片")
    s = open(APPJS, encoding="utf-8").read()
    if "并发槽位面板" in s:
        print("[app.js] 已打过，跳过")
    else:
        with open(APPJS, "a", encoding="utf-8", newline="") as f:
            f.write(JS)
        print("[app.js] 已追加槽位渲染脚本")
    print("\n结论:", "成功——纯前端补丁，浏览器 Ctrl+F5 即生效；单并发服务无 slots 数据，卡片自动隐藏" if ok else "未完成")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
