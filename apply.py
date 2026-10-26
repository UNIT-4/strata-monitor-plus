# -*- coding: utf-8 -*-
"""Strata Monitor Plus 一键安装/重放入口。

用法：
    python apply.py                     # 自动探测 Strata 目录
    python apply.py D:\\strata\\Strata      # 显式指定（包含 serve 子目录的那一层）
    python apply.py D:\\strata\\Strata uninstall   # 用 apply.py 生成的备份恢复原文件

首次安装时，每个将被修改的文件旁会生成一份 `.orig-plus` 原始备份（已存在则不覆盖），
卸载即把这些备份复制回去。补丁全部幂等：重复执行自动跳过已打项。
执行前请先停止 Strata 服务（后端文件被运行中的进程占用时结果不可预期）。
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATCHES = [
    "patches/patch_strata_monitor_cn.py",
    "patches/patch_strata_fan.py",
    "patches/patch_strata_slots.py",
    "patches/patch_strata_cfg_cn.py",
    "patches/patch_strata_i18n.py",
]
REL_TARGETS = [
    os.path.join("serve", "server.py"),
    os.path.join("serve", "telemetry.py"),
    os.path.join("serve", "web", "index.html"),
    os.path.join("serve", "web", "app.js"),
    os.path.join("serve", "web", "sprite.svg"),
]
MARK = ".orig-plus"


def find_root(args):
    for a in args:
        if not a.startswith("-") and a != "uninstall":
            return a.rstrip("\\/")
    env = os.environ.get("STRATA_ROOT")
    if env:
        return env.rstrip("\\/")
    for cand in (r"D:\strata-new\Strata", r"D:\strata\Strata", r"C:\strata\Strata",
                 os.path.expanduser(r"~\Strata")):
        q = os.path.expandvars(cand)
        if os.path.isdir(os.path.join(q, "serve")):
            return q
    sys.exit("找不到 Strata 安装目录。请把路径作为参数传入，或设置环境变量 STRATA_ROOT。")


def do_install(root):
    for rel in REL_TARGETS:
        t = os.path.join(root, rel)
        if os.path.isfile(t):
            bak = t + MARK
            if not os.path.exists(bak):
                shutil.copy2(t, bak)
                print("备份:", rel)
    for p in PATCHES:
        print("\n===", os.path.basename(p))
        r = subprocess.run([sys.executable, os.path.join(HERE, p), root])
        if r.returncode != 0:
            print(">> 该补丁未完全成功（上游文件可能已改版）。其余补丁继续；等待适配或提 issue。")
    print("""
完成。
- 前端改动：浏览器 Ctrl+F5 强刷即生效
- 网络卡片与风扇控制：重启 Strata 后生效
""")


def do_uninstall(root):
    n = 0
    for rel in REL_TARGETS:
        bak = os.path.join(root, rel) + MARK
        if os.path.exists(bak):
            shutil.copy2(bak, os.path.join(root, rel))
            n += 1
    print(f"已用 .orig-plus 备份恢复 {n} 个文件。建议同时删除 Strata 目录下 fan_state.json（若存在）。")


if __name__ == "__main__":
    root = find_root(sys.argv[1:])
    if not os.path.isdir(os.path.join(root, "serve")):
        sys.exit(f"路径不对（其下没有 serve 目录）: {root}")
    if len(sys.argv) > 1 and sys.argv[-1] == "uninstall":
        do_uninstall(root)
    else:
        do_install(root)
