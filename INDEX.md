# Swiggy Instamart Buying Pattern Analyzer - File Index

## 📋 Quick Navigation

### Getting Started
1. **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Start here! Complete project overview
2. **[QUICKSTART.md](QUICKSTART.md)** - Quick commands reference
3. **[NEXT_STEPS.md](NEXT_STEPS.md)** - Installation and setup guide
4. **[README.md](README.md)** - Comprehensive documentation

### Installation & Setup
- **[install.sh](install.sh)** - Automated installation script
- **[verify.sh](verify.sh)** - Verify installation completeness
- **[requirements.txt](requirements.txt)** - Python dependencies

### Configuration
- **[config.yaml](config.yaml)** - User configuration file
- **[pyproject.toml](pyproject.toml)** - Package metadata
- **[setup.py](setup.py)** - Setup script

### Technical Details
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Architecture & implementation details

## 📁 Source Code Structure

### Core Package: `swiggy_analyzer/`

#### Authentication (`auth/`)
- **oauth_manager.py** (183 lines) - OAuth PKCE flow implementation
- **token_store.py** (103 lines) - Encrypted token storage with macOS Keychain

#### MCP Client (`mcp/`)
- **client.py** (160 lines) - HTTP client with rate limiting and retries
- **endpoints.py** (156 lines) - Swiggy Instamart API wrapper methods

#### Data Layer (`data/`)
- **models.py** (98 lines) - Pydantic data models
- **repository.py** (341 lines) - SQLite repository with all DB operations
- **schema.sql** (95 lines) - Complete database schema

#### Analysis Engine (`analysis/`)
- **pattern_detector.py** (52 lines) - Buying pattern detection
- **scoring.py** (175 lines) - Weighted scoring algorithm
- **predictor.py** (62 lines) - Main recommendation engine

#### Basket Manager (`basket/`)
- **manager.py** (116 lines) - Basket operations and validation
- **formatter.py** (93 lines) - Rich terminal formatting

#### Scheduler (`scheduler/`)
- **cron_manager.py** (186 lines) - macOS launchd integration

#### Configuration (`config/`)
- **defaults.py** (48 lines) - Default configuration values
- **settings.py** (125 lines) - YAML configuration manager

#### CLI Interface (`cli/`)
- **main.py** (33 lines) - CLI entry point
- **commands.py** (436 lines) - All command implementations

## 🧪 Test Suite: `tests/`

### Test Fixtures
- **conftest.py** (102 lines) - Pytest fixtures and mock data

### Test Modules
- **test_analysis/test_scoring.py** (118 lines) - Scoring algorithm tests
- **test_analysis/test_pattern_detector.py** (41 lines) - Pattern detection tests
- **test_data/test_repository.py** (62 lines) - Repository operation tests

## 📊 Statistics

### Code Metrics
- **Total Python Files**: 25
- **Total Lines of Code**: 2,541
- **Test Files**: 4
- **Test Coverage Target**: 80%+

### File Sizes
- **Documentation**: ~45 KB (6 files)
- **Source Code**: ~2,541 lines
- **Configuration**: 1.1 KB
- **Scripts**: 5.2 KB

## 🔍 Finding What You Need

### "I want to..."

#### ...get started quickly
→ Read [QUICKSTART.md](QUICKSTART.md)

