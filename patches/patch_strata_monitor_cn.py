# -*- coding: utf-8 -*-
"""Strata Monitor 中文化 + 网络监控板块 补丁脚本
用法：python patch_strata_monitor_cn.py          （幂等：已打的补丁会自动跳过）
Strata 升级后重跑本脚本即可重新应用。
备份目录：G:\本地LLM建设\strata_backup_20261025\web原版\
"""
import re
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


WEB = os.path.join(ROOT, "serve", "web")
FILES = {
    "index": WEB + r"\index.html",
    "app":   WEB + r"\app.js",
    "sprite": WEB + r"\sprite.svg",
}
TELEMETRY = os.path.join(ROOT, "serve", "telemetry.py")

def patch(path, pairs, label):
    with open(path, "r", encoding="utf-8", newline="") as f:
        s = f.read()
    ok = skip = miss = 0
    for old, new in pairs:
        if new in s:
            skip += 1                     # 已打过（含 old 是 new 前缀的追加式替换）
            continue
        n = s.count(old)
        if n == 0:
            print(f"  [MISS] {label}: 未找到 -> {old[:70]!r}")
            miss += 1
            continue
        if n > 1:
            print(f"  [DUP {n}] {label}: 多处出现，用更长上下文重试 -> {old[:70]!r}")
            miss += 1
            continue
        s = s.replace(old, new)
        ok += 1
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(s)
    print(f"[{label}] 替换 {ok}，跳过(已是中文/已打) {skip}，未命中 {miss}")
    return miss == 0

