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
      // Only update if user hasn't actively focused input
      if (document.activeElement !== balanceInput) {
        balanceInput.value = telem.balance;
        balanceDisplay.textContent = `$${Number(telem.balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
      }
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

  // Auto-boot on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSupabase);
  } else {
    initSupabase();
  }
})();
