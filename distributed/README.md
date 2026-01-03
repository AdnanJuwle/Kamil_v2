# Kamil v2 Distributed System - Quick Start

## Overview

This directory contains the distributed architecture implementation for Kamil v2. The system uses a hub-and-spoke model with an Orchestrator coordinating specialized nodes.

## Quick Start

### 1. Start All Nodes (Terminal 1: Orchestrator)

```bash
python distributed/run_orchestrator.py
```

This starts the orchestrator on port 8000 (default).

### 2. Start LLM Node (Terminal 2)

```bash
python distributed/run_llm_node.py 8001 mistral:latest localhost:8000 general
```

This starts an LLM node on port 8001, using the `mistral:latest` model, connecting to orchestrator at `localhost:8000`, with `general` specialization.

### 3. Start Tool Node (Terminal 3)

```bash
python distributed/run_tool_node.py 8002 localhost:8000
```

This starts a tool node on port 8002 with all tools available.

### 4. Start Memory Node (Terminal 4)

```bash
python distributed/run_memory_node.py 8003 localhost:8000
```

This starts a memory node on port 8003.

### 5. Run Client (Terminal 5)

```bash
python main.py distributed localhost:8000
```

Then choose your interface (cli/web/voice).

## Node Configuration

### LLM Node Specializations

You can run multiple LLM nodes with different specializations:

```bash
# Coding specialist
python distributed/run_llm_node.py 8001 mistral:latest localhost:8000 coding

# Math/logic specialist  
python distributed/run_llm_node.py 8004 mistral:latest localhost:8000 math,logic

# General purpose
python distributed/run_llm_node.py 8005 llama3:latest localhost:8000 general
```

### Tool Node Tool Selection

Run tool nodes with specific tools:

```bash
# Only file operations
python distributed/run_tool_node.py 8002 localhost:8000 file_ops

# Code and web tools
python distributed/run_tool_node.py 8006 localhost:8000 code_tools,web_tools
```

## Network Configuration

By default, nodes bind to `0.0.0.0` (all interfaces). For local-only:

- Modify the `host` parameter in node constructors
- Or use `127.0.0.1` for localhost-only

## Monitoring

### Check Orchestrator Status

```bash
curl http://localhost:8000/health
curl http://localhost:8000/nodes
```

### Check Node Capabilities

```bash
curl http://localhost:8001/capabilities  # LLM node
curl http://localhost:8002/capabilities   # Tool node
curl http://localhost:8003/capabilities  # Memory node
```

## Architecture

See `ARCHITECTURE.md` in the root directory for detailed architecture documentation.

## Troubleshooting

### Node Not Registering

1. Check orchestrator is running: `curl http://localhost:8000/health`
2. Check node logs for registration errors
3. Verify network connectivity between nodes

### Task Execution Fails

1. Check all required nodes are running
2. Verify node capabilities match task requirements
3. Check orchestrator logs for routing decisions

### Memory Operations Fail

1. Ensure memory node is running
2. Check memory node logs
3. Verify vector DB initialization

## Development

### Adding New Node Types

1. Create node class inheriting from `NodeServer`
2. Implement required routes
3. Create entry point script
4. Update orchestrator routing logic

### Extending Protocol

1. Add new message types to `distributed/protocol.py`
2. Update node implementations
3. Update orchestrator routing