# ---------------- index.html 静态文字 ----------------
HTML = [
    ('<span id="pill-text">Connecting&hellip;</span>', '<span id="pill-text">连接中…</span>'),
    ('title="Light / dark" aria-label="Switch between light and dark"', 'title="明暗主题" aria-label="切换明暗主题"'),
    ('aria-label="Views"', 'aria-label="视图"'),
    ('<use href="web/sprite.svg#i-chat"/></svg>Chat</button>', '<use href="web/sprite.svg#i-chat"/></svg>聊天</button>'),
    ('<use href="web/sprite.svg#i-image"/></svg>Images</button>', '<use href="web/sprite.svg#i-image"/></svg>图片</button>'),
    ('<use href="web/sprite.svg#i-activity"/></svg>Monitor</button>', '<use href="web/sprite.svg#i-activity"/></svg>监控</button>'),
    ('<use href="web/sprite.svg#i-info"/></svg>About</button>', '<use href="web/sprite.svg#i-info"/></svg>关于</button>'),
    ('<div class="chat-empty__title">Ask anything</div>', '<div class="chat-empty__title">有什么想问的？</div>'),
    ('id="chat-empty-sub">The model runs on this PC. Nothing leaves it.</div>', 'id="chat-empty-sub">模型在本机运行，数据绝不出门。</div>'),
    ('placeholder="Ask anything&hellip;" aria-label="Message"', 'placeholder="输入问题…" aria-label="消息"'),
    ('title="Attach a text file (or drop it here)" aria-label="Attach a file"', 'title="添加文本文件（也可拖入）" aria-label="添加文件"'),
    ('title="New chat" aria-label="New chat"', 'title="新对话" aria-label="新对话"'),
    ('title="Save this chat as Markdown" aria-label="Save this chat"', 'title="把对话保存为 Markdown" aria-label="保存对话"'),
    ('title="Sampling and thinking" aria-label="Sampling and thinking"', 'title="采样与思考设置" aria-label="采样与思考设置"'),
    ('<use href="web/sprite.svg#i-stop"/></svg>Stop</button>', '<use href="web/sprite.svg#i-stop"/></svg>停止</button>'),
    ('id="send-btn" aria-label="Send"', 'id="send-btn" aria-label="发送"'),
    ('id="img-title">Make an image</span>', 'id="img-title">生成图片</span>'),
    ('placeholder="Describe the image&hellip;" aria-label="Prompt"', 'placeholder="描述图片内容…" aria-label="提示词"'),
    ('<label class="st-field">Size', '<label class="st-field">尺寸'),
    ('<label class="st-field">Seed', '<label class="st-field">随机种子'),
    ('id="img-seed" type="number" min="0" placeholder="random"', 'id="img-seed" type="number" min="0" placeholder="随机"'),
    ('id="img-go">Generate</button>', 'id="img-go">生成</button>'),
    ('id="img-hint">One image at a time; a chat request waits for it (and the other way round).</span>', 'id="img-hint">一次生成一张；与聊天请求互斥排队。</span>'),
    ('<span class="card-title">Model state</span>', '<span class="card-title">模型状态</span>'),
    ('data-s="idle">Idle</span>', 'data-s="idle">空闲</span>'),
    ('data-s="reading">Reading</span>', 'data-s="reading">读入</span>'),
    ('data-s="generating">Generating</span>', 'data-s="generating">生成中</span>'),
    ('data-s="queued">Queued</span>', 'data-s="queued">排队中</span>'),
    ('data-s="error">Error</span>', 'data-s="error">出错</span>'),
    ('id="state-label">Waiting for a request</span>', 'id="state-label">等待请求</span>'),
    ('<span class="card-title">Context fill</span>', '<span class="card-title">上下文占用</span>'),
    ('<div class="bar-row"><span>Experts in VRAM</span>', '<div class="bar-row"><span>显存专家缓存</span>'),
    ('<div class="bar-row"><span>System RAM</span>', '<div class="bar-row"><span>内存占用</span>'),
    ('<div class="bar-row"><span>GPU temperature</span>', '<div class="bar-row"><span>GPU 温度</span>'),
    ('<span class="card-title">Recent requests</span>', '<span class="card-title">最近请求</span>'),
    ('id="req-all" hidden>Show all</button>', 'id="req-all" hidden>全部显示</button>'),
    ('<thead><tr><th>Time</th><th>Status</th><th class="num">Prompt</th><th class="num">Reused</th><th class="num">Output</th>',
     '<thead><tr><th>时间</th><th>状态</th><th class="num">提示词</th><th class="num">复用</th><th class="num">输出</th>'),
    ('<th class="num" title="New prompt tokens per second, excluding reused cache tokens (engine prompt time)">Prefill t/s</th>',
     '<th class="num" title="新提示词每秒预填充量（不含复用缓存，按引擎计时无复用）">预填充 t/s</th>'),
    ('<th class="num">Decode t/s</th>', '<th class="num">解码 t/s</th>'),
    ('<th class="num" title="While writing the answer: the share of the experts looked up that were already in VRAM. Experts the GPU read over PCIe (--pcie-frac) are not counted in it; their share of all routed experts is shown after it (+N% PCIe)">VRAM hit rate</th>',
     '<th class="num" title="生成回答期间：命中的专家已在显存中的比例。经 PCIe 读取的专家（--pcie-frac）不计入，其占比以 +N% PCIe 附注。">显存命中率</th>'),
    ('<th class="num">Duration</th>', '<th class="num">耗时</th>'),
    ('<tr><td colspan="9" class="muted">No requests yet</td>', '<tr><td colspan="9" class="muted">暂无请求</td>'),
    ('<span class="card-title">Conversation cache</span>', '<span class="card-title">会话缓存</span>'),
    ('<div class="bar-row"><span>Parked conversations</span>', '<div class="bar-row"><span>暂存对话</span>'),
    ('<div class="bar-row"><span>Their memory (RAM)</span>', '<div class="bar-row"><span>占用内存</span>'),
    ('<span class="card-title">MCP servers</span>', '<span class="card-title">MCP 服务器</span>'),
    ('<p class="muted small mcp-note">Their tools run on this PC with your rights, when the model decides to call them\n          (in this page\'s chat only; switch it off in Sampling).</p>',
     '<p class="muted small mcp-note">模型决定调用时，其工具将以您的权限在本机运行（仅本页聊天启用；可在采样设置中关闭）。</p>'),
    ('<span class="card-title">Model and engine</span>', '<span class="card-title">模型与引擎</span>'),
    ('<span class="card-title">This PC</span>', '<span class="card-title">本机信息</span>'),
    ('<span class="card-title">Connect your tools</span>', '<span class="card-title">接入你的应用</span>'),
    ('<p class="muted">Any OpenAI- or Anthropic-compatible client works with these addresses.</p>', '<p class="muted">任何 OpenAI / Anthropic 兼容客户端均可用这些地址接入。</p>'),
    ('<span class="card-title">Settings</span>', '<span class="card-title">设置</span>'),
    ('for="api-key">API key <output>only if the server was started with one</output>', 'for="api-key">API 密钥 <output>仅当服务端启动时配置了才需要</output>'),
    ('id="api-key" type="password" autocomplete="off" placeholder="Not needed"', 'id="api-key" type="password" autocomplete="off" placeholder="无需"' ),
    ('<div class="toggle-row"><span>Dark theme</span>', '<div class="toggle-row"><span>深色主题</span>'),
    ('aria-label="Dark theme"', 'aria-label="深色主题"'),
    ('<p class="muted small">Chats, settings and the key are kept in this browser only.', '<p class="muted small">对话、设置与密钥仅保存在本浏览器。'),
    ('>Strata on GitHub</a>', '>在 GitHub 查看 Strata</a>'),
    ('<span class="card-title">Model settings</span>', '<span class="card-title">模型设置</span>'),
    ('<p class="muted small">Kept in the model\'s run config for every client. An empty field is the default. They\n          take effect the next time the model starts (close Strata\'s window and start it again).</p>',
     '<p class="muted small">写入模型运行配置，对所有客户端生效；留空即默认值。下次模型启动时生效（关闭 Strata 窗口后重新启动）。</p>'),
    ('id="cfg-save" type="button">Save</button>', 'id="cfg-save" type="button">保存</button>'),
    ('aria-label="Sampling and thinking" aria-hidden', 'aria-label="采样与思考" aria-hidden'),
    ('<span class="card-title">Sampling</span>', '<span class="card-title">采样</span>'),
    ('id="drawer-close" aria-label="Close"', 'id="drawer-close" aria-label="关闭"'),
    ('for="s-thinking">Thinking <output', 'for="s-thinking">思考深度 <output'),
    ('role="radiogroup" aria-label="Thinking"', 'role="radiogroup" aria-label="思考深度"'),
    ('data-v="none">Off</button>', 'data-v="none">关</button>'),
    ('data-v="low">Low</button>', 'data-v="low">低</button>'),
    ('data-v="medium">Medium</button>', 'data-v="medium">中</button>'),
    ('data-v="high">High</button>', 'data-v="high">高</button>'),
    ('for="s-temp">Temperature <output', 'for="s-temp">温度 <output'),
    ('<span class="muted small">0 = always the most likely word (exact, repeatable)</span>', '<span class="muted small">0 = 总取概率最高的词（精确、可复现）</span>'),
    ('for="s-max">Max tokens <output>empty = until done</output>', 'for="s-max">最大输出 <output>留空 = 自然说完</output>'),
    ('id="s-max" type="number" min="1" step="1" placeholder="Until done"', 'id="s-max" type="number" min="1" step="1" placeholder="说完为止"'),
    ('for="s-seed">Seed <output>empty = random</output>', 'for="s-seed">随机种子 <output>留空 = 随机</output>'),
    ('id="s-seed" type="number" min="1" step="1" placeholder="Random"', 'id="s-seed" type="number" min="1" step="1" placeholder="随机"'),
    ('<span>Show thinking<br><span class="muted small">expanded while it streams</span></span>', '<span>显示思考过程<br><span class="muted small">生成时展开显示</span></span>'),
    ('aria-label="Show thinking"', 'aria-label="显示思考过程"'),
    ('<span>Use tools from MCP servers<br>', '<span>使用 MCP 工具<br>'),
    ('id="mcp-row-sub">the model may call them while it answers</span>', 'id="mcp-row-sub">模型回答时可能调用</span>'),
    ('aria-label="Use tools from MCP servers"', 'aria-label="使用 MCP 工具"'),
    ('<span>Experimental speed projection<br><span class="muted small">the\n      engine\'s control vector; off = the stock model. Switching reads the chat again once</span></span>',
     '<span>实验性速度预测 ESP<br><span class="muted small">引擎控制向量；关闭=原版模型。切换会重读一遍对话</span></span>'),
    ('aria-label="Experimental speed projection"', 'aria-label="实验性速度预测"'),
    ('<span>Use for other apps too<br><span class="muted small">omp and other API clients get\n      these settings for anything they don\'t set themselves</span></span>',
     '<span>同样作用于其他应用<br><span class="muted small">omp 等 API 客户端未显式设置时沿用这些参数</span></span>'),
    ('aria-label="Use for other apps too"', 'aria-label="同样作用于其他应用"'),
    ('id="s-reset" type="button">Reset</button>', 'id="s-reset" type="button">重置</button>'),
    ('id="s-apply" type="button">Apply</button>', 'id="s-apply" type="button">应用</button>'),
]

