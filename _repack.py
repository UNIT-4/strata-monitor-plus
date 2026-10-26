# -*- coding: utf-8 -*-
"""把四个补丁脚本参数化为可发布版本（路径自适应）。"""
import re
import os

SRC = r"G:\本地LLM建设\strata_test"
DST = r"G:\本地LLM建设\strata-monitor-plus\patches"
FILES = ["patch_strata_monitor_cn.py", "patch_strata_fan.py",
         "patch_strata_slots.py", "patch_strata_cfg_cn.py", "patch_strata_i18n.py"]

ROOT_BLOCK = r'''
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
'''

os.makedirs(DST, exist_ok=True)
for f in FILES:
    s = open(os.path.join(SRC, f), encoding="utf-8").read()
    # 绝对路径常量 -> os.path.join(ROOT, ...)
    pat = re.compile(r'r"D:\\strata-new\\Strata\\([A-Za-z0-9_\\.\\-]+)"')
    def repl(m):
        parts = ", ".join('"%s"' % p for p in m.group(1).split("\\"))
        return "os.path.join(ROOT, %s)" % parts
    s, n = pat.subn(repl, s)
    if re.search(r"^import os$", s, re.M) is None:
        s = s.replace("import sys", "import os\nimport sys", 1)
    # 2) 在文件头部第一个模块级 import sys 之后注入 ROOT 自适应块
    #    （绝不能用"最后一个 import"——补丁源码的三引号字符串里也有顶格 import 行）
    m = re.search(r"^import sys$", s, re.M)
    assert m, f"{f}: 找不到模块级 import sys 注入点"
    s = s[: m.end()] + "\n" + ROOT_BLOCK + s[m.end():]
    out = s
    left = len(re.findall(r"strata-new", out.replace(ROOT_BLOCK, "")))
    open(os.path.join(DST, f), "w", encoding="utf-8").write(out)
    print("%s: 参数化 %d 处 | 残留绝对路径 %d" % (f, n, left))
