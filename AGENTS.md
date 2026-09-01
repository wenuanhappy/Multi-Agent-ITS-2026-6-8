# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

Multi-Agent ITS (Intelligent Tutoring System) — A Socratic-style high school math teaching system based on the CrewAI multi-agent framework. Course: Conic Sections (椭圆/双曲线/抛物线).

**Key Design**: Flow-Crew-Agent-Tool four-layer architecture where deterministic tasks (anti-spoiler scanning, SymPy validation) run as Tools, while reasoning tasks (teaching dialogue, peer questioning) run as Agents within Crews.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys in .env
# ANTHROPIC_API_KEY=...
# DEEPSEEK_API_KEY=...

# Run the server (port 8300)
python run.py

# Access at http://localhost:8300
```

## Architecture

### Flow-Crew-Agent-Tool Hierarchy

1. **TutoringFlow** (`flow/tutoring_flow.py`): CrewAI Flow FSM orchestrator. Manages 9 E312 teaching stages via structured `LessonState` (Pydantic). Delegates LLM calls to Crews.

2. **Three Crews** (`crews/`):
   - `TeachingCrew`: Teacher agent generates Socratic responses via Sequential process
   - `FeynmanCrew`: Peer agent asks clarifying questions to test understanding depth
   - `CorrectionCrew`: TA agent provides structured math correction feedback

3. **Four Agents** (`agents/`): Teacher (Socratic dialogue), Peer (Feynman questioning), TA (math correction), Diagnostician (error classification)

4. **Four Tools** (`tools/`): AntiSpoilerTool (spoiler blacklist matching), SymPyDiagnosisTool (symbolic verification), KGRetrievalTool (knowledge graph), LLMClassifierTool (semantic classification)

### LLM Distribution

- **MiniMax-2.7-INT8**: All LLM calls (text generation + function calling) via 阿里云 PAI-EAS
  - Primary: `CREWAI_LLM` (for text generation)
  - Function calling: `CREWAI_LLM_FALLBACK` (for tool routing)
  - Direct calls: `MiniMaxProvider` in `core/llm_providers.py`

**Configuration**: `config/settings.py` → `MINIMAX_API_KEY`, `MINIMAX_BASE_URL`, `MINIMAX_MODEL`

### State Management

`LessonState` (Pydantic in `flow/state.py`) centralizes all runtime state previously scattered across `self._e312_*` attributes. Contains:
- Current stage (`E312Stage` enum with 9 stages)
- Per-stage phase tracking (e.g., `range_phase: "predict" | "derive"`)
- Feynman side-path state (`feynman_active`, turn count, pending stages)
- Example problem progress tracking

### Ablation Experiment Modes

Controlled by `MULTI_AGENT_MODE` in settings:
- **off/A**: Baseline FSM + single agent
- **B**: + TeacherAgent + AntiSpoilerTool (constraint layer)
- **C**: Full multi-Crew collaboration (TeachingCrew + FeynmanCrew + CorrectionCrew)
- **D**: C + agent autonomous tool calling

### Course Routing

- `ellipse_312` → CrewAI `TutoringFlow` (fully multi-agent)
- Other 5 courses → Legacy `LessonFlow` (equivalent logic, single-agent)

## Key File Purposes

| File | Purpose |
|------|---------|
| `config/settings.py` | LLM config, port (8300), Anthropic SDK patch |
| `flow/state.py` | `LessonState` Pydantic model, `E312Stage` enum |
| `flow/tutoring_flow.py` | Main FSM orchestrator (~60KB, all stage handlers) |
| `api/server.py` | FastAPI server, session routing to CrewAI vs legacy |
| `crews/teaching_crew.py` | Teacher agent + AntiSpoiler/KG tools, DeepSeek for routing |
| `crews/feynman_crew.py` | Peer agent Feynman loop logic |
| `crews/correction_crew.py` | TA agent structured correction generation |
| `tools/sympy_diagnosis.py` | Symbolic math validation via SymPy |
| `tools/anti_spoiler_scan.py` | Spoiler blacklist matching (deterministic) |
| `core/llm_providers.py` | Codex + DeepSeek dual-channel LLM interface |
| `core/feynman_loop.py` | Feynman side-path state machine |
| `core/diagnostic.py` | Student error tracking and state |
| `courses/example_diagnostician_312.py` | Example problem validation logic |

## Adding a New Course

1. Create `courses/example_canonicals_{id}.py` with standard answers
2. Create `courses/example_diagnostician_{id}.py` with diagnosis rules
3. Add stage enum in `flow/state.py` + handler methods in `flow/tutoring_flow.py`
4. Register in `api/server.py` `CREWAI_COURSES` or legacy routing

## Common Issues

- **Codex tool call failures**: Ensure `config/settings.py` patch loads before CrewAI imports
- **Session state corruption**: CrewAI flow state is Pydantic model, legacy uses `flow.state()` method
- **Async LLM blocking**: Server uses `asyncio.to_thread()` for synchronous LLM calls in thread pool (32 workers)