# ---------------- app.js 动态文字 ----------------
APP = [
    ('label: "Speed", icon: "gauge"', 'label: "速度", icon: "gauge"'),
    ('label: "GPU load", icon: "gpu"', 'label: "GPU 负载", icon: "gpu"'),
    ('label: "VRAM", icon: "layers"', 'label: "显存", icon: "layers"'),
    ('label: "GPU temp", icon: "thermometer"', 'label: "GPU 温度", icon: "thermometer"'),
    ('label: "Power", icon: "bolt"', 'label: "功耗", icon: "bolt"'),
    ('label: "PCIe", icon: "link"', 'label: "PCIe", icon: "link"'),
    ('label: "Disk read", icon: "disk", unit: "MB/s", series: "disk_read_mb", tone: "info"},',
     'label: "磁盘读取", icon: "disk", unit: "MB/s", series: "disk_read_mb", tone: "info"},\n  {key: "netup", label: "网络上行", icon: "upload", unit: "MB/s", series: "net_up_mb", tone: "info"},\n  {key: "netdown", label: "网络下行", icon: "download", unit: "MB/s", series: "net_down_mb", tone: "info"},'),
    ('id="ms-speed">Decode</span>', 'id="ms-speed">解码</span>'),
    ('id="ms-prefill">Prefill</span>', 'id="ms-prefill">预填充</span>'),
    ('`Reading prompt · ${pct}%` : "Reading prompt"', '`读入提示词 · ${pct}%` : "读入提示词"'),
    ('`Generating · ${fmt(live.tok_s, 1)} tok/s`', '`生成中 · ${fmt(live.tok_s, 1)} tok/s`'),
    ('setPill("idle", "Idle")', 'setPill("idle", "空闲")'),
    ('setPill("queued", `${live.queued} queued`)', 'setPill("queued", `${live.queued} 个排队`)'),
    ('setPill("error", "API key needed")', 'setPill("error", "需要 API 密钥")'),
    ('toast("warn", "API key needed", "This server needs a key: add it under About > Settings.", 6000)', 'toast("warn", "需要 API 密钥", "该服务器要求密钥：请到 关于 > 设置 中填写。", 6000)'),
    ('let label = "Waiting for a request"', 'let label = "等待请求"'),
    ('label = "Reading prompt";', 'label = "读入提示词";'),
    (': "Generating";', ': "生成中";'),
    ('live.state === "generating" ? "Decode now" : last ? "Decode last request" : "Decode")', 'live.state === "generating" ? "当前解码" : last ? "上次解码" : "解码")'),
    ('live.state === "reading" ? "Prefill now" : live.state === "generating" ? "Prefill this request" : last ? "Prefill last request" : "Prefill")', 'live.state === "reading" ? "当前预填充" : live.state === "generating" ? "本次预填充" : last ? "上次预填充" : "预填充")'),
    ('eng.expert_slots ? `${fmt(eng.expert_slots)} experts cached`', 'eng.expert_slots ? `${fmt(eng.expert_slots)} 专家已缓存`'),
    ('hw.gpu_power_limit ? `of ${fmt(hw.gpu_power_limit)} W limit` : ""', 'hw.gpu_power_limit ? `上限 ${fmt(hw.gpu_power_limit)} W` : ""'),
    ('`to GPU ${fmt(hw.gpu_pcie_rx_mb, hw.gpu_pcie_rx_mb < 10 ? 1 : 0)} MB/s`', '`传向GPU ${fmt(hw.gpu_pcie_rx_mb, hw.gpu_pcie_rx_mb < 10 ? 1 : 0)} MB/s`'),
    ('` · idle Gen${hw.gpu_pcie_gen}`', '` · 闲置 Gen${hw.gpu_pcie_gen}`'),
    ('st.threads ? `${st.cores ? `${st.cores} cores · ` : ""}${st.threads} threads` : ""', 'st.threads ? `${st.cores ? `${st.cores} 物理核 · ` : ""}${st.threads} 线程` : ""'),
    ('st.psutil ? "" : "needs psutil (setup installs it)"', 'st.psutil ? "" : "需要 psutil（安装器已自带）"'),
    ('`write ${fmt(hw.disk_write_mb, 1)} MB/s`', '`写入 ${fmt(hw.disk_write_mb, 1)} MB/s`'),
    ('class="muted">No requests yet</td>', 'class="muted">暂无请求</td>'),
    ('stop: ["", "Done"], length: ["", "Max tokens"], cancel: ["st-badge--queued", "Stopped"],', 'stop: ["", "完成"], length: ["", "达上限"], cancel: ["st-badge--queued", "已停止"],'),
    ('disconnect: ["st-badge--queued", "Closed"], error: ["st-badge--error", "Error"]', 'disconnect: ["st-badge--queued", "已断开"], error: ["st-badge--error", "出错"]'),
    ('return s < 60 ? "just now" : s < 3600 ? `${fmt(s / 60)} min ago` : `${fmt(s / 3600, 1)} h ago`;', 'return s < 60 ? "刚刚" : s < 3600 ? `${fmt(s / 60)} 分钟前` : `${fmt(s / 3600, 1)} 小时前`;'),
    # —— 网络卡片渲染逻辑（追加在磁盘卡片 spark 之后）——
    ('  spark("sp-disk", h.disk_read_mb);',
     '''  spark("sp-disk", h.disk_read_mb);
  const netFmt = (v) => v >= 1000 ? fmt(v / 1024, 2) : fmt(v, v < 10 ? 1 : 0);
  const netUnit = (v) => v >= 1000 ? "GB/s" : "MB/s";
  if (hw.net_up_mb == null) {
    setMetric("netup", null, "", st.psutil ? "等待首个采样" : "需要 psutil");
    setMetric("netdown", null, "", "");
  } else {
    setMetric("netup", netFmt(hw.net_up_mb), netUnit(hw.net_up_mb), hw.conn_established == null ? "" : `活动连接 ${fmt(hw.conn_established)}`);
    setMetric("netdown", netFmt(hw.net_down_mb), netUnit(hw.net_down_mb), "");
  }
  spark("sp-netup", h.net_up_mb);
  spark("sp-netdown", h.net_down_mb);'''),
]

