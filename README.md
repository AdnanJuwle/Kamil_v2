# Kamil v2 - Distributed Local AI Assistant

> **A local-first, distributed AI assistant system designed as a personal cognitive infrastructure**

Kamil v2 is not "an LLM app" - it is an **AI operating layer across devices**. Unlike traditional monolithic assistants, Kamil v2 decomposes intelligence into specialized components that collaborate over a local network, enabling higher capability without requiring a single powerful device.

## 🎯 What Makes Kamil v2 Different

- **Local-first execution** - No cloud dependency, complete privacy
- **Distributed architecture** - Run components across multiple devices
- **Hardware-aware routing** - Automatically utilizes available GPUs, CPUs, and memory
- **Modular intelligence** - Specialized nodes for reasoning, execution, and memory
- **Persistent memory** - Long-term semantic and episodic memory
- **Offline survivability** - Works completely offline
- **Verification-ready** - Designed for future blockchain/provenance integration

## 🏗️ Architecture

Kamil v2 uses a **hub-and-spoke distributed architecture**:

```
                ┌────────────────────┐
                │   User Interface   │
                │ (CLI / Web / App)  │
                └─────────┬──────────┘
                          │
                  ┌───────▼────────┐
                  │  Orchestrator   │  ← Central Brain
                  │ (Coordinator)   │
                  └───────┬────────┘
          ┌───────────────┼────────────────┐
          │               │                │
┌─────────▼────────┐ ┌────▼─────────┐ ┌────▼─────────┐
│ LLM Node(s)       │ │ Tool Node(s)  │ │ Memory Node  │
│ (Reasoning)       │ │ (Execution)   │ │ (Persistence)│
└──────────────────┘ └───────────────┘ └──────────────┘
```

### Core Components

- **Orchestrator Node** - Task decomposition, routing, and scheduling (the brain)
- **LLM Nodes** - Stateless reasoning engines (can be specialized: coding, math, general)
- **Tool Nodes** - Execution layer with validation and sandboxing
- **Memory Node** - Persistent storage (vector DB, knowledge graph, episodic logs)

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- At least one LLM model pulled (e.g., `ollama pull mistral:latest`)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AdnanJuwle/Kamil_v2.git
cd Kamil_v2
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running in Distributed Mode

**Terminal 1 - Start Orchestrator:**
```bash
python distributed/run_orchestrator.py
```

**Terminal 2 - Start LLM Node:**
```bash
python distributed/run_llm_node.py 8001 mistral:latest localhost:8000 general
```

**Terminal 3 - Start Tool Node:**
```bash
python distributed/run_tool_node.py 8002 localhost:8000
```

**Terminal 4 - Start Memory Node:**
```bash
python distributed/run_memory_node.py 8003 localhost:8000
```

**Terminal 5 - Run Client:**
```bash
python main.py distributed localhost:8000
```

Then choose your interface (cli/web/voice).

### Running in Monolithic Mode (Backward Compatible)

For a single-process setup:

```bash
python main.py
```

This runs all components in one process (useful for development/testing).

## 📖 Usage Examples

### Distributed Setup

The distributed mode allows you to:
- Run LLM inference on a GPU-equipped machine
- Execute tools on a different machine
- Store memory on a dedicated storage server
- Scale horizontally by adding more nodes

### Specialized LLM Nodes

Run multiple LLM nodes with different specializations:

```bash
# Coding specialist
python distributed/run_llm_node.py 8001 mistral:latest localhost:8000 coding

# Math/logic specialist
python distributed/run_llm_node.py 8004 mistral:latest localhost:8000 math,logic

# General purpose
python distributed/run_llm_node.py 8005 llama3:latest localhost:8000 general
```

The orchestrator will automatically route tasks to the appropriate specialist.

## 🛠️ Features

### Current Capabilities

- **Multi-modal interfaces** - CLI, Web UI, Voice (planned)
- **File operations** - Read, write, create, delete files
- **Code generation** - Generate and execute code
- **Web research** - Search and fetch web content
- **Automation** - System automation and workflows
- **Persistent memory** - Semantic search and knowledge graph

### Architecture Highlights

- **Separation of concerns** - Reasoning vs execution
- **No LLM god object** - Clear component boundaries
- **Deterministic orchestration** - Explicit task dependency graphs
- **Horizontal scalability** - Add nodes as needed
- **Hardware efficiency** - Route tasks to appropriate hardware
- **Inspectable state** - All operations are explicit and logged

## 📁 Project Structure

```
Kamil_v2/
├── core/                    # Core components
│   ├── agent.py             # Monolithic agent (backward compat)
│   ├── llm_engine.py         # LLM inference engine
│   ├── memory.py             # Memory system
│   ├── task_orchestrator.py  # Task orchestration
│   └── ...
├── distributed/              # Distributed architecture
│   ├── orchestrator_node.py  # Central coordinator
│   ├── llm_node.py          # Reasoning engine node
│   ├── tool_node.py         # Execution node
│   ├── memory_node.py       # Storage node
│   ├── network.py           # Communication layer
│   └── ...
├── interfaces/              # User interfaces
│   ├── cli.py               # Command-line interface
│   ├── web_ui.py            # Web interface
│   └── voice_interface.py   # Voice interface
├── tools/                    # Tool implementations
│   ├── file_ops.py          # File operations
│   ├── code_tools.py        # Code generation
│   ├── web_tools.py         # Web scraping
│   └── ...
├── memory_store/            # Memory storage
│   ├── vector_db.py         # Vector database
│   └── knowledge_graph.py   # Knowledge graph
├── main.py                   # Entry point
├── ARCHITECTURE.md           # Detailed architecture docs
└── README.md                 # This file
```

## 🔧 Configuration

Edit `config.py` to configure:
- Default model name
- Timeout settings
- Memory limits
- Embedding model

## 🧪 Development

### Running Tests

```bash
# Add tests as they're developed
python -m pytest tests/
```

### Adding New Nodes

1. Create node class inheriting from `NodeServer`
2. Implement required routes
3. Create entry point script
4. Update orchestrator routing logic

See `distributed/README.md` for detailed development guide.

## 📝 License

[Add your license here]

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🔮 Roadmap

- [ ] Enhanced sandboxing for tool execution
- [ ] Automatic node discovery (mDNS/Bonjour)
- [ ] Blockchain/provenance integration
- [ ] Advanced memory compression
- [ ] Multi-device synchronization
- [ ] Performance optimizations
- [ ] Docker containerization
- [ ] Kubernetes deployment support

## 📚 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed architecture documentation
- [distributed/README.md](distributed/README.md) - Distributed system quick start

## 🙏 Acknowledgments

Kamil v2 is designed as a serious systems engineering project, not just prompt engineering. It represents a new approach to local AI assistants.

---

**Built with ❤️ for local-first AI**