#### ...understand the architecture
→ Read [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

#### ...install the system
→ Run `./install.sh` or follow [NEXT_STEPS.md](NEXT_STEPS.md)

#### ...understand the scoring algorithm
→ See `swiggy_analyzer/analysis/scoring.py` or [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

#### ...add a new feature
→ Check the extensibility section in [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

#### ...troubleshoot issues
→ Check troubleshooting in [README.md](README.md) or [NEXT_STEPS.md](NEXT_STEPS.md)

#### ...run tests
→ See testing section in [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

#### ...configure the system
→ Edit `config.yaml` or use `swiggy-analyzer config set`

#### ...understand the database
→ See `swiggy_analyzer/data/schema.sql` and [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

#### ...set up scheduling
→ Use `swiggy-analyzer schedule enable` (see [QUICKSTART.md](QUICKSTART.md))

## 🗂️ Complete File Tree

```
/Users/suvrat.hiran/project/swiggy/
│
├── 📚 Documentation (6 files)
│   ├── INDEX.md                          ← You are here
│   ├── PROJECT_OVERVIEW.md               ← Start here!
│   ├── README.md                         ← Full documentation
│   ├── QUICKSTART.md                     ← Quick reference
│   ├── NEXT_STEPS.md                     ← Setup guide
│   └── IMPLEMENTATION_SUMMARY.md         ← Technical details
│
├── 🔧 Configuration (4 files)
│   ├── config.yaml                       ← User settings
│   ├── pyproject.toml                    ← Package metadata
│   ├── setup.py                          ← Setup script
│   └── requirements.txt                  ← Dependencies
│
├── 📜 Scripts (3 files)
│   ├── install.sh                        ← Installation
│   ├── verify.sh                         ← Verification
│   └── .gitignore                        ← Git ignore rules
│
├── 📦 Source Code - swiggy_analyzer/ (25 Python files)
│   │
│   ├── 🔐 auth/ (2 files)
│   │   ├── oauth_manager.py              ← OAuth PKCE flow
│   │   └── token_store.py                ← Token encryption
│   │
│   ├── 🌐 mcp/ (2 files)
│   │   ├── client.py                     ← HTTP client
│   │   └── endpoints.py                  ← API wrappers
│   │
│   ├── 💾 data/ (4 files)
│   │   ├── models.py                     ← Pydantic models
│   │   ├── repository.py                 ← SQLite operations
│   │   ├── schema.sql                    ← DB schema
│   │   └── __init__.py
│   │
│   ├── 🧮 analysis/ (4 files)
│   │   ├── pattern_detector.py           ← Pattern detection
│   │   ├── scoring.py                    ← Scoring algorithm
│   │   ├── predictor.py                  ← Recommendation engine
│   │   └── __init__.py
│   │
│   ├── 🛒 basket/ (3 files)
│   │   ├── manager.py                    ← Basket operations
│   │   ├── formatter.py                  ← Rich formatting
│   │   └── __init__.py
│   │
│   ├── ⏰ scheduler/ (2 files)
│   │   ├── cron_manager.py               ← Launchd integration
│   │   └── __init__.py
│   │
│   ├── ⚙️ config/ (3 files)
│   │   ├── settings.py                   ← Config manager
│   │   ├── defaults.py                   ← Default values
│   │   └── __init__.py
│   │
│   ├── 💻 cli/ (3 files)
│   │   ├── main.py                       ← Entry point
│   │   ├── commands.py                   ← All commands
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── 🧪 Tests - tests/ (4 Python files)
│   ├── conftest.py                       ← Test fixtures
│   ├── test_analysis/
│   │   ├── test_scoring.py               ← Scoring tests
│   │   └── test_pattern_detector.py      ← Pattern tests
│   └── test_data/
│       └── test_repository.py            ← Repository tests
│
├── 📁 Data (created on first run)
│   └── swiggy.db                         ← SQLite database
│
└── 📋 Logs (created on first run)
    └── swiggy_analyzer.log               ← Application logs
```

## 🎯 Key Files by Function

### Authentication & Security
- `auth/oauth_manager.py` - OAuth flow
- `auth/token_store.py` - Token encryption
- Config: OAuth endpoints, PKCE implementation

### Data Management
- `data/repository.py` - All database operations
- `data/models.py` - Data structures
- `data/schema.sql` - Database schema
- Database: `data/swiggy.db`

### Analysis & Recommendations
- `analysis/scoring.py` - Scoring algorithm (★ Core logic)
- `analysis/pattern_detector.py` - Pattern detection
- `analysis/predictor.py` - Recommendation engine

### API Integration
- `mcp/client.py` - HTTP client with rate limiting
- `mcp/endpoints.py` - Swiggy API wrappers

### User Interface
- `cli/commands.py` - All CLI commands
- `basket/formatter.py` - Rich terminal UI

### Automation
- `scheduler/cron_manager.py` - Daily scheduling

### Configuration
- `config.yaml` - User settings
- `config/settings.py` - Config manager

## 🔗 Cross-References

### Modified Together
- `analysis/scoring.py` + `config.yaml` (scoring weights)
- `mcp/endpoints.py` + `data/models.py` (API responses)
- `cli/commands.py` + `basket/manager.py` (basket operations)

### Dependencies
- CLI → All modules (orchestrates everything)
- Predictor → Detector + Scorer
- Basket Manager → MCP Endpoints
- All modules → Repository (data layer)

## 📈 Complexity by Module

### Simple (< 100 lines)
- Pattern detector, Predictor, Defaults, CLI main

### Medium (100-200 lines)
- OAuth manager, Token store, MCP client, Endpoints, Scorer, Basket manager, Formatter, Scheduler, Settings

### Complex (> 200 lines)
- Repository (341 lines) - Comprehensive data operations
- CLI Commands (436 lines) - All command implementations

## 🚀 Quick Commands

```bash
# View any file
cat swiggy_analyzer/analysis/scoring.py

# Run verification
./verify.sh

# Install
./install.sh

# Check stats
find swiggy_analyzer -name "*.py" -exec wc -l {} +

# Run tests
pytest tests/ -v
```

## 📝 Notes

- All Python files include comprehensive docstrings
- Each module has a specific, focused responsibility
- Clean separation between layers (CLI → Services → Data)
- Easy to test and extend
- Production-ready code quality

---

**Last Updated**: February 2, 2026

**Total Files**: 40+ (code, tests, docs, config)

**Ready to Use**: ✅ Yes
