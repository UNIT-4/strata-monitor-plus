# -*- coding: utf-8 -*-
"""Strata Monitor Plus 多语言补丁：向 index.html 注入 i18n 引擎（语言下拉 + DOM 实时翻译）。
用法：python patch_strata_i18n.py [Strata根目录]   （幂等）
默认语言=中文（与编译期中文补丁一致）；选择 English / Español / Português 后运行时翻译全部界面文本。
"""
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

import os

def _find_root():
    env = os.environ.get("STRATA_ROOT")
    if env: return env.rstrip("\\/")
    for p in (r"D:\strata-026\Strata", r"D:\strata-new\Strata", r"D:\strata\Strata", r"C:\strata\Strata", os.path.expanduser(r"~\Strata")):
        if os.path.isdir(os.path.join(p, "serve")): return p
    raise SystemExit("找不到 Strata 目录，请传参")

ROOT = sys.argv[1] if len(sys.argv) > 1 else _find_root()
WEB = os.path.join(ROOT, "serve", "web")
HTML = os.path.join(WEB, "index.html")
I18N_JS = os.path.join(WEB, "i18n.js")

# ---------------- 词条：中文 -> 其他语言（含上游 86 条 + 自制卡片全部文案）----------------
LANGS = {
"zh": {},
"en": {
"连接中…": "Connecting…",
"有什么想问的？": "Ask anything",
"模型在本机运行，数据绝不出门。": "The model runs on this PC. Nothing leaves it.",
"在本机运行，数据绝不出门。": "runs on this PC. Nothing leaves it.",
"输入问题…": "Ask anything…",
"消息": "Message",
"添加文本文件（也可拖入）": "Attach a text file (or drop it here)",
"添加文件": "Attach a file",
"新对话": "New chat",
"把对话保存为 Markdown": "Save this chat as Markdown",
"保存对话": "Save this chat",
"采样与思考设置": "Sampling and thinking",
"停止": "Stop",
"发送": "Send",
"生成图片": "Make an image",
"描述图片内容…": "Describe the image…",
"提示词": "Prompt",
"尺寸": "Size",
"随机种子": "Seed",
"随机": "Random",
"说完为止": "Until done",
"一次生成一张；与聊天请求互斥排队。": "One image at a time; a chat request waits for it (and the other way round).",
"模型状态": "Model state",
"空闲": "Idle",
"读入": "Reading",
"生成中": "Generating",
"排队中": "Queued",
"出错": "Error",
"等待请求": "Waiting for a request",
"上下文占用": "Context fill",
"显存专家缓存": "Experts in VRAM",
"内存占用": "System RAM",
"GPU 温度": "GPU temperature",
"最近请求": "Recent requests",
"全部显示": "Show all",
"时间": "Time",
"状态": "Status",
"提示词 ": "Prompt",
"复用": "Reused",
"输出": "Output",
"预填充 t/s": "Prefill t/s",
"解码 t/s": "Decode t/s",
"显存命中率": "VRAM hit rate",
"耗时": "Duration",
"暂无请求": "No requests yet",
"会话缓存": "Conversation cache",
"暂存对话": "Parked conversations",
"占用内存": "Their memory (RAM)",
"MCP 服务器": "MCP servers",
"模型决定调用时，其工具将以您的权限在本机运行（仅本页聊天启用；可在采样设置中关闭）。": "Their tools run on this PC with your rights, when the model decides to call them (in this page's chat only; switch it off in Sampling).",
"模型与引擎": "Model and engine",
"本机信息": "This PC",
"接入你的应用": "Connect your tools",
"任何 OpenAI / Anthropic 兼容客户端均可用这些地址接入。": "Any OpenAI- or Anthropic-compatible client works with these addresses.",
"设置": "Settings",
"API 密钥": "API key",
"仅当服务端启动时配置了才需要": "only if the server was started with one",
"无需": "Not needed",
"深色主题": "Dark theme",
"对话、设置与密钥仅保存在本浏览器。": "Chats, settings and the key are kept in this browser only.",
"在 GitHub 查看 Strata": "Strata on GitHub",
"模型设置": "Model settings",
"写入模型运行配置，对所有客户端生效；留空即默认值。下次模型启动时生效（关闭 Strata 窗口后重新启动）。": "Kept in the model's run config for every client. An empty field is the default. They take effect the next time the model starts.",
"保存": "Save",
"采样": "Sampling",
"关闭": "Close",
"思考深度": "Thinking",
"关": "Off",
"低": "Low",
"中": "Medium",
"高": "High",
"温度": "Temp",
"0 = 总取概率最高的词（精确、可复现）": "0 = always the most likely word (exact, repeatable)",
"最大输出": "Max tokens",
"留空 = 自然说完": "empty = until done",
"留空 = 随机": "empty = random",
"显示思考过程": "Show thinking",
"生成时展开显示": "expanded while it streams",
"使用 MCP 工具": "Use tools from MCP servers",
"模型回答时可能调用": "the model may call them while it answers",
"实验性速度预测 ESP": "Experimental speed projection",
"引擎控制向量；关闭=原版模型。切换会重读一遍对话": "the engine's control vector; off = the stock model. Switching reads the chat again once",
"同样作用于其他应用": "Use for other apps too",
"omp 等 API 客户端未显式设置时沿用这些参数": "omp and other API clients get these settings for anything they don't set themselves",
"重置": "Reset",
"应用": "Apply",
"聊天": "Chat",
"图片": "Images",
"监控": "Monitor",
"关于": "About",
"速度": "Speed",
"GPU 负载": "GPU load",
"显存": "VRAM",
"功耗": "Power",
"磁盘读取": "Disk read",
"网络上行": "Network up",
"网络下行": "Network down",
"解码": "Decode",
"预填充": "Prefill",
"读入提示词": "Reading prompt",
"个排队": "queued",
"需要 API 密钥": "API key needed",
"该服务器要求密钥：请到 关于 > 设置 中填写。": "This server needs a key: add it under About > Settings.",
"当前解码": "Decode now",
"上次解码": "Decode last request",
"本次预填充": "Prefill this request",
"当前预填充": "Prefill now",
"上次预填充": "Prefill last request",
"专家已缓存": "experts cached",
"上限": "limit",
"传向GPU": "to GPU",
"闲置": "idle",
"物理核": "cores",
"线程": "threads",
"需要 psutil（安装器已自带）": "needs psutil (setup installs it)",
"写入": "write",
"完成": "Done",
"达上限": "Max tokens",
"已停止": "Stopped",
"已断开": "Closed",
"刚刚": "just now",
"分钟前": "min ago",
"小时前": "h ago",
"活动连接": "connections",
"等待首个采样": "waiting for first sample",
"生成中…": "Writing…",
"复制代码": "Copy code",
"复制回答": "Copy the answer",
"已复制到剪贴板": "Copied to clipboard",
"API 密钥已保存": "API key saved",
"未保存": "Not saved",
"暂无可保存内容": "Nothing to save yet",
"采样设置已保存": "Sampling saved",
"无法连接服务器": "Server not reachable",
"请求失败": "request failed",
"引擎返回错误": "the engine reported an error",
"尚未连接模型（见监控页）": "no server is connected yet (see the Monitor)",
"不可用": "not available",
"不可读（NVML）": "not readable (NVML)",
"源码构建": "built from source",
"文件过大": "File too large",
"不是文本文件": "Not a text file",
"图片过大": "Picture too large",
"图片输入已关闭": "Pictures are off",
"粘贴的图片": "pasted image",
"收起": "Show fewer",
"立即回答": "answers right away",
"暂存 / 恢复": "Parked / restored",
"自启动累计复用": "Reused since start",
"最近一次换入": "Last switch",
"已暂存": "Parked",
"已恢复": "Restored",
"个请求复用了部分提示词": "requests reused part of their prompt",
"提示词 token 已复用": "prompt tokens reused",
"次清除": "evicted",
"（占全部提示词": "(of all prompt tokens)",
"）": ")",
"继续已暂存会话的请求会直接换回其状态，无需重新预填充；槽位或内存不足时最先暂退最旧的会话。": "A request that continues a parked conversation gets its state back instead of reading it again; the oldest goes when the slots or the memory are full.",
"引擎会保留最近一轮会话状态，追问只需读入新增部分。如需同时保留多个会话（多智能体轮转），在运行配置 args 中加入 \"--conversation-cache-mib\", \"8192\"（见 docs/DETAILS.md）。": "The engine keeps the last conversation's state, so a follow-up reads only what is new. To keep several conversations, add \"--conversation-cache-mib\", \"8192\" to the run config's args.",
"显卡风扇": "GPU fan",
"系统默认": "System default",
"中等": "Medium",
"激进": "Aggressive",
"自定义": "Custom",
"当前转速": "now",
"模式": "mode",
"跟随驱动原生调教。中等/激进为温控曲线自动调速；自定义用滑块钉死转速。": "Follow the driver. Medium/Aggressive follow a thermal curve; Custom pins the speed with the slider.",
"度强制满速保护；退出时自动交还驱动。": " forces 100%; the driver is handed back on exit.",
"调速中：目标": "Ramping: target",
"保护线": "guard at",
"（重启 Strata 后需后端补丁生效，若显示 404 请重启服务）": "(backend patch active after restart; 404 = restart the service)",
"失败：": "failed: ",
"并发槽位": "Parallel slots",
"槽活跃": "slots busy",
"排队": "queued",
"外部": "outside",
"在跑": "running",
"双并发模式实时状态：空闲槽保留的 token 可被同会话下一轮直接复用；「外部」为独占快车道或排队准入中的请求。": "Live dual-slot state: idle slots keep tokens for the same conversation's next turn; \"outside\" requests use the exclusive fast lane or wait for admission.",
"槽": "Slot",
"空置": "empty",
"已读": "read",
"已生成": "generated",
"下一轮可续": "kept for next turn",
"快车道 · 独占直通": "Fast lane · exclusive",
"无外部请求 · 待命": "no outside request · standby",
"外部请求到来时走此独占直通": "outside requests take this exclusive lane",
"不在槽内（引擎最快路径，第二请求到来时自动让位进槽）": "not in a slot (engine's fastest path; yields to a slot when a second request arrives)",
"活跃": "active",
"语言": "Language",
"视图": "Views",
"明暗主题": "Light / dark",
"切换明暗主题": "Switch between light and dark",
"上一次请求": "Last request"
},
"es": {
"连接中…": "Conectando…",
"有什么想问的？": "Pregunta lo que quieras",
"模型在本机运行，数据绝不出门。": "El modelo se ejecuta en este PC. Los datos nunca salen.",
"新对话": "Nueva conversación",
"停止": "Detener",
"发送": "Enviar",
"生成图片": "Generar imagen",
"尺寸": "Tamaño",
"随机种子": "Semilla",
"随机": "Aleatorio",
"说完为止": "Hasta terminar",
"模型状态": "Estado del modelo",
"空闲": "Inactivo",
"读入": "Leyendo",
"生成中": "Generando",
"排队中": "En cola",
"出错": "Error",
"等待请求": "Esperando una petición",
"上下文占用": "Uso de contexto",
"显存专家缓存": "Expertos en VRAM",
"内存占用": "RAM del sistema",
"GPU 温度": "Temp. de GPU",
"最近请求": "Peticiones recientes",
"全部显示": "Mostrar todo",
"时间": "Hora",
"状态": "Estado",
"复用": "Reutilizado",
"输出": "Salida",
"显存命中率": "Aciertos en VRAM",
"耗时": "Duración",
"暂无请求": "Sin peticiones aún",
"会话缓存": "Caché de conversaciones",
"暂存对话": "Conversaciones guardadas",
"占用内存": "Memoria usada",
"MCP 服务器": "Servidores MCP",
"模型与引擎": "Modelo y motor",
"本机信息": "Este PC",
"接入你的应用": "Conecta tus apps",
"设置": "Ajustes",
"API 密钥": "Clave API",
"无需": "No requerida",
"深色主题": "Tema oscuro",
"在 GitHub 查看 Strata": "Strata en GitHub",
"模型设置": "Ajustes del modelo",
"保存": "Guardar",
"采样": "Muestreo",
"关闭": "Cerrar",
"思考深度": "Profundidad de razonamiento",
"关": "Apagado",
"低": "Bajo",
"中": "Medio",
"高": "Alto",
"温度": "Temperatura",
"最大输出": "Tok. máx",
"显示思考过程": "Mostrar razonamiento",
"重置": "Restablecer",
"应用": "Aplicar",
"聊天": "Chat",
"图片": "Imágenes",
"监控": "Monitor",
"关于": "Acerca de",
"速度": "Velocidad",
"GPU 负载": "Carga GPU",
"显存": "VRAM",
"功耗": "Consumo",
"磁盘读取": "Lectura disco",
"网络上行": "Subida red",
"网络下行": "Bajada red",
"解码": "Decodificación",
"预填充": "Prefill",
"读入提示词": "Leyendo prompt",
"个排队": "en cola",
"需要 API 密钥": "Se requiere clave API",
"专家已缓存": "expertos en caché",
"写入": "escritura",
"完成": "Hecho",
"达上限": "Límite alcanzado",
"已停止": "Detenido",
"已断开": "Cerrado",
"刚刚": "ahora mismo",
"分钟前": "min atrás",
"小时前": "h atrás",
"活动连接": "conexiones",
"等待首个采样": "esperando muestra",
"复制代码": "Copiar código",
"复制回答": "Copiar respuesta",
"已复制到剪贴板": "Copiado al portapapeles",
"无法连接服务器": "Servidor inaccesible",
"请求失败": "La petición falló",
"不可用": "no disponible",
"收起": "Mostrar menos",
"立即回答": "responde enseguida",
"暂存 / 恢复": "Guardadas / restauradas",
"最近一次换入": "Último cambio",
"已暂存": "Guardada",
"已恢复": "Restaurada",
"显卡风扇": "Ventilador GPU",
"系统默认": "Predet. del sistema",
"中等": "Medio",
"激进": "Agresivo",
"自定义": "Personalizado",
"当前转速": "actual",
"模式": "modo",
"失败：": "error: ",
"并发槽位": "Ranuras paralelas",
"槽活跃": "ranuras activas",
"排队": "en cola",
"外部": "externa",
"在跑": "ejecutando",
"槽": "Ranura",
"空置": "vacía",
"已读": "leído",
"已生成": "generado",
"快车道 · 独占直通": "Carril rápido · exclusivo",
"无外部请求 · 待命": "sin peticiones externas · en espera",
"外部请求到来时走此独占直通": "las peticiones externas usan este carril",
"活跃": "activo",
"语言": "Idioma",
"文件过大": "Archivo demasiado grande",
"不是文本文件": "No es un archivo de texto",
"图片过大": "Imagen demasiado grande",
"图片输入已关闭": "Imágenes desactivadas",
"粘贴的图片": "imagen pegada",
"解码中": "Generando",
"跟随驱动原生调教。中等/激进为温控曲线自动调速；自定义用滑块钉死转速。": "Sigue al controlador. Medio/Agresivo usan una curva térmica; Personalizado fija la velocidad con el deslizador.",
"度强制满速保护；退出时自动交还驱动。": " fuerza el 100%; el controlador se devuelve al salir.",
"调速中：目标": "Ajustando: objetivo",
"保护线": "protección a",
"上一次请求": "Última petición",
"提示词": "Prompt",
"requests": "peticiones",
"prompt tokens read at": "tokens de prompt leídos a",
"reused": "reutilizados",
"written at": "escritos a",
"Since": "Desde",
"Show all": "Mostrar todo",
"Show fewer": "Mostrar menos"
},
"pt": {
"连接中…": "Conectando…",
"有什么想问的？": "Pergunte o que quiser",
"模型在本机运行，数据绝不出门。": "O modelo roda neste PC. Os dados nunca saem dele.",
"新对话": "Nova conversa",
"停止": "Parar",
"发送": "Enviar",
"生成图片": "Gerar imagem",
"尺寸": "Tamanho",
"随机种子": "Semente",
"随机": "Aleatório",
"说完为止": "Até terminar",
"模型状态": "Estado do modelo",
"空闲": "Ocioso",
"读入": "Lendo",
"生成中": "Gerando",
"排队中": "Na fila",
"出错": "Erro",
"等待请求": "Aguardando requisições",
"上下文占用": "Uso de contexto",
"显存专家缓存": "Especialistas na VRAM",
"内存占用": "RAM do sistema",
"GPU 温度": "Temp. da GPU",
"最近请求": "Requisições recentes",
"上一次请求": "Última requisição",
"全部显示": "Mostrar tudo",
"时间": "Hora",
"状态": "Estado",
"复用": "Reutilizado",
"输出": "Saída",
"显存命中率": "Acertos na VRAM",
"耗时": "Duração",
"暂无请求": "Nenhuma requisição ainda",
"会话缓存": "Cache de conversas",
"暂存对话": "Conversas arquivadas",
"占用内存": "Memória usada",
"MCP 服务器": "Servidores MCP",
"模型与引擎": "Modelo e mecanismo",
"本机信息": "Este PC",
"接入你的应用": "Conecte seus apps",
"设置": "Configurações",
"API 密钥": "Chave API",
"无需": "Não necessária",
"深色主题": "Tema escuro",
"在 GitHub 查看 Strata": "Strata no GitHub",
"模型设置": "Config. do modelo",
"保存": "Salvar",
"采样": "Amostragem",
"关闭": "Fechar",
"思考深度": "Profundidade de raciocínio",
"关": "Desligado",
"低": "Baixo",
"中": "Médio",
"高": "Alto",
"温度": "Temperatura",
"最大输出": "Tok. máx",
"显示思考过程": "Mostrar raciocínio",
"重置": "Redefinir",
"应用": "Aplicar",
"聊天": "Chat",
"图片": "Imagens",
"监控": "Monitor",
"关于": "Sobre",
"速度": "Velocidade",
"GPU 负载": "Carga da GPU",
"显存": "VRAM",
"功耗": "Potência",
"磁盘读取": "Leitura de disco",
"网络上行": "Envio de rede",
"网络下行": "Recepção de rede",
"解码": "Decodificação",
"预填充": "Prefill",
"读入提示词": "Lendo prompt",
"个排队": "na fila",
"需要 API 密钥": "Chave API necessária",
"专家已缓存": "especialistas em cache",
"写入": "gravação",
"完成": "Concluído",
"达上限": "Limite atingido",
"已停止": "Parado",
"已断开": "Fechado",
"刚刚": "agora mesmo",
"分钟前": "min atrás",
"小时前": "h atrás",
"活动连接": "conexões",
"等待首个采样": "aguardando amostra",
"复制代码": "Copiar código",
"复制回答": "Copiar resposta",
"已复制到剪贴板": "Copiado para a área de transferência",
"无法连接服务器": "Servidor inacessível",
"请求失败": "A requisição falhou",
"不可用": "indisponível",
"收起": "Mostrar menos",
"立即回答": "responde já",
"暂存 / 恢复": "Arquivadas / restauradas",
"最近一次换入": "Última troca",
"已暂存": "Arquivada",
"已恢复": "Restaurada",
"显卡风扇": "Ventoinha da GPU",
"系统默认": "Padrão do sistema",
"中等": "Médio",
"激进": "Agressivo",
"自定义": "Personalizado",
"当前转速": "atual",
"模式": "modo",
"失败：": "falha: ",
"并发槽位": "Slots paralelos",
"槽活跃": "slots ativos",
"排队": "na fila",
"外部": "externa",
"在跑": "rodando",
"槽": "Slot",
"空置": "vazio",
"已读": "lido",
"已生成": "gerado",
"快车道 · 独占直通": "Faixa rápida · exclusiva",
"无外部请求 · 待命": "sem requisição externa · em espera",
"外部请求到来时走此独占直通": "requisições externas usam esta faixa",
"活跃": "ativo",
"语言": "Idioma",
"文件过大": "Arquivo grande demais",
"不是文本文件": "Não é arquivo de texto",
"图片过大": "Imagem grande demais",
"图片输入已关闭": "Imagens desativadas",
"粘贴的图片": "imagem colada",
"跟随驱动原生调教。中等/激进为温控曲线自动调速；自定义用滑块钉死转速。": "Segue o driver. Médio/Agressivo seguem curva térmica; Personalizado fixa a velocidade no controle.",
"度强制满速保护；退出时自动交还驱动。": " força 100%; o driver é devolvido ao sair.",
"调速中：目标": "Ajustando: alvo",
"保护线": "proteção em",
"提示词": "Prompt",
"requests": "requisições",
"prompt tokens read at": "tokens de prompt lidos a",
"reused": "reutilizados",
"written at": "gravados a",
"Since": "Desde",
"Show all": "Mostrar tudo",
"Show fewer": "Mostrar menos"
}
}
JS_TEMPLATE = """
// ==== Strata Monitor Plus i18n (injected, idempotent) ====
(function () {
  if (window.__smpI18n) return; window.__smpI18n = true;
  var LANGS = %LANGS%;
  var LABELS = { zh: "中文", en: "English", es: "Español", pt: "Português" };
  var attrs = ["title", "aria-label", "placeholder"];
  function lang() { var m = location.search.match(/[?&]lang=(\\w+)/); if (m && LABELS[m[1]]) return m[1]; return localStorage.getItem("strata.lang") || "zh"; }
  function dict() { return LANGS[lang()] || null; }
  var keys = null, byLen = null;
  function prep(d) { if (byLen && prep.l === lang()) return; prep.l = lang(); byLen = Object.keys(d).sort(function (a, b) { return b.length - a.length; }); }
  function tr(s, d) {
    for (var i = 0; i < byLen.length; i++) { var k = byLen[i]; var p = s.indexOf(k); if (p >= 0) { s = s.slice(0, p) + d[k] + s.slice(p + k.length); } }
    return s;
  }
  function apply() {
    var d = dict();
    var root = document.body; if (!root) return;
    if (!d) { restore(d0); return; }        // zh: 恢复原始中文快照
    if (!d0) snap();
    prep(d);
    walk(root, d);
  }
  var d0 = null;
  function snap() { d0 = {}; var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); var n, i = 0; while ((n = w.nextNode())) { n.__i = i; d0[i++] = n.nodeValue; } var a = document.body.querySelectorAll("[title],[aria-label],[placeholder]"); for (var k = 0; k < a.length; k++) { a[k].__i = "a" + k; d0["a" + k] = { t: a[k].title, l: a[k].getAttribute("aria-label"), p: a[k].getAttribute("placeholder") }; } }
  function restore(orig) { if (!orig) return; var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); var n; while ((n = w.nextNode())) { if (n.__i in orig && n.nodeValue !== orig[n.__i]) { var t = orig[n.__i]; if (t.indexOf("…") >= 0 || /[\\u4e00-\\u9fff]/.test(t) || /^(Ask|Pregunta|Pergunte|Attach|Describe)/.test(t)) {} n.nodeValue = t; } } var a = document.body.querySelectorAll("[title],[aria-label],[placeholder]"); for (var k = 0; k < a.length; k++) { var o = orig["a" + a[k].__i]; if (!o) continue; if (a[k].title !== o.t) a[k].title = o.t; if (a[k].getAttribute("aria-label") !== o.l) { if (o.l === null) a[k].removeAttribute("aria-label"); else a[k].setAttribute("aria-label", o.l); } if (a[k].getAttribute("placeholder") !== o.p) { if (o.p === null) a[k].removeAttribute("placeholder"); else a[k].setAttribute("placeholder", o.p); } } }
  function walk(root, d) {
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    var n; while ((n = w.nextNode())) {
      var p = n.parentElement; if (!p || p.closest("script,style")) continue;
      var v = n.nodeValue; if (!v || !v.trim()) continue;
      var t = tr(v, d); if (t !== v) n.nodeValue = t;
    }
    var els = root.querySelectorAll ? root.querySelectorAll("[title],[aria-label],[placeholder]") : [];
    for (var i = 0; i < els.length; i++) for (var j = 0; j < attrs.length; j++) {
      var a = attrs[j], v2 = els[i].getAttribute(a);
      if (v2) { var t2 = tr(v2, d); if (t2 !== v2) els[i].setAttribute(a, t2); }
    }
  }
  function picker() {
    var nav = document.querySelector("header .theme-toggle, .theme-toggle, header .icon-btn") || document.querySelector("header");
    if (!nav) return;
    var sel = document.createElement("select");
    sel.id = "smp-lang"; sel.setAttribute("aria-label", "Language");
    sel.title = "界面语言 / Interface language";
    sel.style.cssText = "margin-left:8px;border-radius:9px;border:1px solid var(--st-line);background:var(--st-surface);color:var(--st-ink);padding:5px 6px;font-size:13px";
    var cur = lang();
    for (var c in LABELS) { var o = document.createElement("option"); o.value = c; o.textContent = LABELS[c]; if (c === cur) o.selected = true; sel.appendChild(o); }
    sel.addEventListener("change", function () { localStorage.setItem("strata.lang", sel.value); location.reload(); });
    var host = nav.parentElement && nav.parentElement.querySelectorAll("button,select").length <= 6 ? nav.parentElement : nav;
    if (document.getElementById("smp-lang")) return;
    nav.insertAdjacentElement("afterend", sel);
  }
  var t = null;
  function schedule() { clearTimeout(t); t = setTimeout(function () { try { apply(); } catch (e) {} }, 250); }
  function boot() {
    if (!d0) snap();
    picker(); apply();
    new MutationObserver(schedule).observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: attrs });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
"""

def main():
    s = open(HTML, encoding="utf-8").read()
    js = JS_TEMPLATE.replace("%LANGS%", "{ zh: {}, " + ", ".join('"%s": %s' % (k, __import__("json").dumps(v, ensure_ascii=False)) for k, v in LANGS.items()) + " }")
    open(I18N_JS, "w", encoding="utf-8", newline="\n").write(js)
    print("[i18n.js] 写入完成，%d 字节" % len(js.encode("utf-8")))
    if "web/i18n.js" in s:
        print("[index.html] 已注入，跳过")
    else:
        anchor = "</body>"
        if s.count(anchor) != 1:
            print("[index.html] MISS: 找不到 </body>"); return 1
        s = s.replace(anchor, '<script src="web/i18n.js" defer></script>\n</body>')
        open(HTML, "w", encoding="utf-8", newline="").write(s)
        print("[index.html] 已注入 i18n 脚本")
    print("结论: 成功——浏览器 Ctrl+F5 后，主题按钮旁出现语言下拉（中文/English/Español/Português）")
    return 0

if __name__ == "__main__":
    sys.exit(main())
