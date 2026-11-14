"""
Comprehensive Verification Suite: Forward-Test Telemetry, Risk Discipline,
Fernet AES Vault Security, and Purged Walk-Forward ML Classifier.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd

_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from core.vault_manager import VaultManager
from communication.whatsapp_bot import WhatsAppBot
from telemetry.forward_test_tracker import ForwardTestTracker
from ai.feature_extractor import FeatureExtractor
from ai.meta_labeler import MetaLabeler
from config.settings import AISettings
from scripts.train_meta_model import train_and_save_meta_model, purged_walk_forward_cv, fit_logistic_regression, compute_roc_auc
from engine.session_reporter import TitanSessionReporter
from backtest.engine import BacktestEngine


class TestForwardTestAndMLPipeline(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = os.path.join(self.temp_dir, "test_secrets.vault")
        self.fwd_db_path = os.path.join(self.temp_dir, "forward_test.sqlite")
        self.fwd_csv_path = os.path.join(self.temp_dir, "forward_features.csv")
        self.model_json_path = os.path.join(self.temp_dir, "meta_classifier.json")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # =========================================================================
    # 1. VAULT MANAGER: AES FERNET v2 & LEGACY FALLBACK
    # =========================================================================

    def test_vault_fernet_v2_and_backward_compatibility(self):
        vault = VaultManager(vault_path=self.vault_path, master_passphrase="quant-secret-passphrase-2026")
        secrets = {
            "MT5_LOGIN": 88402914,
            "MT5_PASSWORD": "SuperSecretTraderPass123!",
            "MT5_SERVER": "MetaQuotes-Demo"
        }

        # Encrypt and save v2
        ok = vault.encrypt_and_save(secrets)
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(self.vault_path))

        with open(self.vault_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        self.assertEqual(payload.get("version"), 2)
        self.assertEqual(payload.get("cipher"), "fernet-aes-128-cbc-hmac-sha256")
        self.assertTrue(payload["data"].startswith("gAAAAA"))
        self.assertNotIn("SuperSecretTraderPass123!", json.dumps(payload))

        # Successful decryption
        decrypted = vault.load_and_decrypt()
        self.assertIsNotNone(decrypted)
        self.assertEqual(decrypted["MT5_LOGIN"], secrets["MT5_LOGIN"])
        self.assertEqual(decrypted["MT5_PASSWORD"], secrets["MT5_PASSWORD"])

        # Wrong passphrase returns None
        wrong_vault = VaultManager(vault_path=self.vault_path, master_passphrase="wrong-passphrase")
        self.assertIsNone(wrong_vault.load_and_decrypt())

        # Tampered ciphertext returns None
        tampered = dict(payload)
        tampered["data"] = payload["data"][:-8] + "AAAAAAAA"
        with open(self.vault_path, "w", encoding="utf-8") as f:
            json.dump(tampered, f)
        self.assertIsNone(vault.load_and_decrypt())

        # Legacy v1 fallback and automatic upgrade
        import base64
        legacy_key = vault._derive_legacy_key(vault.master_passphrase)
        raw_bytes = json.dumps(secrets).encode("utf-8")
        encrypted_v1 = bytearray()
        for i, b in enumerate(raw_bytes):
            encrypted_v1.append(b ^ legacy_key[i % len(legacy_key)])
        v1_payload = {
            "version": 1,
            "data": base64.b64encode(bytes(encrypted_v1)).decode("ascii")
        }
        with open(self.vault_path, "w", encoding="utf-8") as f:
            json.dump(v1_payload, f)

        # Legacy read works
        v1_decrypted = vault.load_and_decrypt()
        self.assertIsNotNone(v1_decrypted)
        self.assertEqual(v1_decrypted["MT5_LOGIN"], secrets["MT5_LOGIN"])

        # Upgrade to v2
        upgraded = vault.upgrade_vault_to_fernet()
        self.assertTrue(upgraded)
        with open(self.vault_path, "r", encoding="utf-8") as f:
            upgraded_payload = json.load(f)
        self.assertEqual(upgraded_payload["version"], 2)
        upgraded_decrypted = vault.load_and_decrypt()
        self.assertEqual(upgraded_decrypted["MT5_PASSWORD"], secrets["MT5_PASSWORD"])

    # =========================================================================
    # 2. WHATSAPP BOT: PRICING ALIGNMENT & CHECKOUT URL
    # =========================================================================

    def test_whatsapp_pricing_tiers_alignment(self):
        bot = WhatsAppBot()
        bot.forward_lead_to_telegram = lambda *args, **kwargs: True
        dispatched_messages = []
        bot.send_text_message = lambda recipient, text: dispatched_messages.append((recipient, text))

        # Query price payload
        price_payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "contacts": [{"profile": {"name": "Buyer"}}],
                        "messages": [{
                            "from": "test_user_1",
                            "type": "text",
                            "text": {"body": "What is the price?"}
                        }]
                    }
                }]
            }]
        }
        bot.process_incoming_message(price_payload)
        self.assertEqual(len(dispatched_messages), 1)
        resp_text = dispatched_messages[0][1]

        # Verify $50, $450, $999 tiers present
        self.assertIn("$50 USDT / ₹4,499 INR", resp_text)
        self.assertIn("$450 USDT / ₹39,999 INR", resp_text)
        self.assertIn("$999 USDT / ₹89,999 INR", resp_text)
        self.assertIn("https://smkanish2009-blip.github.io/don-aurelius/checkout.html", resp_text)
        self.assertNotIn("$499", resp_text)
        self.assertNotIn("$1,499", resp_text)
        self.assertNotIn("$3,999", resp_text)

        # Query buy payload
        dispatched_messages.clear()
        buy_payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "contacts": [{"profile": {"name": "Buyer"}}],
                        "messages": [{
                            "from": "test_user_2",
                            "type": "text",
                            "text": {"body": "I want to buy"}
                        }]
                    }
                }]
            }]
        }
        bot.process_incoming_message(buy_payload)
        buy_text = dispatched_messages[0][1]
        self.assertIn("https://smkanish2009-blip.github.io/don-aurelius/checkout.html", buy_text)

    # =========================================================================
    # 3. FORWARD TEST TRACKER: METRICS, SHARPE, SORTINO, DRAWDOWN, HORIZONS
    # =========================================================================

    def test_forward_test_tracker_metrics_and_horizons(self):
        tracker = ForwardTestTracker(db_path=self.fwd_db_path)
        base_time = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Log simulated daily equity curve over 70 days (INTERIM_FORWARD_TEST stage: 60-180 days)
        current_equity = 100000.0

        for day in range(70):
            day_dt = base_time + timedelta(days=day)
            day_iso = day_dt.isoformat()

            # Record candidate
            ticket = 7000 + day
            p_win = 0.65 if day % 2 == 0 else 0.45
            status = "EXECUTED" if p_win >= 0.55 else "VETOED_AI"

            features = {
                "range_height_usd": 12.5,
                "range_x_atr_h1": 1.4,
                "adx_h1": 26.0,
                "m15_body_to_range": 0.70
            }

            tracker.record_signal_candidate(
                signal_id=f"sig_{ticket}",
                symbol="XAUUSD",
                setup_type="SETUP_A",
                direction="BUY",
                entry_price=2650.0,
                stop_loss=2642.0,
                take_profit=2666.0,
                risk_r=2.0,
                spread_usd=0.20,
                regime="BULLISH_EXPANSION",
                meta_prob=p_win,
                model_mode="HEURISTIC_WARMUP",
                status=status,
                features=features,
                ticket_id=ticket if status == "EXECUTED" else None,
                timestamp_utc=day_iso
            )

            # Record closed trade outcome if executed
            if status == "EXECUTED":
                pnl = 800.0 if (day % 3 != 0) else -500.0
                pnl_r = 1.6 if pnl > 0 else -1.0
                tracker.record_outcome(
                    ticket_id=ticket,
                    exit_price=2666.0 if pnl > 0 else 2642.0,
                    net_pnl_usd=pnl,
                    pnl_r=pnl_r,
                    exit_reason="TP_HIT" if pnl > 0 else "SL_HIT",
                    closed_at_utc=day_iso
                )
                current_equity += pnl

            # Record daily equity snapshot
            tracker.record_equity_snapshot(
                balance=current_equity,
                equity=current_equity,
                floating_pnl=0.0,
                timestamp_utc=day_iso
            )

        # Compute all-time metrics
        metrics = tracker.compute_metrics(window_days=None)
        self.assertGreater(metrics["total_trades"], 10)
        self.assertGreater(metrics["elapsed_days"], 65.0)
        self.assertEqual(metrics["maturity_status"], "INTERIM_FORWARD_TEST")
        self.assertIsNotNone(metrics["sharpe_ratio"])
        self.assertIsNotNone(metrics["sortino_ratio"])
        self.assertGreater(metrics["win_rate_pct"], 50.0)
        self.assertGreater(metrics["profit_factor"], 1.0)
        self.assertGreater(metrics["expectancy_r"], 0.0)

        # Verify rolling horizon report
        horizon = tracker.get_horizon_report()
        self.assertIn("all_time", horizon)
        self.assertIn("rolling_30d", horizon)
        self.assertIn("rolling_180d", horizon)
        self.assertIn("rolling_365d", horizon)
        self.assertIn("ml_dataset", horizon)

        # Export ML dataset
        csv_rows = tracker.export_ml_dataset(csv_path=self.fwd_csv_path)
        self.assertGreater(csv_rows, 10)
        self.assertTrue(os.path.exists(self.fwd_csv_path))

        # Write JSON report
        report_json = os.path.join(self.temp_dir, "forward_report.json")
        saved_report = tracker.write_json_report(json_path=report_json)
        self.assertTrue(os.path.exists(report_json))
        self.assertEqual(saved_report["all_time"]["maturity_status"], "INTERIM_FORWARD_TEST")

    # =========================================================================
    # 4. FEATURE EXTRACTOR: ALL KEYS & SANITIZATION
    # =========================================================================

    def test_feature_extractor_integrity(self):
        np.random.seed(42)
        n = 150
        dates_m5 = pd.date_range("2026-09-20 06:00:00", periods=n, freq="5min")
        df_m5 = pd.DataFrame({
            "time": dates_m5, "open": np.linspace(2650, 2655, n),
            "high": np.linspace(2652, 2658, n), "low": np.linspace(2648, 2654, n),
            "close": np.linspace(2651, 2657, n), "tick_volume": np.full(n, 500)
        })
        dates_m15 = pd.date_range("2026-09-20 06:00:00", periods=n, freq="15min")
        df_m15 = pd.DataFrame({
            "time": dates_m15, "open": np.linspace(2648, 2656, n),
            "high": np.linspace(2652, 2660, n), "low": np.linspace(2646, 2654, n),
            "close": np.linspace(2650, 2658, n), "tick_volume": np.full(n, 1200)
        })
        dates_h1 = pd.date_range("2026-09-20 06:00:00", periods=n, freq="1h")
        df_h1 = pd.DataFrame({
            "time": dates_h1, "open": np.linspace(2640, 2660, n),
            "high": np.linspace(2645, 2665, n), "low": np.linspace(2635, 2655, n),
            "close": np.linspace(2642, 2662, n), "tick_volume": np.full(n, 4000)
        })

        feats = FeatureExtractor.extract_features(
            df_m5=df_m5, df_m15=df_m15, df_h1=df_h1,
            range_high=2665.0, range_low=2650.0, spread_usd=0.25,
            direction="BUY", setup_type="SETUP_A"
        )

        # 12 legacy keys present
        legacy_keys = [
            "range_height_usd", "range_x_atr_h1", "spread_to_range_ratio",
            "garman_klass_vol_m15", "atr_ratio_m15_to_h1", "dist_to_ema200_pct",
            "ema_trend_aligned", "adx_h1", "adx_slope_3bars", "m15_body_to_range",
            "m15_upper_wick_ratio", "m15_lower_wick_ratio"
        ]
        for k in legacy_keys:
            self.assertIn(k, feats)
            self.assertFalse(np.isnan(feats[k]))

        # New quantitative microstructure & cyclical features
        new_keys = [
            "dist_to_range_high_atr", "dist_to_range_low_atr", "ema20_ema50_spread_atr",
            "m5_return_3bars", "hour_utc_sin", "hour_utc_cos", "is_buy_signal", "setup_is_breakout"
        ]
        for k in new_keys:
            self.assertIn(k, feats)
            self.assertFalse(np.isnan(feats[k]))
            self.assertFalse(np.isinf(feats[k]))

        self.assertEqual(feats["is_buy_signal"], 1.0)
        self.assertEqual(feats["setup_is_breakout"], 1.0)

    # =========================================================================
    # 5. WALK-FORWARD TRAINING & META-LABELER INFERENCE
    # =========================================================================

    def test_purged_walk_forward_training_and_meta_labeler(self):
        # Create synthetic labeled dataset with 120 samples
        np.random.seed(42)
        n = 120
        timestamps = [
            (datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=i * 4)).isoformat()
            for i in range(n)
        ]
        # Signal features
        x1 = np.random.uniform(0.5, 3.0, n)
        x2 = np.random.uniform(15.0, 45.0, n)
        x3 = np.random.uniform(0.3, 0.9, n)
        # Probabilistic target
        prob = 1.0 / (1.0 + np.exp(-(0.5 * (x1 - 1.5) + 0.05 * (x2 - 25.0) + 1.2 * (x3 - 0.5))))
        y = (np.random.rand(n) < prob).astype(int)

        df = pd.DataFrame({
            "timestamp_utc": timestamps,
            "setup_type": ["SETUP_A"] * n,
            "direction": ["BUY"] * n,
            "spread_usd": [0.20] * n,
            "regime": ["BULLISH_EXPANSION"] * n,
            "range_x_atr_h1": x1,
            "adx_h1": x2,
            "m15_body_to_range": x3,
            "win_label": y,
            "pnl_r": np.where(y == 1, 1.8, -1.0),
            "net_pnl_usd": np.where(y == 1, 900.0, -500.0)
        })
        df.to_csv(self.fwd_csv_path, index=False)

        # Train model artifact
        res = train_and_save_meta_model(
            csv_path=self.fwd_csv_path,
            output_model_path=self.model_json_path,
            min_samples=100
        )
        self.assertIsNotNone(res)
        self.assertTrue(os.path.exists(self.model_json_path))
        self.assertEqual(res["train_samples"], 120)
        self.assertIn("cv_roc_auc", res["metrics"])

        # Test MetaLabeler in TRAINED_ML mode
        settings = AISettings()
        ml_labeler = MetaLabeler(ai_settings=settings, model_path=self.model_json_path)
        self.assertEqual(ml_labeler.model_mode, "TRAINED_ML")

        test_feats = {
            "range_x_atr_h1": 1.5,
            "adx_h1": 35.0,
            "m15_body_to_range": 0.85
        }
        p_win = ml_labeler.predict_success_probability(test_feats)
        self.assertTrue(0.05 <= p_win <= 0.95)
        allow, prob_out, risk_mult = ml_labeler.filter_trade(test_feats)
        self.assertIsInstance(allow, bool)

        # Test MetaLabeler fallback in HEURISTIC_WARMUP mode when model file absent
        non_existent_path = os.path.join(self.temp_dir, "missing_model.json")
        warmup_labeler = MetaLabeler(ai_settings=settings, model_path=non_existent_path)
        self.assertEqual(warmup_labeler.model_mode, "HEURISTIC_WARMUP")
        h_prob = warmup_labeler.predict_success_probability(test_feats)
        self.assertTrue(0.10 <= h_prob <= 0.95)

    # =========================================================================
    # 6. SESSION REPORTER: FORWARD TEST DATA IN HTML
    # =========================================================================

    def test_session_reporter_forward_telemetry(self):
        from unittest.mock import patch
        with patch("engine.session_reporter.mt5") as mock_mt5:
            mock_mt5.initialize.return_value = False
            reporter = TitanSessionReporter(
                db_path=os.path.join(self.temp_dir, "metrics.db"),
                forward_db_path=self.fwd_db_path
            )
            reporter.desktop_path = os.path.join(self.temp_dir, "report.html")

            # Generate report
            html = reporter.generate_html_report()
            self.assertTrue(os.path.exists(reporter.desktop_path))
            self.assertIn("LONG-TERM FORWARD-TEST MATURITY", html)
            self.assertIn("Annualized Sharpe", html)
            self.assertIn("Peak Max Drawdown", html)
            self.assertNotIn("DEMO #113182919", html)
            self.assertNotIn("Baseline: $100,000.00 USD", html)

    # =========================================================================
    # 7. BACKTEST ENGINE: SHARPE, SORTINO, CALMAR COMPUTATION
    # =========================================================================

    def test_backtest_engine_metrics_calculation(self):
        engine = BacktestEngine()
        sim_trades = [
            {"pnl_usd": 500.0, "pnl_r": 1.5, "bars_held": 10},
            {"pnl_usd": 750.0, "pnl_r": 2.0, "bars_held": 8},
            {"pnl_usd": -300.0, "pnl_r": -1.0, "bars_held": 5},
            {"pnl_usd": 600.0, "pnl_r": 1.8, "bars_held": 12},
            {"pnl_usd": -250.0, "pnl_r": -0.8, "bars_held": 4},
            {"pnl_usd": 900.0, "pnl_r": 2.4, "bars_held": 15},
        ]
        metrics = engine._calculate_metrics(sim_trades, initial=10000.0, final=12200.0, peak=12200.0)

        self.assertIn("sharpe_ratio", metrics)
        self.assertIn("sortino_ratio", metrics)
        self.assertIn("calmar_ratio", metrics)
        self.assertGreater(metrics["sharpe_ratio"], 0.0)
        self.assertGreater(metrics["sortino_ratio"], 0.0)
        self.assertEqual(metrics["total_trades"], 6)


if __name__ == "__main__":
    unittest.main()
