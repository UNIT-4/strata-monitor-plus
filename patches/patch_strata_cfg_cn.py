# -*- coding: utf-8 -*-
"""Strata 「模型设置」表单中文化 补丁（纯前端：key→中文映射 + 下拉选项显示文字翻译）
用法：python patch_strata_cfg_cn.py   （幂等；升级后重跑）
说明：字段 help 文案来自后端 runconfig.py；本补丁在前端渲染处按字段 key 替换中文，
     未知新字段自动回退英文原文，不会报错。刷新浏览器即生效。"""
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


APPJS = os.path.join(ROOT, "serve", "web", "app.js")

MAP_JS = '''

// ================= 模型设置字段中文化（本地补丁） =================
var CFG_CN = {
  "sampling.temperature": "未指定温度的请求的默认温度（0 = 贪婪；留空按模型卡默认：思考模式 1.0、非思考 0.7）",
  "sampling.top_p": "未指定 top_p 的请求的默认 top_p（核采样）",
  "sampling.top_k": "未指定 top_k 的请求的默认 top_k（1-64）",
  "sampling.min_p": "未指定 min_p 的请求的默认 min_p",
  "reasoning_budget_tokens": "每个请求思考令牌的上限（0 或留空 = 不限制）",
  "fit_max_tokens": "max_tokens 超出上下文时自动裁剪（默认开启）；关闭后像 llama.cpp 一样直接报 400",
  "anthropic_thinking": "Anthropic 请求未要求思考时：按模型默认思考（model）或不思考（on_request）",
  "effort_position": "非默认推理强度的注入位置：开头（默认）或结尾（切换强度时不失效缓存）",
  "aliases": "服务器额外接受并列出的模型别名（用逗号分隔）",
  "idle_unload_s": "空闲多少秒后卸载模型释放显存（0 或留空 = 从不卸载）",
  "mtp": "MTP 草稿层：关闭后引擎不带它启动（省约 1GB 显存，但生成变慢）；留空或开启 = 按安装现状",
  "lazy_load": "启动时先不加载模型；收到第一个请求再加载（仅文本）",
  "engine_silence_s": "引擎静默超过此时长就结束该请求（默认 300 秒，0 = 一直等）",
  "api_monitor": "在内存中保留最近 100 个请求的输入与输出，供监控页展示",
  "open_browser": "模型就绪后自动在浏览器打开聊天页",
  "vram_reserve_mib": "引擎为其他程序预留的显存（MiB），从专家缓存中扣除（引擎默认 700）"
};
var CFG_CN_ENUM = { "model": "模型默认", "on_request": "不思考", "start": "开头", "end": "结尾" };
'''

PAIRS = [
    ('      const opts = k.kind === "bool" ? [["true", "on"], ["false", "off"]] : k.choices.map((x) => [x, x]);',
     '      const opts = k.kind === "bool" ? [["true", "开"], ["false", "关"]] : k.choices.map((x) => [x, (typeof CFG_CN_ENUM !== "undefined" && CFG_CN_ENUM[x]) || x]);'),
    ('const opts = k.kind === "bool"', 'const opts = k.kind === "bool"'),
    ('<option value=""${cur === "" ? " selected" : ""}>default</option>',
     '<option value=""${cur === "" ? " selected" : ""}>默认</option>'),
    ('value="${esc(text)}" placeholder="default"', 'value="${esc(text)}" placeholder="默认"'),
    ('  cfgKeys = c.keys || [];',
     '  cfgKeys = (c.keys || []).map(function (k) { return (typeof CFG_CN !== "undefined" && CFG_CN[k.key]) ? Object.assign({}, k, {help: CFG_CN[k.key]}) : k; });'),
]

def main():
    s = open(APPJS, encoding="utf-8").read()
    if "模型设置字段中文化" in s:
        print("已打过，跳过"); return 0
    ok = True
    for old, new in PAIRS[0:1] + PAIRS[2:]:          # 跳过第2条自检占位
        n = s.count(old)
        if n != 1:
            print(f"[MISS x{n}] {old[:60]!r}"); ok = False; continue
        s = s.replace(old, new)
    s = s + MAP_JS
    if ok:
        open(APPJS, "w", encoding="utf-8", newline="").write(s)
        print("已打补丁：模型设置表单中文化（16 字段 + 下拉选项 + default→默认）")
    print("结论:", "成功——浏览器 Ctrl/F5 刷新即生效" if ok else "存在未命中，未写入")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
