"""
Hardcore Diagnostic & Bug-Hunting Script for XAUUSD AI Trading Bot.
Scans all modules, checks AST, tests imports, verifies database schemas,
and checks for edge-case failure modes across all subsystems.
"""

import sys
import os
import ast
import traceback
import importlib

# Ensure project root is on path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

print(f"[+] Initializing Hardcore Diagnostic Suite in {ROOT_DIR}")

failures = []
warnings = []
passed = 0

# ==========================================
# TEST 1: AST Syntax and Bug Pattern Scan
# ==========================================
print("\n" + "="*60)
print("PHASE 1: AST SYNTAX & ANTI-PATTERN STATIC ANALYSIS")
print("="*60)

py_files = []
for root, dirs, files in os.walk(ROOT_DIR):
    rel_root = os.path.relpath(root, ROOT_DIR)
    if any(p in rel_root.split(os.sep) for p in [".git", ".venv", "__pycache__", "scratch", "deploy"]):
        continue
    for f in files:
        if f.endswith(".py"):
            py_files.append(os.path.join(root, f))

print(f"[*] Scanning {len(py_files)} Python source files...")

for file_path in py_files:
    rel_path = os.path.relpath(file_path, ROOT_DIR)
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
        tree = ast.parse(code, filename=rel_path)
    except Exception as e:
        failures.append(f"SYNTAX ERROR in {rel_path}: {e}")
        continue

    # Walk AST to detect dangerous patterns
    for node in ast.walk(tree):
        # 1. Bare except:
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                warnings.append(f"{rel_path}:{node.lineno} - Bare 'except:' clause (masks KeyboardInterrupt and SystemExit)")
            elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
                # Check if body is just pass
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    warnings.append(f"{rel_path}:{node.lineno} - Silent 'except Exception: pass' (swallows bugs)")

        # 2. Potential unclosed sqlite connections or open calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "connect":
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "sqlite3":
                    # Check if inside a 'with' block or assigned to variable
                    pass

print(f"[+] AST Analysis Complete. Scanned {len(py_files)} files.")
print(f"    - Failures: {len([f for f in failures if 'SYNTAX' in f])}")
print(f"    - Warnings: {len(warnings)}")

# ==========================================
# TEST 2: Import Validation Across All Core Modules
# ==========================================
print("\n" + "="*60)
print("PHASE 2: DYNAMIC IMPORT VALIDATION")
print("="*60)

critical_modules = [
    "config.settings",
    "config.credentials",
    "core.time_engine",
    "core.calendar_manager",
    "core.holiday_manager",
    "core.latency_guard",
    "core.state_machine",
    "risk.position_sizer",
    "risk.risk_manager",
    "risk.circuit_breaker",
    "risk.input_guardrails",
    "risk.prop_firm_guard",
    "indicators.range_detector",
    "indicators.technicals",
    "indicators.macro_trend",
    "intelligence.war_room",
    "intelligence.agent_radar",
    "intelligence.agent_predator",
    "intelligence.agent_inquisitor",
    "intelligence.economic_calendar",
    "intelligence.quantum_twin",
    "intelligence.global_sentinel",
    "database.jarvis_logger",
    "communication.telegram_hud",
    "communication.jarvis_voice",
    "engine.mt5_execution",
    "engine.session_reporter",
    "engine.strategy",
    "engine.orchestrator",
    "licensing.models",
    "licensing.database",
    "security.license_enforcer",
]

for mod in critical_modules:
    try:
        m = importlib.import_module(mod)
        passed += 1
        print(f"  [OK] {mod}")
    except Exception as e:
        err_msg = f"IMPORT FAILED: {mod} -> {e}\n{traceback.format_exc()}"
        failures.append(err_msg)
        print(f"  [FAIL] {mod}: {e}")

# ==========================================
# TEST 3: Database Column & Schema Consistency Check
# ==========================================
print("\n" + "="*60)
print("PHASE 3: DATABASE SCHEMA CONSISTENCY AUDIT")
print("="*60)

