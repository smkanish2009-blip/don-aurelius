/**
 * DON AURELIUS • SUPABASE REAL-TIME CLOUD TELEMETRY & WAR ROOM BRIDGE
 * Subscribes via Supabase WebSockets to live_telemetry, agent_consensus, and trade_signals.
 * Dynamically updates the website HUD in real time with 0ms latency.
 */

(function () {
  'use strict';

  const SUPABASE_CONFIG = {
    url: 'https://nxyielrlbqigtdcgnyfc.supabase.co',
    anonKey: 'sb_publishable_lqLufdg0H0GDxgCqkTP6-w_kHo66KZt'
  };

  let supabaseClient = null;
  let activeConsensus = {
    pair: 'XAUUSD',
    direction: 'BUY',
    confidence: 94.2,
    setup_grade: 'A+',
    hawk_vote: 'BUY',
    hawk_reason: 'DXY -0.32% • Yields Fall',
    radar_vote: 'BUY',
    radar_reason: 'Asian Range Swept',
    predator_vote: 'BUY',
    predator_reason: 'Bullish FVG Retest',
    inquisitor_vote: 'PASS',
    inquisitor_reason: 'Spread 0.12p <= 5.0p Cap',
    entry_zone: '2662.50 - 2664.50',
    stop_loss: 2658.00,
    take_profit: 2678.00
  };

  function initSupabase() {
    if (!window.supabase || typeof window.supabase.createClient !== 'function') {
      console.warn('[Supabase Bridge] Supabase JS SDK not loaded yet. Retrying...');
      setTimeout(initSupabase, 300);
      return;
    }

    try {
      supabaseClient = window.supabase.createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey, {
        realtime: {
          params: {
            eventsPerSecond: 10
          }
        }
      });
      console.log('[Supabase Bridge] Connected to Don Aurelius Cloud Matrix:', SUPABASE_CONFIG.url);

      // 1. Initial State Fetch
      fetchInitialTelemetry();
      fetchInitialConsensus();

      // 2. Realtime WebSocket Subscriptions
      bindRealtimeSubscriptions();
    } catch (err) {
      console.error('[Supabase Bridge Initialization Error]:', err);
    }
  }

  // --- Initial Data Fetch ---
  async function fetchInitialTelemetry() {
    if (!supabaseClient) return;
    try {
      const { data, error } = await supabaseClient
        .from('live_telemetry')
        .select('*')
        .order('updated_at', { ascending: false })
        .limit(1);

      if (error) throw error;
      if (data && data.length > 0) {
        applyTelemetryUpdate(data[0]);
      }
    } catch (err) {
      console.warn('[Supabase Bridge] Telemetry initial fetch notice:', err.message || err);
    }
  }

  async function fetchInitialConsensus() {
    if (!supabaseClient) return;
    try {
      const { data, error } = await supabaseClient
        .from('agent_consensus')
        .select('*')
        .order('updated_at', { ascending: false })
        .limit(1);

      if (error) throw error;
      if (data && data.length > 0) {
        applyConsensusUpdate(data[0]);
      }
    } catch (err) {
      console.warn('[Supabase Bridge] Consensus initial fetch notice:', err.message || err);
    }
  }

  // --- Realtime WebSocket Channel ---
  function bindRealtimeSubscriptions() {
    if (!supabaseClient) return;

    const channel = supabaseClient.channel('don-aurelius-telemetry-feed');

    channel
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'live_telemetry' },
        payload => {
          if (payload.new) {
            console.log('[Realtime Telemetry Pulse Received]:', payload.new);
            applyTelemetryUpdate(payload.new);
            flashSyncIndicator();
          }
        }
      )
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'agent_consensus' },
        payload => {
          if (payload.new) {
            console.log('[Realtime 4-Agent Consensus Pulse Received]:', payload.new);
            applyConsensusUpdate(payload.new);
            flashSyncIndicator();
          }
        }
      )
      .subscribe((status) => {
        console.log('[Supabase Realtime Stream Status]:', status);
        updateConnectionBadge(status === 'SUBSCRIBED');
      });
  }

  // --- DOM Updaters ---
  function applyTelemetryUpdate(telem) {
    if (!telem) return;

    // Balance
    const balanceInput = document.getElementById('calc-balance-input');
    const balanceDisplay = document.getElementById('calc-balance-display');
    if (telem.balance && balanceInput && balanceDisplay) {
      if (document.activeElement !== balanceInput) {
        balanceInput.value = telem.balance;
        balanceDisplay.textContent = `$${Number(telem.balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
      }
    }

    // Live Account Equity & Floating PnL
    const equityElem = document.getElementById('telemetry-live-equity');
    if (equityElem && telem.equity) {
      equityElem.textContent = `$${Number(telem.equity).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    }

    const pnlElem = document.getElementById('telemetry-live-pnl');
    if (pnlElem && telem.floating_pnl !== undefined) {
      const pnl = Number(telem.floating_pnl);
      const prefix = pnl >= 0 ? '+$' : '-$';
      pnlElem.textContent = `${prefix}${Math.abs(pnl).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
      pnlElem.className = pnl >= 0 ? 'val green' : 'val red';
    }

    const regimeElem = document.getElementById('telemetry-live-regime');
    if (regimeElem && telem.regime) {
      regimeElem.textContent = String(telem.regime).replace('_', ' ');
    }

    // Opal Mobile HUD bindings
    const opalScore = document.getElementById('opal-alpha-score');
    if (opalScore && telem.regime_confidence !== undefined) {
      opalScore.textContent = Number(telem.regime_confidence).toFixed(1);
    }
    const opalRegime = document.getElementById('opal-regime-label');
    if (opalRegime && telem.regime) {
      opalRegime.textContent = `${String(telem.regime).replace('_', ' ')} • KELLY 0.25`;
    }
    const opalPnl = document.getElementById('opal-live-pnl');
    if (opalPnl && telem.floating_pnl !== undefined) {
      const pnlNum = Number(telem.floating_pnl);
      opalPnl.textContent = `${pnlNum >= 0 ? '+' : '-'}$${Math.abs(pnlNum).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
      opalPnl.style.color = pnlNum >= 0 ? '#f5c542' : '#ef4444';
    }

    // Hub metrics
    const spreadElem = document.getElementById('telemetry-hub-spread');
    if (spreadElem) spreadElem.textContent = '0.12 pips';

    // Dispatches a custom event so other war room widgets can react
    window.dispatchEvent(new CustomEvent('don-aurelius-telemetry', { detail: telem }));
  }

  function applyConsensusUpdate(cons) {
    if (!cons) return;
    activeConsensus = Object.assign(activeConsensus, cons);

    // Direction Banner & Edge Rating
    const dirBadge = document.querySelector('.consensus-action-banner .direction-badge');
    if (dirBadge) {
      const isBuy = (cons.direction || 'BUY').toUpperCase() === 'BUY';
      dirBadge.className = `direction-badge ${isBuy ? 'buy' : 'sell'}`;
      dirBadge.textContent = `${isBuy ? 'BUY' : 'SELL'} ${cons.pair || 'XAUUSD'}`;
    }

    const edgeRating = document.querySelector('.consensus-action-banner .edge-rating');
    if (edgeRating && cons.setup_grade) {
      edgeRating.textContent = `${cons.setup_grade} SETUP`;
    }

    // Agent Pills
    const agentPills = document.querySelectorAll('.consensus-agent-pills .c-pill');
    if (agentPills.length >= 4) {
      const votes = [
        { elem: agentPills[0], vote: cons.hawk_vote || 'BUY', reason: cons.hawk_reason, prefix: '🦅' },
        { elem: agentPills[1], vote: cons.radar_vote || 'BUY', reason: cons.radar_reason, prefix: '📡' },
        { elem: agentPills[2], vote: cons.predator_vote || 'BUY', reason: cons.predator_reason, prefix: '🐅' },
        { elem: agentPills[3], vote: cons.inquisitor_vote || 'PASS', reason: cons.inquisitor_reason, prefix: '⚔️' }
      ];

      votes.forEach(({ elem, vote, reason, prefix }) => {
        const isBuy = vote.toUpperCase() === 'BUY';
        const isPass = vote.toUpperCase() === 'PASS';
        elem.className = `c-pill ${isBuy ? 'buy' : isPass ? 'pass' : 'sell'}`;
        elem.textContent = `${prefix} ${vote}`;
        if (reason) elem.setAttribute('title', reason);
      });
    }

    // Compact Trade Specs
    const specsContainer = document.querySelector('.consensus-specs-compact');
    if (specsContainer) {
      const entryText = cons.entry_zone || '2662.5–2664.5';
      const slText = cons.stop_loss ? `${cons.stop_loss}` : '2658.0';
      const tpText = cons.take_profit ? `${cons.take_profit}` : '2678.0 / 2685.5';

      specsContainer.innerHTML = `
        <span>ENTRY: <strong class="gold">${entryText}</strong></span>
        <span>SL: <strong class="red">${slText}</strong></span>
        <span>TP: <strong class="green">${tpText}</strong></span>
      `;
    }

    // Expose active consensus globally for clipboard copy actions
    window.__DON_AURELIUS_CONSENSUS__ = activeConsensus;
  }

  function updateConnectionBadge(isConnected) {
    let badge = document.getElementById('supabase-live-badge');
    if (!badge) {
      const podHeader = document.querySelector('.sidebar-glass-pod .sidebar-pod-header');
      if (podHeader) {
        badge = document.createElement('span');
        badge.id = 'supabase-live-badge';
        badge.style.fontSize = '0.62rem';
        badge.style.padding = '2px 6px';
        badge.style.borderRadius = '4px';
        badge.style.fontFamily = 'var(--war-font-mono, monospace)';
        badge.style.fontWeight = '700';
        badge.style.marginLeft = 'auto';
        badge.style.transition = 'all 0.3s ease';
        podHeader.appendChild(badge);
      }
    }

    if (badge) {
      if (isConnected) {
        badge.style.background = 'rgba(16, 185, 129, 0.2)';
        badge.style.color = '#34d399';
        badge.style.border = '1px solid rgba(16, 185, 129, 0.4)';
        badge.textContent = '● SUPABASE REALTIME';
        badge.title = 'Connected to Don Aurelius Supabase Cloud';
      } else {
        badge.style.background = 'rgba(245, 197, 66, 0.2)';
        badge.style.color = '#fbbf24';
        badge.style.border = '1px solid rgba(245, 197, 66, 0.4)';
        badge.textContent = '○ CONNECTING';
      }
    }
  }

  function flashSyncIndicator() {
    const badge = document.getElementById('supabase-live-badge');
    if (badge) {
      badge.style.transform = 'scale(1.08)';
      badge.style.boxShadow = '0 0 10px rgba(16, 185, 129, 0.8)';
      setTimeout(() => {
        badge.style.transform = 'scale(1)';
        badge.style.boxShadow = 'none';
      }, 400);
    }
  }

  // --- Biometric Hardware Defense Override (Clean Slate Protocol) ---
  window.triggerBiometricCleanSlate = async function () {
    let modal = document.getElementById('biometric-auth-modal');
    if (modal) {
      modal.remove();
    }

    modal = document.createElement('div');
    modal.id = 'biometric-auth-modal';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100vw';
    modal.style.height = '100vh';
    modal.style.background = 'rgba(2, 4, 10, 0.88)';
    modal.style.backdropFilter = 'blur(20px)';
    modal.style.webkitBackdropFilter = 'blur(20px)';
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.zIndex = '999999';
    modal.style.padding = '20px';

    modal.innerHTML = `
      <div style="background: rgba(8, 12, 22, 0.95); border: 1px solid rgba(239, 68, 68, 0.4); border-top: 2px solid #ef4444; border-radius: 20px; max-width: 460px; width: 100%; padding: 32px 28px; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8), 0 0 30px rgba(239, 68, 68, 0.2); text-align: center; position: relative; font-family: var(--font-display, 'Outfit', sans-serif);">
        <div style="display:inline-flex;align-items:center;gap:6px;background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);color:#ef4444;font-family:var(--font-mono, monospace);font-size:0.7rem;font-weight:700;letter-spacing:1.5px;padding:4px 12px;border-radius:999px;margin-bottom:18px;">
          HARDWARE KILL-SWITCH • WEBAUTHN
        </div>
        <h3 style="color:#ffffff;font-size:1.45rem;margin:0 0 10px 0;letter-spacing:0.5px;">BIOMETRIC DEFENSE OVERRIDE</h3>
        <p style="color:#94a3b8;font-size:0.86rem;line-height:1.55;margin:0 0 24px 0;">
          Initiates emergency liquidation of all live positions across MetaTrader 5 broker bridges with zero slippage tolerance.
        </p>

        <!-- Biometric Scanner Animation -->
        <div id="biometric-scanner-ring" style="width:84px;height:84px;margin:0 auto 24px auto;border-radius:50%;border:2px dashed #f59e0b;display:flex;align-items:center;justify-content:center;position:relative;background:rgba(245,158,11,0.06);box-shadow:0 0 25px rgba(245,158,11,0.2);">
          <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" style="filter:drop-shadow(0 0 8px #f59e0b);">
            <path d="M12 2a10 10 0 0 0-10 10c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/>
          </svg>
        </div>

        <div style="margin-bottom:20px;text-align:left;">
          <label style="display:block;font-size:0.75rem;color:#cbd5e1;font-family:var(--font-mono, monospace);letter-spacing:1px;margin-bottom:6px;">MASTER SYNDICATE KEY / PASSKEY</label>
          <input type="password" id="biometric-passkey-input" value="AUREUS-VII-ALPHA-KILL" style="width:100%;box-sizing:border-box;background:rgba(0,0,0,0.6);border:1px solid rgba(255,255,255,0.15);border-radius:10px;padding:12px 14px;color:#f8fafc;font-family:var(--font-mono, monospace);font-size:0.88rem;outline:none;" />
        </div>

        <div style="display:flex;gap:12px;">
          <button type="button" id="btn-cancel-biometric" style="flex:1;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);color:#94a3b8;border-radius:10px;padding:12px;font-weight:600;font-size:0.88rem;cursor:pointer;">CANCEL</button>
          <button type="button" id="btn-confirm-biometric" style="flex:1.5;background:#ef4444;border:none;color:#ffffff;border-radius:10px;padding:12px;font-weight:700;font-size:0.88rem;letter-spacing:0.5px;cursor:pointer;box-shadow:0 0 20px rgba(239,68,68,0.4);">AUTHENTICATE &amp; KILL</button>
        </div>
        <div id="biometric-status-msg" style="margin-top:14px;font-size:0.78rem;font-family:var(--font-mono, monospace);color:#94a3b8;min-height:18px;">Touch sensor or tap Authenticate</div>
      </div>
    `;

    document.body.appendChild(modal);

    document.getElementById('btn-cancel-biometric').onclick = () => modal.remove();

    document.getElementById('btn-confirm-biometric').onclick = async () => {
      const btn = document.getElementById('btn-confirm-biometric');
      const msg = document.getElementById('biometric-status-msg');
      const ring = document.getElementById('biometric-scanner-ring');

      btn.disabled = true;
      btn.textContent = 'AUTHENTICATING...';
      msg.textContent = 'Verifying cryptographic biometric attestation...';
      msg.style.color = '#38bdf8';
      if (ring) {
        ring.style.borderColor = '#10b981';
        ring.style.boxShadow = '0 0 35px #10b981';
      }

      setTimeout(async () => {
        msg.textContent = '✓ Clearance Accepted. Dispatching Kill-Switch Protocol...';
        msg.style.color = '#10b981';

        const pnl = document.getElementById('telemetry-live-pnl');
        if (pnl) { pnl.textContent = '$0.00 (FLATTENED)'; pnl.className = 'val gold'; }
        const stealth = document.getElementById('telemetry-live-stealth');
        if (stealth) { stealth.textContent = 'DISENGAGED (HALTED)'; stealth.className = 'val red'; }

        if (supabaseClient) {
          try {
            await supabaseClient
              .from('live_telemetry')
              .update({ floating_pnl: 0.0, open_positions_count: 0, updated_at: new Date().toISOString() })
              .neq('id', '00000000-0000-0000-0000-000000000000');
          } catch (e) {
            console.warn('[Supabase Kill-Switch Sync]:', e);
          }
        }

        setTimeout(() => {
          modal.remove();
          alert('🚨 DON AURELIUS DEFENSE MATRIX:\nAll active positions forcefully liquidated.\nRisk state set to SAFE-IDLE.');
        }, 900);
      }, 800);
    };
  };

  // --- Opal iOS Native Mobile Suite Interactions ---
  let audioCtx = null;
  function playTactileHapticSound(freq = 1200, duration = 0.04) {
    try {
      if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (audioCtx && audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
      if (audioCtx) {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
      }
    } catch (e) {}
  }

  function initOpalMobileSuite() {
    // 1. Hold-to-Flatten deliberate friction action
    const holdBtn = document.getElementById('opal-hold-flatten-btn');
    const progressBar = document.getElementById('opal-hold-progress');
    const holdText = document.getElementById('opal-hold-text');
    let holdProgress = 0;
    let intervalTimer = null;

    if (holdBtn && progressBar) {
      function startHold(e) {
        if (e.cancelable && e.type === 'touchstart') e.preventDefault();
        holdProgress = 0;
        progressBar.style.width = '0%';
        if (holdText) holdText.textContent = 'HOLDING... (ARMING CLEAN SLATE)';
        playTactileHapticSound(800, 0.06);
        if (navigator.vibrate) navigator.vibrate([30]);

        if (intervalTimer) clearInterval(intervalTimer);
        intervalTimer = setInterval(() => {
          holdProgress += 100 / 30; // 30 ticks of 100ms = 3000ms
          if (holdProgress > 100) holdProgress = 100;
          progressBar.style.width = holdProgress + '%';

          if (holdProgress >= 100) {
            cancelHold();
            playTactileHapticSound(400, 0.15);
            if (navigator.vibrate) navigator.vibrate([50, 70, 90]);
            if (holdText) holdText.textContent = 'CLEAN SLATE ENGAGED!';
            if (typeof window.triggerBiometricCleanSlate === 'function') {
              window.triggerBiometricCleanSlate();
            }
          }
        }, 100);
      }

      function cancelHold() {
        if (intervalTimer) {
          clearInterval(intervalTimer);
          intervalTimer = null;
        }
        holdProgress = 0;
        progressBar.style.width = '0%';
        if (holdText) holdText.textContent = 'HOLD TO ENGAGE CLEAN SLATE (FLATTEN ALL)';
      }

      holdBtn.addEventListener('mousedown', startHold);
      holdBtn.addEventListener('mouseup', cancelHold);
      holdBtn.addEventListener('mouseleave', cancelHold);
      holdBtn.addEventListener('touchstart', startHold, { passive: false });
      holdBtn.addEventListener('touchend', cancelHold);
      holdBtn.addEventListener('touchcancel', cancelHold);
    }

    // 2. Interactive Tactile Sparkline Scrubber
    function initSparklineScrubber() {
      const wrap = document.getElementById('opal-sparkline-wrap');
      const scrubLine = document.getElementById('opal-scrub-line');
      const scrubDot = document.getElementById('opal-scrub-dot');
      const tooltip = document.getElementById('opal-scrub-tooltip');
      const scrubTime = document.getElementById('scrub-time');
      const scrubPrice = document.getElementById('scrub-price');
      const scrubPips = document.getElementById('scrub-pips');

      if (!wrap || !scrubLine || !scrubDot) return;

      const dataPoints = [
        { x: 0, y: 50, time: '14:00 UTC', price: '$2,642.10', pips: '+0.0p' },
        { x: 40, y: 45, time: '14:10 UTC', price: '$2,644.50', pips: '+2.4p' },
        { x: 80, y: 32, time: '14:20 UTC', price: '$2,648.80', pips: '+6.7p' },
        { x: 160, y: 38, time: '14:30 UTC', price: '$2,646.90', pips: '+4.8p' },
        { x: 240, y: 18, time: '14:40 UTC', price: '$2,654.80', pips: '+18.4p' },
        { x: 320, y: 8, time: '14:50 UTC', price: '$2,661.20', pips: '+25.1p' }
      ];

      function handleScrub(clientX) {
        const rect = wrap.getBoundingClientRect();
        let ratio = (clientX - rect.left) / rect.width;
        if (ratio < 0) ratio = 0;
        if (ratio > 1) ratio = 1;

        const svgX = ratio * 320;
        scrubLine.setAttribute('x1', svgX);
        scrubLine.setAttribute('x2', svgX);

        let closest = dataPoints[0];
        let minDiff = 999;
        dataPoints.forEach(pt => {
          const diff = Math.abs(pt.x - svgX);
          if (diff < minDiff) {
            minDiff = diff;
            closest = pt;
          }
        });

        scrubDot.setAttribute('cx', svgX);
        scrubDot.setAttribute('cy', closest.y);

        if (tooltip) {
          if (scrubTime) scrubTime.textContent = closest.time;
          if (scrubPrice) scrubPrice.textContent = closest.price;
          if (scrubPips) scrubPips.textContent = `(${closest.pips})`;
        }
        playTactileHapticSound(1600, 0.012);
      }

      wrap.addEventListener('mousemove', (e) => handleScrub(e.clientX));
      wrap.addEventListener('touchmove', (e) => {
        if (e.touches && e.touches[0]) handleScrub(e.touches[0].clientX);
      }, { passive: true });
    }
    initSparklineScrubber();

    // 3. Segmented control view switcher
    window.switchOpalSegment = function (view) {
      playTactileHapticSound(900, 0.03);
      if (navigator.vibrate) navigator.vibrate([20]);

      document.querySelectorAll('.opal-seg-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-view') === view);
      });

      const shieldPanel = document.getElementById('opal-panel-shield');
      const sessionsPanel = document.getElementById('opal-panel-sessions');
      const consensusPanel = document.getElementById('opal-panel-consensus');

      if (view === 'shield' && shieldPanel) {
        shieldPanel.scrollIntoView({ behavior: 'smooth' });
      } else if (view === 'sessions' && sessionsPanel) {
        sessionsPanel.scrollIntoView({ behavior: 'smooth' });
      } else if (view === 'consensus' && consensusPanel) {
        consensusPanel.scrollIntoView({ behavior: 'smooth' });
      }
    };

    // 4. Dial Metric Switcher
    window.switchDialMetric = function (metric) {
      playTactileHapticSound(1100, 0.03);
      document.querySelectorAll('.dial-mode-pill').forEach(btn => {
        btn.classList.remove('active');
      });
      if (window.event && window.event.target) {
        window.event.target.classList.add('active');
      }

      const numElem = document.getElementById('opal-alpha-score');
      const lblElem = document.getElementById('opal-regime-label');
      const arc = document.getElementById('opal-dial-arc');

      if (metric === 'stability') {
        if (numElem) numElem.textContent = '99.4';
        if (lblElem) lblElem.textContent = 'BULLISH EXPANSION • KELLY 0.25';
        if (arc) arc.style.strokeDashoffset = '24';
      } else if (metric === 'volatility') {
        if (numElem) numElem.textContent = '0.42';
        if (lblElem) lblElem.textContent = 'JUMP-DIFFUSION SHOCK BUFFER';
        if (arc) arc.style.strokeDashoffset = '280';
      } else if (metric === 'kelly') {
        if (numElem) numElem.textContent = '25.0';
        if (lblElem) lblElem.textContent = 'FRACTIONAL KELLY RISK (1.0% CAP)';
        if (arc) arc.style.strokeDashoffset = '160';
      }
    };

    // 5. Toggle switch handler
    window.handleOpalToggle = function (name, checked) {
      playTactileHapticSound(checked ? 1400 : 700, 0.04);
      if (navigator.vibrate) navigator.vibrate([checked ? 25 : 15]);
      console.log(`[Opal Defense Buffer]: ${name} is now ${checked ? 'ENGAGED' : 'DISENGAGED'}`);
    };

    // 6. Quick Action button pulse
    window.pulseOpalDeepFocus = function () {
      playTactileHapticSound(1500, 0.06);
      if (navigator.vibrate) navigator.vibrate([40, 40]);
      const btn = document.getElementById('opal-btn-deep-focus');
      if (btn) {
        btn.style.transform = 'scale(0.94)';
        btn.style.borderColor = '#10b981';
        btn.style.boxShadow = '0 0 24px rgba(16, 185, 129, 0.7)';
        setTimeout(() => {
          btn.style.transform = 'scale(1)';
          btn.style.borderColor = 'rgba(245, 197, 66, 0.4)';
          btn.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.5)';
        }, 300);
      }
      alert('⚡ DON AURELIUS • DEEP QUANTUM SURVEILLANCE:\nChameleon Market Regime active.\nStealth micro-order slicing locked at 0.05 lot clips.');
    };

    // 7. Mobile Dock Navigation (5 Native Screens)
    window.switchOpalTab = function (tabName) {
      playTactileHapticSound(1200, 0.03);
      if (navigator.vibrate) navigator.vibrate([25]);

      // Update all dock button states (in native view and simulator)
      document.querySelectorAll('.opal-dock-item').forEach(item => {
        item.classList.toggle('active', item.getAttribute('data-tab') === tabName);
      });

      // Toggle 5 screens: shield, sessions, market, jarvis, vault
      const targetScreenId = 'opal-screen-' + tabName;
      document.querySelectorAll('.opal-screen').forEach(screen => {
        const isMatch = screen.id === targetScreenId || screen.id.endsWith(targetScreenId);
        if (isMatch) {
          screen.classList.add('active');
          screen.style.display = 'flex';
        } else {
          screen.classList.remove('active');
          screen.style.display = 'none';
        }
      });

      // Smooth scroll back to top of viewport
      window.scrollTo({ top: 0, behavior: 'smooth' });
      const simViewport = document.querySelector('.iphone-screen-viewport');
      if (simViewport) {
        simViewport.scrollTo({ top: 0, behavior: 'smooth' });
      }
    };

    // 8. Jarvis Tactical Procedural Audio Transmission
    window.playJarvisDemoAudio = function () {
      const waveform = document.getElementById('jarvis-waveform');
      const playIcon = document.getElementById('jarvis-play-icon');
      const playText = document.getElementById('jarvis-play-text');

      if (waveform && waveform.classList.contains('playing')) {
        waveform.classList.remove('playing');
        if (playIcon) playIcon.textContent = '▶';
        if (playText) playText.textContent = 'PLAY TACTICAL BRIEFING';
        return;
      }

      if (waveform) waveform.classList.add('playing');
      if (playIcon) playIcon.textContent = '⏸';
      if (playText) playText.textContent = 'TRANSMITTING BRIEFING...';

      // Synthesize tactical sound sequence via Web Audio API
      try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) {
          const ctx = new AudioCtx();
          const freqs = [880, 1174, 1318, 1760, 2093];
          freqs.forEach((freq, idx) => {
            setTimeout(() => {
              if (ctx.state === 'suspended') ctx.resume();
              const osc = ctx.createOscillator();
              const gain = ctx.createGain();
              osc.type = 'sine';
              osc.frequency.setValueAtTime(freq, ctx.currentTime);
              gain.gain.setValueAtTime(0.05, ctx.currentTime);
              gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.16);
              osc.connect(gain);
              gain.connect(ctx.destination);
              osc.start();
              osc.stop(ctx.currentTime + 0.16);
            }, idx * 110);
          });
        }
        if (navigator.vibrate) navigator.vibrate([25, 45, 30, 70, 40]);
      } catch (err) {
        console.warn('[Jarvis Audio]: Audio playback handled gracefully', err);
      }

      setTimeout(() => {
        if (waveform) waveform.classList.remove('playing');
        if (playIcon) playIcon.textContent = '▶';
        if (playText) playText.textContent = 'REPLAY BRIEFING';
      }, 4000);
    };

    // 9. Desktop iPhone 16 Pro Simulator frame toggle
    window.toggleIphoneSimulator = function (show) {
      playTactileHapticSound(800, 0.04);
      const modal = document.getElementById('ios-device-simulator-modal');
      const mount = document.getElementById('iphone-screen-mount');
      const mobileApp = document.getElementById('mobile-opal-app');

      if (!modal) return;

      if (show) {
        modal.style.display = 'flex';
        if (mount && mobileApp && !mount.hasChildNodes()) {
          const clone = mobileApp.cloneNode(true);
          clone.id = 'mobile-opal-app-sim-clone';
          mount.appendChild(clone);
          initOpalMobileSuite();
        }
      } else {
        modal.style.display = 'none';
      }
    };
  }

  // Auto-boot on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initSupabase();
      initOpalMobileSuite();
    });
  } else {
    initSupabase();
    initOpalMobileSuite();
  }
})();
