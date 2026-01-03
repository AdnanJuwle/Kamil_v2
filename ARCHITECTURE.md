# Kamil v2 - Distributed Architecture

## Overview

Kamil v2 is a **local-first, distributed AI assistant system** designed as a personal cognitive infrastructure rather than a single chatbot. It decomposes intelligence into specialized components that collaborate over a local network.

## Core Principles

1. **Local-first execution** - No cloud dependency
2. **Modular intelligence** - Task-specific models
3. **Explicit orchestration** - No hidden magic
4. **Hardware-aware routing** - Efficient resource utilization
5. **Persistent, inspectable memory** - Verifiable execution
6. **Offline survivability** - Works without internet
7. **Future verification-ready** - Designed for blockchain/provenance integration

## Architecture

### Hub-and-Spoke Model

```
                ┌────────────────────┐
                │   User Interface   │
                │ (CLI / Web / App)  │
                └─────────┬──────────┘
                          │
                  ┌───────▼────────┐
                  │  Orchestrator   │  ← Brain / Scheduler
                  │ (Coordinator)   │
                  └───────┬────────┘
          ┌───────────────┼────────────────┐
          │               │                │
┌─────────▼────────┐ ┌────▼─────────┐ ┌────▼─────────┐
│ LLM Node(s)       │ │ Tool Node(s)  │ │ Memory Node  │
│ (Reasoning)       │ │ (Execution)   │ │ (Persistence)│
└─────────┬────────┘ └────┬─────────┘ └────┬─────────┘
          │               │                │
   ┌──────▼─────┐   ┌─────▼─────┐   ┌──────▼─────┐
   │ GPU System │   │ CPU System│   │ Disk / DB  │
   └────────────┘   └───────────┘   └────────────┘
```

## Component Roles

### 1. Orchestrator Node (Coordinator)

**Responsibilities:**
- Task decomposition
- Model selection
- Routing & scheduling
- State tracking
- Dependency resolution

**Does NOT:**
- Perform heavy inference
- Store large memory blobs
- Execute tools directly

**Think of it as:** A kernel scheduler for intelligence.

### 2. LLM Nodes (Reasoning Engines)

**Properties:**
- Stateless by default
- No direct memory writes
- Pure reasoning interfaces
- Can be specialized (coding, math, general, etc.)

**Execution Model:**
1. Receive task slice
2. Produce structured output
3. Return to orchestrator

### 3. Tool Nodes (Execution Layer)

**Properties:**
- Execute actions (not reasoning)
- Validation & sandboxing
- Permission checks
- No direct LLM access

**Critical Rule:** LLMs never execute tools directly. All actions go through tool nodes.

### 4. Memory Node (Persistent Cognition)

**Memory Types:**
- Short-term context
- Long-term semantic memory
- Episodic memory
- Structured knowledge

**Storage Forms:**
- Vector database (semantic recall)
- Relational/document DB (facts)
- Time-indexed logs (episodes)

**Access Control:**
- Read-only for LLMs
- Write-controlled by orchestrator

### 5. Hardware-Aware Routing

Each node advertises:
- CPU cores
- RAM
- VRAM
- Accelerator availability
- Current load

Orchestrator decides:
- Which device runs what
- Whether to parallelize
- Whether to degrade gracefully

## Communication Protocol

- **Transport:** REST over HTTP (local network)
- **Format:** JSON
- **Stateless:** No hidden shared state
- **Explicit schemas:** All messages typed

## Getting Started

### 1. Start Orchestrator

```bash
python distributed/run_orchestrator.py [port]
# Default port: 8000
```

### 2. Start LLM Node

```bash
python distributed/run_llm_node.py [port] [model] [orchestrator_addr] [specializations]
# Example:
python distributed/run_llm_node.py 8001 mistral:latest localhost:8000 coding,general
```

### 3. Start Tool Node

```bash
python distributed/run_tool_node.py [port] [orchestrator_addr] [tools]
# Example:
python distributed/run_tool_node.py 8002 localhost:8000 file_ops,code_tools
```

### 4. Start Memory Node

```bash
python distributed/run_memory_node.py [port] [orchestrator_addr]
# Example:
python distributed/run_memory_node.py 8003 localhost:8000
```

### 5. Run Client (UI)

```bash
# Distributed mode
python main.py distributed [orchestrator_addr]

# Monolithic mode (backward compatible)
python main.py
```

## Example Flow

**User:** "Train a small ML model and summarize results."

**Flow:**
1. UI → Orchestrator
2. Orchestrator decomposes task
3. Orchestrator → LLM Node (planning)
4. LLM Node → Orchestrator (training plan)
5. Orchestrator → Tool Node (execute training)
6. Tool Node → Orchestrator (metrics)
7. Orchestrator → LLM Node (summarize)
8. LLM Node → Orchestrator (summary)
9. Orchestrator → Memory Node (store experiment)
10. Orchestrator → UI (final response)

**No step is implicit. Everything is explicit.**

## File Structure

```
distributed/
├── __init__.py
├── protocol.py              # Communication schemas
├── network.py               # REST API layer
├── orchestrator_node.py     # Central coordinator
├── llm_node.py              # Reasoning engine
├── tool_node.py             # Execution layer
├── memory_node.py           # Persistent storage
├── node_discovery.py        # Registration & discovery
├── distributed_agent.py     # Client interface
├── run_orchestrator.py      # Orchestrator entry point
├── run_llm_node.py          # LLM node entry point
├── run_tool_node.py         # Tool node entry point
└── run_memory_node.py       # Memory node entry point
```

## Technical Highlights

- **Separation of concerns:** Reasoning vs execution
- **No LLM god object:** Each component has clear boundaries
- **Deterministic orchestration:** Explicit task graphs
- **Horizontal scalability:** Add more nodes as needed
- **Hardware efficiency:** Route tasks to appropriate hardware
- **Inspectable state:** All operations are explicit and logged

This is **systems engineering**, not prompt engineering.