try:
    from database.jarvis_logger import JarvisDatabaseLogger
    test_db = os.path.join(ROOT_DIR, "data", "test_diagnostic.db")
    if os.path.exists(test_db):
        os.remove(test_db)
    
    logger = JarvisDatabaseLogger(db_path=test_db)
    # Check tables
    import sqlite3
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    print(f"  [+] Created Tables: {tables}")
    
    # Check trades columns
    cursor.execute("PRAGMA table_info(trades);")
    trade_cols = [r[1] for r in cursor.fetchall()]
    print(f"  [+] 'trades' columns: {trade_cols}")
    conn.close()

    # Check if session_reporter query matches trades schema
    from engine.session_reporter import TitanSessionReporter
    reporter = TitanSessionReporter(db_path=test_db)
    # Test fetch_db_trades
    trades_res = reporter.fetch_db_trades()
    print(f"  [+] TitanSessionReporter.fetch_db_trades() ran without error, returned: {len(trades_res)} trades")
    
    # Test logging a trade
    log_ok = logger.log_trade_deployment(
        ticket_id=123456,
        direction="BUY",
        volume=0.05,
        entry_price=2650.50,
        sl=2640.00,
        tp=2670.00
    )
    if not log_ok:
        failures.append("Failed to log trade deployment into test DB")
    else:
        print("  [+] Successfully logged test trade deployment")

    # Fetch trades again via session reporter
    trades_res_after = reporter.fetch_db_trades()
    print(f"  [+] TitanSessionReporter fetched {len(trades_res_after)} trade records")
    if len(trades_res_after) == 0:
        failures.append("CRITICAL: TitanSessionReporter failed to retrieve logged trade (schema mismatch!)")

    # Clean up test DB
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except Exception:
            pass

except Exception as e:
    failures.append(f"Database schema audit exception: {e}\n{traceback.format_exc()}")

# ==========================================
# TEST 4: Orchestrator Single-Cycle Simulation (Mock MT5)
# ==========================================
print("\n" + "="*60)
print("PHASE 4: ORCHESTRATOR SINGLE-STEP EXECUTION SIMULATION")
print("="*60)

try:
    from engine.orchestrator import JarvisOrchestrator
    
    # Initialize with mock mode
    orch = JarvisOrchestrator(
        telegram_token=None,
        telegram_chat_id=None,
        elevenlabs_key=None,
        symbol="XAUUSD"
    )
    init_ok = orch.initialize()
    print(f"  [+] Orchestrator initialized: {init_ok}")
    
    # Run a single step to verify pipeline
    print("  [*] Running orchestrator.run_step() in mock mode...")
    orch.run_step()
    print("  [+] orchestrator.run_step() executed successfully with 0 unhandled exceptions!")
    passed += 1

except Exception as e:
    failures.append(f"Orchestrator simulation failed: {e}\n{traceback.format_exc()}")
    print(f"  [-] Orchestrator failed: {e}")

# ==========================================
# TEST 5: Standalone Test Suite Execution Check
# ==========================================
print("\n" + "="*60)
print("PHASE 5: STANDALONE TEST RUNNER VERIFICATION")
print("="*60)

# Check if tests/test_all.py has sys.path setup
test_all_path = os.path.join(ROOT_DIR, "tests", "test_all.py")
with open(test_all_path, "r", encoding="utf-8") as f:
    t_content = f.read()

if "sys.path.insert" not in t_content:
    failures.append("tests/test_all.py is missing sys.path configuration to allow direct execution `python tests/test_all.py`")
else:
    print("  [+] tests/test_all.py has proper sys.path configuration")

# ==========================================
# SUMMARY REPORT
# ==========================================
print("\n" + "="*60)
print(f"DIAGNOSTIC SUMMARY: {passed} PASSED | {len(failures)} FAILURES | {len(warnings)} WARNINGS")
print("="*60)

if failures:
    print("\n[-] DETECTED CRITICAL FAILURES:")
    for f in failures:
        print(f"  * {f}")
else:
    print("\n[+] ZERO CRITICAL FAILURES DETECTED!")

if warnings:
    print(f"\n[!] WARNINGS DETECTED ({len(warnings)} total, top 10 shown):")
    for w in warnings[:10]:
        print(f"  * {w}")