# ---------------- sprite.svg：新增 upload 图标（download 垂直镜像） ----------------
SPRITE = [
    ('<symbol id="i-download"', '<symbol id="i-upload" viewBox="0 0 24 24"><path d="M12 19V5m0 0l-6 6m6-6l6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></symbol>\n<symbol id="i-download"'),
]

# ---------------- telemetry.py：网络采样 ----------------
TELE = [
    ('        self._disk_prev = None', '        self._disk_prev = None\n        self._net_prev = None'),
    ('        s["disk_read_mb"], s["disk_write_mb"] = self._disk()',
     '        s["disk_read_mb"], s["disk_write_mb"] = self._disk()\n        s["net_up_mb"], s["net_down_mb"] = self._net()'),
    # _net 方法追加在 _disk 之后（以 sample 定义行为锚点）
    ('    def sample(self):',
     '''    def _net(self):
        if not self.ps:
            return None, None
        try:
            c = self.ps.net_io_counters()
        except (OSError, RuntimeError):
            return None, None
        if c is None:
            return None, None
        t = time.time()
        prev, self._net_prev = self._net_prev, (t, c.bytes_sent, c.bytes_recv)
        if prev is None or t <= prev[0]:
            return None, None
        dt = t - prev[0]
        return (c.bytes_sent - prev[1]) / dt / 2**20, (c.bytes_recv - prev[2]) / dt / 2**20

    def sample(self):'''),
    ('"disk_read_mb", "tok_s", "prefill_tok_s_mean"):', '"disk_read_mb", "net_up_mb", "net_down_mb", "tok_s", "prefill_tok_s_mean"):'),
]

def main():
    # telemetry.py 已打过（存在 _net 方法）则整体跳过，防重复插入
    if "_net_prev" in open(TELEMETRY, encoding="utf-8").read():
        print("[telemetry.py] 已打过，跳过")
        r4 = True
    else:
        r4 = patch(TELEMETRY, TELE, "telemetry.py")
    r1 = patch(FILES["index"], HTML, "index.html")
    r2 = patch(FILES["app"], APP, "app.js")
    r3 = patch(FILES["sprite"], SPRITE, "sprite.svg")
    print("\n结论：", "全部成功（前端刷新即生效；telemetry 改动需重启 strata 后网络卡片出数）"
          if all([r1, r2, r3, r4]) else "存在未命中项，见上方 MISS 行")
    return 0 if all([r1, r2, r3, r4]) else 1

if __name__ == "__main__":
    sys.exit(main())
