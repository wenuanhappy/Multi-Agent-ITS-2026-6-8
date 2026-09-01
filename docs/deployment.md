部署指南
========

环境要求：Python 3.10+，macOS/Linux/Windows 都行，需要能访问 Anthropic API 和 DeepSeek API。


1) 安装依赖
-----------

cd Multi-Agent-ITS
pip install -r requirements.txt

如果 crewai 装得慢可以分开装：
pip install fastapi uvicorn anthropic httpx sympy pydantic python-dotenv
pip install crewai crewai-tools


2) 配置 API Key
---------------

在项目根目录建一个 .env 文件（注意有个点）：

ANTHROPIC_API_KEY=sk-ant-你的Anthropic密钥

DEEPSEEK_API_KEY=你的DeepSeek密钥

两个都需要，Anthropic 做文本生成，DeepSeek 做工具路由。


3) 启动
-------

python run.py

正常会看到：
  Starting Multi-Agent ITS (CrewAI) on http://0.0.0.0:8300
  [config] anthropic SDK patched: strict tools will be stripped
  [server] 默认线程池已调大至 32 workers

浏览器打开 http://localhost:8300 就能用。

使用流程：首页选曲线 → 选小节 → 进入交互课堂（左边对话，右边JSXGraph画布）


4) 端口冲突
-----------

默认 8300。被占用的话：
  API_PORT=9000 python run.py
或者直接改 config/settings.py 里的 API_PORT。


6) 目录说明
-----------

Multi-Agent-ITS/
├── run.py              启动入口
├── .env                API 密钥（别提交git）
├── config/             配置
├── api/                FastAPI 服务端
├── flow/               CrewAI Flow 编排器（FSM状态机）
├── agents/             4个 CrewAI Agent
├── crews/              3个 Crew（教学/费曼/纠错）
├── tools/              4个 CrewAI Tool
├── core/               共享核心模块
├── courses/            例题数据和诊断协议
├── legacy/             完整课程引擎（6课通用状态机）
├── knowledge_graph/    圆锥曲线知识图谱
├── frontend/           前端（3个html）
└── docs/               文档
