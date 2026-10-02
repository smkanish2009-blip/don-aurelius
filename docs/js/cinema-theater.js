/**
 * DON AURELIUS • CINEMATIC AVATAR-GRADE MT5 INSTALLATION THEATER & HOLOGRAPHIC WALKTHROUGH
 * Engineered with 60 FPS Canvas Motion Graphics, Web Audio Sound Synthesis,
 * and 4-Chapter Interactive Holographic Onboarding by SM.KANISH.
 */

(function () {
  'use strict';

  // --- Sound Synthesizer (Zero external dependencies, pure Web Audio API) ---
  class SoundFX {
    constructor() {
      this.ctx = null;
      this.isMuted = true; // Default muted to respect browser autoplay policies
    }

    init() {
      if (!this.ctx && (window.AudioContext || window.webkitAudioContext)) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        this.ctx = new AudioCtx();
      }
      if (this.ctx && this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
    }

    playTone(freq, type = 'sine', duration = 0.12, gainLevel = 0.05) {
      if (this.isMuted) return;
      this.init();
      if (!this.ctx) return;

      try {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = type;
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

        gain.gain.setValueAtTime(gainLevel, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + duration);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start();
        osc.stop(this.ctx.currentTime + duration);
      } catch (e) {
        // Audio policy ignore
      }
    }

    playClick() {
      this.playTone(1800, 'sine', 0.04, 0.04);
    }

    playTransition() {
      if (this.isMuted) return;
      this.init();
      if (!this.ctx) return;
      try {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(400, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(1200, this.ctx.currentTime + 0.25);
        gain.gain.setValueAtTime(0.04, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + 0.25);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.25);
      } catch (e) {}
    }

    playLaserPulse() {
      this.playTone(950, 'sawtooth', 0.08, 0.03);
    }
  }

  const sfx = new SoundFX();

  // --- Chapter Metadata ---
  const CHAPTERS = [
    {
      id: 1,
      title: "BINARY DEPLOYMENT & MT5 INGESTION",
      badge: "STEP 01 / 04",
      sub: "Drop Don_Aurelius.ex5 directly into the MQL5 Experts Navigator tree onto Gold M15.",
      durationSec: 20,
      color: "#f5c542" // Gold
    },
    {
      id: 2,
      title: "SECURITY CLEARANCE & ALGO PROTOCOL",
      badge: "STEP 02 / 04",
      sub: "Enable 'Allow Algorithmic Trading', authorize DLL calls & whitelist Telegram API endpoints.",
      durationSec: 20,
      color: "#00f0ff" // Cyan
    },
    {
      id: 3,
      title: "4-AGENT NEURAL WAR ROOM SYNCHRONIZATION",
      badge: "STEP 03 / 04",
      sub: "Hawk, Radar, Predator & Inquisitor execute intermarket scans for unanimous 4/4 buy lock.",
      durationSec: 20,
      color: "#10b981" // Emerald
    },
    {
      id: 4,
      title: "PRECISION EXECUTION & 24/7 CLOUD WARP",
      badge: "STEP 04 / 04",
      sub: "Server-side trailing stops (+25 pips), News Shield freeze & 1ms MQL5 VPS cloud deployment.",
      durationSec: 20,
      color: "#a855f7" // Purple
    }
  ];

  const TOTAL_DURATION_SEC = 80;

  // --- Theater Controller State ---
  let canvas, ctx;
  let currentChapterIndex = 0;
  let currentTimeSec = 0;
  let isPlaying = true;
  let animationFrameId = null;
  let lastTimestamp = 0;
  let particles = [];

  // --- Particle System for Avatar Bioluminescence ---
  function initParticles(w, h) {
    particles = [];
    const count = 45;
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        radius: Math.random() * 2 + 0.6,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        alpha: Math.random() * 0.6 + 0.2,
        color: Math.random() > 0.5 ? '#00f0ff' : '#f5c542'
      });
    }
  }

  function updateAndDrawParticles(w, h) {
    ctx.save();
    for (let p of particles) {
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0) p.x = w;
      if (p.x > w) p.x = w;
      if (p.y < 0) p.y = h;
      if (p.y > h) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.alpha;
      ctx.shadowBlur = 8;
      ctx.shadowColor = p.color;
      ctx.fill();
    }
    ctx.restore();
  }

  // --- Scene Renderers for Each Chapter ---

  // Chapter 1: 3D Holographic Laptop & MT5 Navigator Injection
  function renderChapter1(w, h, progress) {
    const cx = w / 2;
    const cy = h / 2;

    // 1. Draw 3D Isometric Hologram Base Grid
    ctx.save();
    ctx.strokeStyle = 'rgba(0, 240, 255, 0.15)';
    ctx.lineWidth = 1;
    for (let i = -180; i <= 180; i += 30) {
      ctx.beginPath();
      ctx.moveTo(cx + i, cy + 120);
      ctx.lineTo(cx + i * 2, cy + 180);
      ctx.stroke();
    }

    // 2. Draw Laptop Base & Screen Wireframe
    ctx.strokeStyle = 'rgba(245, 197, 66, 0.6)';
    ctx.lineWidth = 2;
    ctx.shadowBlur = 12;
    ctx.shadowColor = 'rgba(245, 197, 66, 0.4)';

    // Laptop Base
    ctx.beginPath();
    ctx.moveTo(cx - 160, cy + 100);
    ctx.lineTo(cx + 160, cy + 100);
    ctx.lineTo(cx + 200, cy + 140);
    ctx.lineTo(cx - 200, cy + 140);
    ctx.closePath();
    ctx.fillStyle = 'rgba(10, 15, 26, 0.7)';
    ctx.fill();
    ctx.stroke();

    // Trackpad
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.strokeRect(cx - 40, cy + 115, 80, 20);

    // Screen Hologram (Floating upwards)
    ctx.strokeStyle = 'rgba(0, 240, 255, 0.8)';
    ctx.shadowColor = 'rgba(0, 240, 255, 0.6)';
    ctx.strokeRect(cx - 170, cy - 130, 340, 210);
    ctx.fillStyle = 'rgba(3, 7, 18, 0.85)';
    ctx.fillRect(cx - 170, cy - 130, 340, 210);

    // Header bar of MT5
    ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
    ctx.fillRect(cx - 170, cy - 130, 340, 24);
    ctx.fillStyle = '#f5c542';
    ctx.font = '600 10px JetBrains Mono, monospace';
    ctx.fillText('MetaTrader 5 • Terminal #10434714118 • XAUUSD (M15)', cx - 160, cy - 114);

    // Left: Navigator Window
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.strokeRect(cx - 165, cy - 100, 100, 175);
    ctx.fillStyle = '#94a3b8';
    ctx.font = '500 8.5px JetBrains Mono, monospace';
    ctx.fillText('📁 Expert Advisors', cx - 158, cy - 85);

    // Glowing Don_Aurelius.ex5 item in navigator
    const itemX = cx - 155;
    const itemY = cy - 65;
    ctx.fillStyle = 'rgba(245, 197, 66, 0.2)';
    ctx.fillRect(itemX - 4, itemY - 10, 92, 16);
    ctx.fillStyle = '#fcd34d';
    ctx.font = '700 9px JetBrains Mono, monospace';
    ctx.fillText('⚡ Don_Aurelius', itemX, itemY + 2);

    // Right: XAUUSD Chart Candlesticks Mockup
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.strokeRect(cx - 60, cy - 100, 225, 175);
    // Draw decorative candles
    const candleData = [
      { x: cx - 40, o: cy - 20, c: cy - 50, h: cy - 60, l: cy - 10, up: true },
      { x: cx - 15, o: cy - 50, c: cy - 40, h: cy - 65, l: cy - 35, up: false },
      { x: cx + 10, o: cy - 40, c: cy - 75, h: cy - 80, l: cy - 30, up: true },
      { x: cx + 35, o: cy - 75, c: cy - 60, h: cy - 85, l: cy - 55, up: false },
      { x: cx + 60, o: cy - 60, c: cy - 88, h: cy - 95, l: cy - 50, up: true },
      { x: cx + 85, o: cy - 88, c: cy - 92, h: cy - 100, l: cy - 80, up: true },
      { x: cx + 110, o: cy - 92, c: cy - 70, h: cy - 105, l: cy - 65, up: false },
      { x: cx + 135, o: cy - 70, c: cy - 85, h: cy - 90, l: cy - 60, up: true }
    ];

    for (let c of candleData) {
      ctx.strokeStyle = c.up ? '#10b981' : '#ef4444';
      ctx.fillStyle = c.up ? '#10b981' : '#ef4444';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(c.x, c.h);
      ctx.lineTo(c.x, c.l);
      ctx.stroke();
      ctx.fillRect(c.x - 4, Math.min(c.o, c.c), 8, Math.max(Math.abs(c.c - c.o), 3));
    }

    // 3. Dynamic Drag & Drop Animation (From Navigator to Chart)
    const dragT = (progress * 2) % 1; // Loops twice per chapter
    const startX = itemX + 40;
    const startY = itemY;
    const targetX = cx + 45;
    const targetY = cy - 40;

    const curX = startX + (targetX - startX) * dragT;
    const curY = startY + (targetY - startY) * dragT - Math.sin(dragT * Math.PI) * 35;

    // Laser particle trail
    ctx.strokeStyle = 'rgba(245, 197, 66, 0.4)';
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.quadraticCurveTo(cx, cy - 80, curX, curY);
    ctx.stroke();
    ctx.setLineDash([]);

    // Floating Dragged Icon
    ctx.beginPath();
    ctx.arc(curX, curY, 14, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(245, 197, 66, 0.25)';
    ctx.strokeStyle = '#f5c542';
    ctx.lineWidth = 2;
    ctx.shadowBlur = 18;
    ctx.shadowColor = '#f5c542';
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#ffffff';
    ctx.font = '700 10px JetBrains Mono, monospace';
    ctx.textAlign = 'center';
    ctx.fillText('EA', curX, curY + 3.5);

    // Magnetic shockwave at drop target
    if (dragT > 0.85) {
      const ringScale = (dragT - 0.85) * 6;
      ctx.beginPath();
      ctx.arc(targetX, targetY, ringScale * 25, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(16, 185, 129, ${1 - ringScale})`;
      ctx.lineWidth = 2.5;
      ctx.stroke();
    }

    ctx.restore();
  }

  // Chapter 2: Security Clearance & Algo Trading Protocol
  function renderChapter2(w, h, progress) {
    const cx = w / 2;
    const cy = h / 2;

    ctx.save();

    // 3D Glass Dialog Modal
    ctx.strokeStyle = 'rgba(0, 240, 255, 0.8)';
    ctx.fillStyle = 'rgba(6, 11, 25, 0.92)';
    ctx.lineWidth = 2;
    ctx.shadowBlur = 24;
    ctx.shadowColor = 'rgba(0, 240, 255, 0.35)';

    const mw = 360;
    const mh = 220;
    ctx.strokeRect(cx - mw / 2, cy - mh / 2, mw, mh);
    ctx.fillRect(cx - mw / 2, cy - mh / 2, mw, mh);

    // Modal Header
    ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
    ctx.fillRect(cx - mw / 2, cy - mh / 2, mw, 30);
    ctx.fillStyle = '#f5c542';
    ctx.font = '700 11px JetBrains Mono, monospace';
    ctx.textAlign = 'left';
    ctx.fillText('🛡️ EA SETTINGS: DON AURELIUS • PROTOCOL ARMOR', cx - mw / 2 + 14, cy - mh / 2 + 19);

    // Tabs
    ctx.fillStyle = '#94a3b8';
    ctx.font = '600 10px JetBrains Mono, monospace';
    ctx.fillText('[Common]', cx - mw / 2 + 20, cy - mh / 2 + 50);
    ctx.fillText('Inputs', cx - mw / 2 + 90, cy - mh / 2 + 50);

    // Toggle 1: Allow Algorithmic Trading
    const t1Active = progress > 0.2;
    drawToggleRow(cx - mw / 2 + 20, cy - mh / 2 + 80, 'Allow Algorithmic Trading', t1Active, '#10b981');

    // Toggle 2: Allow DLL Imports
    const t2Active = progress > 0.45;
    drawToggleRow(cx - mw / 2 + 20, cy - mh / 2 + 115, 'Allow DLL Imports & C-API Bridge', t2Active, '#00f0ff');

    // Toggle 3: Telegram WebRequest HTTPS Whitelist
    const t3Active = progress > 0.7;
    drawToggleRow(cx - mw / 2 + 20, cy - mh / 2 + 150, 'Telegram WebRequest API Whitelist', t3Active, '#f5c542');

    // Bottom Action Button: "INITIALIZE SYSTEM"
    const btnY = cy + mh / 2 - 34;
    ctx.fillStyle = progress > 0.85 ? 'rgba(16, 185, 129, 0.3)' : 'rgba(255, 255, 255, 0.05)';
    ctx.strokeStyle = progress > 0.85 ? '#10b981' : 'rgba(255, 255, 255, 0.2)';
    ctx.strokeRect(cx - 70, btnY, 140, 24);
    ctx.fillRect(cx - 70, btnY, 140, 24);
    ctx.fillStyle = progress > 0.85 ? '#34d399' : '#94a3b8';
    ctx.font = '700 10px JetBrains Mono, monospace';
    ctx.textAlign = 'center';
    ctx.fillText(progress > 0.85 ? '✓ PROTOCOL AUTHORIZED' : 'STANDBY LOCK', cx, btnY + 16);

    ctx.restore();
  }

  function drawToggleRow(x, y, label, isActive, color) {
    ctx.fillStyle = '#ffffff';
    ctx.font = '500 10px JetBrains Mono, monospace';
    ctx.textAlign = 'left';
    ctx.fillText(label, x, y + 12);

    // Switch Track
    const swX = x + 250;
    ctx.fillStyle = isActive ? color : 'rgba(255, 255, 255, 0.15)';
    ctx.beginPath();
    ctx.roundRect(swX, y, 42, 18, 9);
    ctx.fill();

    // Switch Knob
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    const knobX = isActive ? swX + 32 : swX + 10;
    ctx.arc(knobX, y + 9, 7, 0, Math.PI * 2);
    ctx.fill();
  }

  // Chapter 3: 4-Agent Neural War Room Synchronization
  function renderChapter3(w, h, progress) {
    const cx = w / 2;
    const cy = h / 2;

    ctx.save();

    // Central Core Node (Unanimous Consensus Hub)
    const corePulse = Math.sin(progress * Math.PI * 6) * 4;
    ctx.beginPath();
    ctx.arc(cx, cy, 38 + corePulse, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(245, 197, 66, 0.18)';
    ctx.strokeStyle = '#f5c542';
    ctx.lineWidth = 2.5;
    ctx.shadowBlur = 24;
    ctx.shadowColor = '#f5c542';
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#ffffff';
    ctx.font = '800 11px JetBrains Mono, monospace';
    ctx.textAlign = 'center';
    ctx.fillText('4/4 UNANIMOUS', cx, cy - 2);
    ctx.fillStyle = '#34d399';
    ctx.font = '700 10px JetBrains Mono, monospace';
    ctx.fillText('A+ SETUP', cx, cy + 12);

    // 4 Orbiting Agent Nodes
    const agents = [
      { name: '🦅 HAWK', role: 'DXY & Yields', angle: -Math.PI / 4, color: '#38bdf8' },
      { name: '📡 RADAR', role: 'Asian Range', angle: Math.PI / 4, color: '#f5c542' },
      { name: '🐅 PREDATOR', role: 'FVG & Sweeps', angle: (3 * Math.PI) / 4, color: '#10b981' },
      { name: '⚔️ INQUISITOR', role: 'Spread Auditor', angle: -(3 * Math.PI) / 4, color: '#e879f9' }
    ];

    const dist = 135;

    agents.forEach((ag, idx) => {
      const ax = cx + Math.cos(ag.angle) * dist;
      const ay = cy + Math.sin(ag.angle) * dist;

      // Laser energy beams connecting to central core
      ctx.strokeStyle = ag.color;
      ctx.lineWidth = 1.5;
      ctx.shadowBlur = 10;
      ctx.shadowColor = ag.color;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(ax, ay);
      ctx.stroke();

      // Laser pulse traveling along line
      const pulseT = ((progress * 3 + idx * 0.25) % 1);
      const px = ax + (cx - ax) * pulseT;
      const py = ay + (cy - ay) * pulseT;
      ctx.beginPath();
      ctx.arc(px, py, 4, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.fill();

      // Agent Node Card
      ctx.fillStyle = 'rgba(6, 11, 25, 0.88)';
      ctx.strokeStyle = ag.color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(ax - 55, ay - 24, 110, 48, 12);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#ffffff';
      ctx.font = '700 10.5px JetBrains Mono, monospace';
      ctx.textAlign = 'center';
      ctx.fillText(ag.name, ax, ay - 4);

      ctx.fillStyle = '#94a3b8';
      ctx.font = '500 8.5px JetBrains Mono, monospace';
      ctx.fillText(ag.role, ax, ay + 12);
    });

    ctx.restore();
  }

  // Chapter 4: Sub-millisecond Execution & 24/7 Cloud Warping
  function renderChapter4(w, h, progress) {
    const cx = w / 2;
    const cy = h / 2;

    ctx.save();

    // 1. Chart Execution Stream
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
    ctx.lineWidth = 1;
    ctx.strokeRect(cx - 180, cy - 110, 360, 160);
    ctx.fillStyle = 'rgba(3, 7, 18, 0.85)';
    ctx.fillRect(cx - 180, cy - 110, 360, 160);

    // Price Chart Line
    ctx.beginPath();
    ctx.strokeStyle = '#f5c542';
    ctx.lineWidth = 2;
    ctx.moveTo(cx - 160, cy);
    ctx.lineTo(cx - 100, cy - 20);
    ctx.lineTo(cx - 40, cy - 10);
    ctx.lineTo(cx + 20, cy - 45); // Entry break
    ctx.lineTo(cx + 80, cy - 70); // Rocket up
    ctx.lineTo(cx + 140, cy - 90);
    ctx.stroke();

    // Entry Buy Tag
    ctx.fillStyle = '#10b981';
    ctx.beginPath();
    ctx.roundRect(cx + 10, cy - 65, 75, 20, 6);
    ctx.fill();
    ctx.fillStyle = '#ffffff';
    ctx.font = '700 9px JetBrains Mono, monospace';
    ctx.textAlign = 'center';
    ctx.fillText('BUY 2664.00', cx + 47, cy - 51);

    // Trailing Stop Loss Line
    const trailY = cy - 25 - (progress * 30);
    ctx.strokeStyle = '#ef4444';
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(cx - 160, trailY);
    ctx.lineTo(cx + 160, trailY);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = '#ef4444';
    ctx.font = '700 8.5px JetBrains Mono, monospace';
    ctx.textAlign = 'right';
    ctx.fillText('TRAILING STOP (+25 PIPS SECURED)', cx + 160, trailY - 4);

    // 2. 24/7 Cloud VPS Warping Banner (Below Chart)
    const vpsY = cy + 70;
    ctx.fillStyle = 'rgba(16, 185, 129, 0.15)';
    ctx.strokeStyle = 'rgba(16, 185, 129, 0.4)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.roundRect(cx - 180, vpsY, 360, 45, 12);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#34d399';
    ctx.font = '700 11px JetBrains Mono, monospace';
    ctx.textAlign = 'left';
    ctx.fillText('☁️ MQL5 VIRTUAL SERVER ACTIVE • 0.8ms PING', cx - 165, vpsY + 20);

    ctx.fillStyle = '#94a3b8';
    ctx.font = '500 8.5px JetBrains Mono, monospace';
    ctx.fillText('Trading 24/7/365 with laptop 100% turned off & unplugged.', cx - 165, vpsY + 36);

    ctx.restore();
  }

  // --- Main Animation Loop ---
  function animate(timestamp) {
    if (!lastTimestamp) lastTimestamp = timestamp;
    const deltaSec = (timestamp - lastTimestamp) / 1000;
    lastTimestamp = timestamp;

    if (isPlaying) {
      currentTimeSec += deltaSec;
      if (currentTimeSec >= TOTAL_DURATION_SEC) {
        currentTimeSec = 0; // Loop seamlessly
      }
    }

    // Determine current chapter from time
    currentChapterIndex = Math.floor(currentTimeSec / 20) % CHAPTERS.length;
    const currentChapter = CHAPTERS[currentChapterIndex];
    const chapterTime = currentTimeSec % 20;
    const chapterProgress = chapterTime / 20;

    // Render Canvas Frame
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    // Background Cyber Grid
    ctx.fillStyle = '#050811';
    ctx.fillRect(0, 0, w, h);

    // Ambient Avatar Bioluminescent Fog
    const grad = ctx.createRadialGradient(w / 2, h / 2, 40, w / 2, h / 2, w / 1.5);
    grad.addColorStop(0, 'rgba(0, 240, 255, 0.08)');
    grad.addColorStop(0.5, 'rgba(245, 197, 66, 0.04)');
    grad.addColorStop(1, 'rgba(3, 7, 18, 0.95)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    // Particles
    updateAndDrawParticles(w, h);

    // Render Active Chapter Graphics
    if (currentChapterIndex === 0) renderChapter1(w, h, chapterProgress);
    else if (currentChapterIndex === 1) renderChapter2(w, h, chapterProgress);
    else if (currentChapterIndex === 2) renderChapter3(w, h, chapterProgress);
    else if (currentChapterIndex === 3) renderChapter4(w, h, chapterProgress);

    // Update UI HUD Text & Timecode
    updateUI(currentChapter, chapterProgress);

    animationFrameId = requestAnimationFrame(animate);
  }

  function updateUI(chapter, chapterProgress) {
    // Scrubber fill
    const totalProgressPct = (currentTimeSec / TOTAL_DURATION_SEC) * 100;
    const scrubberBar = document.getElementById('cinema-progress-fill');
    if (scrubberBar) {
      scrubberBar.style.width = `${totalProgressPct}%`;
    }

    // Timecode
    const tcElem = document.getElementById('cinema-timecode');
    if (tcElem) {
      const curM = Math.floor(currentTimeSec / 60);
      const curS = Math.floor(currentTimeSec % 60);
      const totM = Math.floor(TOTAL_DURATION_SEC / 60);
      const totS = Math.floor(TOTAL_DURATION_SEC % 60);
      tcElem.textContent = `${String(curM).padStart(2, '0')}:${String(curS).padStart(2, '0')} / ${String(totM).padStart(2, '0')}:${String(totS).padStart(2, '0')}`;
    }

    // HUD Chapter Header
    const hudBadge = document.getElementById('cinema-hud-badge');
    const hudTitle = document.getElementById('cinema-hud-title');
    const hudSub = document.getElementById('cinema-hud-sub');
    if (hudBadge) hudBadge.textContent = chapter.badge;
    if (hudTitle) hudTitle.textContent = chapter.title;
    if (hudSub) hudSub.textContent = chapter.sub;

    // Chapter Pill Highlight
    document.querySelectorAll('.theater-chapter-pill').forEach((pill, idx) => {
      if (idx === currentChapterIndex) {
        pill.classList.add('active');
      } else {
        pill.classList.remove('active');
      }
    });

    // Step Cards Highlight
    document.querySelectorAll('.theater-step-card').forEach((card, idx) => {
      if (idx === currentChapterIndex) {
        card.classList.add('active');
      } else {
        card.classList.remove('active');
      }
    });
  }

  // --- Theater Initialization ---
  function initTheater() {
    canvas = document.getElementById('cinema-theater-canvas');
    if (!canvas) return;
    ctx = canvas.getContext('2d');

    // Resize Handler for crisp Retina display
    function resizeCanvas() {
      const rect = canvas.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      initParticles(rect.width, rect.height);
    }

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    // Controls: Play / Pause
    const playBtn = document.getElementById('btn-cinema-play');
    if (playBtn) {
      playBtn.addEventListener('click', () => {
        isPlaying = !isPlaying;
        playBtn.textContent = isPlaying ? '⏸ PAUSE' : '▶ PLAY';
        sfx.playClick();
      });
    }

    // Controls: Audio Mute / Unmute
    const audioBtn = document.getElementById('btn-cinema-audio');
    if (audioBtn) {
      audioBtn.addEventListener('click', () => {
        sfx.init();
        sfx.isMuted = !sfx.isMuted;
        audioBtn.textContent = sfx.isMuted ? '🔇 AUDIO OFF' : '🔊 AUDIO ON';
        audioBtn.classList.toggle('active', !sfx.isMuted);
        if (!sfx.isMuted) sfx.playTransition();
      });
    }

    // Chapter Pills Click
    document.querySelectorAll('.theater-chapter-pill').forEach((pill, idx) => {
      pill.addEventListener('click', () => {
        currentTimeSec = idx * 20;
        currentChapterIndex = idx;
        sfx.playTransition();
      });
    });

    // Step Cards Click
    document.querySelectorAll('.theater-step-card').forEach((card, idx) => {
      card.addEventListener('click', () => {
        currentTimeSec = idx * 20;
        currentChapterIndex = idx;
        sfx.playTransition();
      });
    });

    // Scrubber Click & Seek
    const scrubberTrack = document.getElementById('cinema-scrubber-track');
    if (scrubberTrack) {
      scrubberTrack.addEventListener('click', (e) => {
        const rect = scrubberTrack.getBoundingClientRect();
        const pos = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        currentTimeSec = pos * TOTAL_DURATION_SEC;
        sfx.playClick();
      });
    }

    // Prompt Drawer Modal Toggle
    const promptModalBtn = document.getElementById('btn-open-higgsfield-prompts');
    const promptModal = document.getElementById('higgsfield-prompts-modal');
    const promptCloseBtn = document.getElementById('btn-close-higgsfield-prompts');

    if (promptModalBtn && promptModal) {
      promptModalBtn.addEventListener('click', () => {
        promptModal.classList.add('active');
        sfx.playClick();
      });
    }

    if (promptCloseBtn && promptModal) {
      promptCloseBtn.addEventListener('click', () => {
        promptModal.classList.remove('active');
        sfx.playClick();
      });
    }

    // Copy Prompt Buttons
    document.querySelectorAll('.btn-copy-prompt').forEach((btn) => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-target');
        const textElem = document.getElementById(targetId);
        if (textElem) {
          navigator.clipboard.writeText(textElem.innerText || textElem.textContent).then(() => {
            const originalText = btn.textContent;
            btn.textContent = '✓ COPIED!';
            sfx.playLaserPulse();
            setTimeout(() => {
              btn.textContent = originalText;
            }, 1800);
          });
        }
      });
    });

    // Start loop
    animationFrameId = requestAnimationFrame(animate);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheater);
  } else {
    initTheater();
  }
})();
