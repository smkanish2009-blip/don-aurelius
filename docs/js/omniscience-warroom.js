/* ==============================================================================
   DON AURELIUS • OMNISCIENCE TACTICAL COCKPIT & QUANTUM WAR ROOM ENGINE (v5.0)
   Architect: SM.KANISH • Sovereign AI Quantitative Syndicate
   Hardware-Accelerated 120 FPS Procedural WebGL / Canvas / Web Audio Engine
   ============================================================================== */

(function () {
  'use strict';

  /* ============================================================================
     1. Procedural Web Audio Synthesizer (Zero External Dependencies)
     ============================================================================ */
  class OmniscienceAudio {
    constructor() {
      this.ctx = null;
      this.masterGain = null;
      this.enabled = true;
      this.analyser = null;
      this.dataArray = null;
    }

    init() {
      if (this.ctx) return;
      try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        this.ctx = new AudioCtx();
        this.masterGain = this.ctx.createGain();
        this.masterGain.gain.setValueAtTime(0.35, this.ctx.currentTime);

        this.analyser = this.ctx.createAnalyser();
        this.analyser.fftSize = 64;
        this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);

        this.masterGain.connect(this.analyser);
        this.analyser.connect(this.ctx.destination);
      } catch (e) {
        console.warn('Web Audio not supported', e);
      }
    }

    resume() {
      this.init();
      if (this.ctx && this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
    }

    toggle() {
      this.enabled = !this.enabled;
      if (this.masterGain) {
        this.masterGain.gain.setValueAtTime(this.enabled ? 0.35 : 0, this.ctx ? this.ctx.currentTime : 0);
      }
      return this.enabled;
    }

    playClick() {
      if (!this.enabled || !this.ctx) return;
      this.resume();
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(950, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(320, this.ctx.currentTime + 0.04);
      gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
      gain.gain.linearRampToValueAtTime(0.001, this.ctx.currentTime + 0.04);
      osc.connect(gain);
      gain.connect(this.masterGain);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.04);
    }

    playBreach() {
      if (!this.enabled || !this.ctx) return;
      this.resume();
      const now = this.ctx.currentTime;
      // Sub-bass thump
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(140, now);
      osc.frequency.exponentialRampToValueAtTime(32, now + 0.55);
      gain.gain.setValueAtTime(0.5, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.6);
      osc.connect(gain);
      gain.connect(this.masterGain);
      osc.start(now);
      osc.stop(now + 0.6);

      // Pneumatic hiss simulation via filtered buffer
      const bufferSize = this.ctx.sampleRate * 0.4;
      const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = Math.random() * 2 - 1;
      }
      const noise = this.ctx.createBufferSource();
      noise.buffer = buffer;
      const filter = this.ctx.createBiquadFilter();
      filter.type = 'bandpass';
      filter.frequency.setValueAtTime(1200, now);
      filter.frequency.exponentialRampToValueAtTime(400, now + 0.4);
      const noiseGain = this.ctx.createGain();
      noiseGain.gain.setValueAtTime(0.25, now);
      noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
      noise.connect(filter);
      filter.connect(noiseGain);
      noiseGain.connect(this.masterGain);
      noise.start(now);
    }

    playSonar() {
      if (!this.enabled || !this.ctx) return;
      this.resume();
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(1600, now);
      osc.frequency.exponentialRampToValueAtTime(1200, now + 0.35);
      gain.gain.setValueAtTime(0.28, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
      osc.connect(gain);
      gain.connect(this.masterGain);
      osc.start(now);
      osc.stop(now + 0.4);
    }

    playLaser() {
      if (!this.enabled || !this.ctx) return;
      this.resume();
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(2200, now);
      osc.frequency.exponentialRampToValueAtTime(350, now + 0.18);
      gain.gain.setValueAtTime(0.22, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
      osc.connect(gain);
      gain.connect(this.masterGain);
      osc.start(now);
      osc.stop(now + 0.18);
    }

    playProfitChime() {
      if (!this.enabled || !this.ctx) return;
      this.resume();
      const now = this.ctx.currentTime;
      const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
      notes.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(freq, now + idx * 0.08);
        gain.gain.setValueAtTime(0.28, now + idx * 0.08);
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.08 + 0.45);
        osc.connect(gain);
        gain.connect(this.masterGain);
        osc.start(now + idx * 0.08);
        osc.stop(now + idx * 0.08 + 0.45);
      });
    }

    playAlarm() {
      if (!this.enabled || !this.ctx) return;
      this.resume();
      const now = this.ctx.currentTime;
      [0, 0.18, 0.36].forEach((t) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(880, now + t);
        osc.frequency.setValueAtTime(440, now + t + 0.08);
        gain.gain.setValueAtTime(0.2, now + t);
        gain.gain.linearRampToValueAtTime(0.001, now + t + 0.14);
        osc.connect(gain);
        gain.connect(this.masterGain);
        osc.start(now + t);
        osc.stop(now + t + 0.14);
      });
    }

    speak(text) {
      if (!('speechSynthesis' in window)) return;
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.pitch = 0.92;
      utterance.rate = 1.02;
      utterance.volume = 0.95;
      const voices = window.speechSynthesis.getVoices();
      const selected = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Daniel') || v.name.includes('Male')));
      if (selected) utterance.voice = selected;
      window.speechSynthesis.speak(utterance);
    }
  }

  const audio = new OmniscienceAudio();

  /* ============================================================================
     2. Mode 1: Interactive 3D Tactical Planetary Liquidity Globe
     ============================================================================ */
  class TacticalGlobe {
    constructor(canvas, onCitySelect) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      this.onCitySelect = onCitySelect;
      this.rotX = 0.35;
      this.rotY = 0;
      this.velX = 0;
      this.velY = 0.004; // Gentle autonomous rotation
      this.isDragging = false;
      this.lastMouseX = 0;
      this.lastMouseY = 0;
      this.points = [];
      this.arcs = [];
      this.hubs = [
        { name: 'London LBMA', lat: 51.5, lon: -0.12, status: 'OPEN • HIGH LIQUIDITY', spread: '0.9 pips', vol: '$42.8B/day', color: '#f5c542' },
        { name: 'New York COMEX', lat: 40.7, lon: -74.0, status: 'PRE-MARKET ACTIVE', spread: '1.2 pips', vol: '$38.2B/day', color: '#00f0ff' },
        { name: 'Zurich Vaults', lat: 47.4, lon: 8.5, status: 'SETTLEMENT LOCKED', spread: '0.8 pips', vol: '$19.5B/day', color: '#f5c542' },
        { name: 'Tokyo Asia Core', lat: 35.7, lon: 139.7, status: 'SESSION HARVESTED', spread: '1.4 pips', vol: '$22.1B/day', color: '#10b981' },
        { name: 'Shanghai SGE', lat: 31.2, lon: 121.5, status: 'PHYSICAL ARBITRAGE', spread: '+$14.20 premium', vol: '$26.4B/day', color: '#f5c542' }
      ];
      this.hoveredHub = null;
      this.initPoints();
      this.initArcs();
      this.bindEvents();
    }

    initPoints() {
      this.points = [];
      // Fibonacci sphere distribution for uniform 3D Earth point cloud
      const numPoints = 650;
      const phi = Math.PI * (3 - Math.sqrt(5)); // Golden ratio angle
      for (let i = 0; i < numPoints; i++) {
        const y = 1 - (i / (numPoints - 1)) * 2; // y goes from 1 to -1
        const radiusAtY = Math.sqrt(1 - y * y);
        const theta = phi * i;
        const x = Math.cos(theta) * radiusAtY;
        const z = Math.sin(theta) * radiusAtY;
        this.points.push({ x, y, z, lat: Math.asin(y), lon: Math.atan2(z, x) });
      }
    }

    latLonToXYZ(latDeg, lonDeg) {
      const lat = (latDeg * Math.PI) / 180;
      const lon = (lonDeg * Math.PI) / 180;
      return {
        x: Math.cos(lat) * Math.sin(lon),
        y: -Math.sin(lat),
        z: Math.cos(lat) * Math.cos(lon)
      };
    }

    initArcs() {
      // Connect key bullion corridors: London-NY, London-Zurich, Tokyo-Shanghai, Zurich-Shanghai
      this.arcs = [
        { from: this.hubs[0], to: this.hubs[1], progress: 0.1, speed: 0.007 },
        { from: this.hubs[0], to: this.hubs[2], progress: 0.5, speed: 0.010 },
        { from: this.hubs[3], to: this.hubs[4], progress: 0.8, speed: 0.008 },
        { from: this.hubs[2], to: this.hubs[4], progress: 0.3, speed: 0.005 }
      ];
    }

    bindEvents() {
      const start = (x, y) => {
        this.isDragging = true;
        this.lastMouseX = x;
        this.lastMouseY = y;
        this.velX = 0;
        this.velY = 0;
      };
      const move = (x, y) => {
        if (this.isDragging) {
          const dx = x - this.lastMouseX;
          const dy = y - this.lastMouseY;
          this.rotY += dx * 0.006;
          this.rotX += dy * 0.006;
          this.rotX = Math.max(-1.2, Math.min(1.2, this.rotX));
          this.velY = dx * 0.004;
          this.velX = dy * 0.004;
          this.lastMouseX = x;
          this.lastMouseY = y;
        } else {
          this.checkHover(x, y);
        }
      };
      const end = () => {
        this.isDragging = false;
      };

      this.canvas.addEventListener('mousedown', e => start(e.clientX, e.clientY));
      window.addEventListener('mousemove', e => {
        const rect = this.canvas.getBoundingClientRect();
        move(e.clientX - rect.left, e.clientY - rect.top);
      });
      window.addEventListener('mouseup', end);

      this.canvas.addEventListener('touchstart', e => {
        if (e.touches.length === 1) start(e.touches[0].clientX, e.touches[0].clientY);
      }, { passive: true });
      this.canvas.addEventListener('touchmove', e => {
        if (e.touches.length === 1) {
          const rect = this.canvas.getBoundingClientRect();
          move(e.touches[0].clientX - rect.left, e.touches[0].clientY - rect.top);
        }
      }, { passive: true });
      this.canvas.addEventListener('touchend', end);

      this.canvas.addEventListener('click', e => {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        this.handleClick(x, y);
      });
    }

    checkHover(mx, my) {
      const w = this.canvas.width;
      const h = this.canvas.height;
      const radius = Math.min(w, h) * 0.38;
      const cx = w / 2;
      const cy = h / 2;

      let found = null;
      for (const hub of this.hubs) {
        const p = this.latLonToXYZ(hub.lat, hub.lon);
        const rot = this.project3D(p.x, p.y, p.z, radius, cx, cy);
        if (rot.z > 0) { // Front face only
          const dist = Math.hypot(rot.x - mx, rot.y - my);
          if (dist < 18) {
            found = hub;
            break;
          }
        }
      }
      if (found !== this.hoveredHub) {
        this.hoveredHub = found;
        this.canvas.style.cursor = found ? 'pointer' : 'grab';
        if (found) audio.playClick();
      }
    }

    handleClick(mx, my) {
      if (this.hoveredHub) {
        audio.playSonar();
        if (this.onCitySelect) this.onCitySelect(this.hoveredHub);
      }
    }

    project3D(x, y, z, radius, cx, cy) {
      // Rotate around X axis
      const cosX = Math.cos(this.rotX);
      const sinX = Math.sin(this.rotX);
      const y1 = y * cosX - z * sinX;
      const z1 = y * sinX + z * cosX;

      // Rotate around Y axis
      const cosY = Math.cos(this.rotY);
      const sinY = Math.sin(this.rotY);
      const x2 = x * cosY + z1 * sinY;
      const z2 = -x * sinY + z1 * cosY;

      return {
        x: cx + x2 * radius,
        y: cy + y1 * radius,
        z: z2,
        scale: (z2 + 1.6) / 2.6
      };
    }

    render() {
      const ctx = this.ctx;
      const w = this.canvas.width;
      const h = this.canvas.height;
      ctx.clearRect(0, 0, w, h);

      if (!this.isDragging) {
        this.rotY += this.velY;
        this.rotX += this.velX;
        this.velY *= 0.96;
        this.velX *= 0.96;
        if (Math.abs(this.velY) < 0.0015) this.velY = 0.0025; // Continuous gentle drift
      }

      const radius = Math.min(w, h) * 0.36;
      const cx = w / 2;
      const cy = h / 2;

      // Draw Globe Ambient Atmospheres
      const atmGrad = ctx.createRadialGradient(cx, cy, radius * 0.6, cx, cy, radius * 1.25);
      atmGrad.addColorStop(0, 'rgba(0, 240, 255, 0.04)');
      atmGrad.addColorStop(0.7, 'rgba(245, 197, 66, 0.03)');
      atmGrad.addColorStop(1, 'transparent');
      ctx.fillStyle = atmGrad;
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 1.25, 0, Math.PI * 2);
      ctx.fill();

      // Draw Globe Rim Silhouette
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.stroke();

      // Render 3D Point Cloud
      for (const p of this.points) {
        const pr = this.project3D(p.x, p.y, p.z, radius, cx, cy);
        const alpha = Math.max(0.06, (pr.z + 1) / 2);
        ctx.fillStyle = pr.z > 0 ? `rgba(245, 197, 66, ${alpha * 0.85})` : `rgba(255, 255, 255, ${alpha * 0.25})`;
        ctx.beginPath();
        const ptSize = pr.z > 0 ? Math.max(1, 1.8 * pr.scale) : 1;
        ctx.arc(pr.x, pr.y, ptSize, 0, Math.PI * 2);
        ctx.fill();
      }

      // Render Parabolic Liquidity Arcs
      const time = performance.now() * 0.001;
      for (const arc of this.arcs) {
        arc.progress = (arc.progress + arc.speed) % 1;
        const p1 = this.latLonToXYZ(arc.from.lat, arc.from.lon);
        const p2 = this.latLonToXYZ(arc.to.lat, arc.to.lon);

        const r1 = this.project3D(p1.x, p1.y, p1.z, radius, cx, cy);
        const r2 = this.project3D(p2.x, p2.y, p2.z, radius, cx, cy);

        // Control point lifted in 3D space
        const mx = (p1.x + p2.x) * 0.5 * 1.45;
        const my = (p1.y + p2.y) * 0.5 * 1.45;
        const mz = (p1.z + p2.z) * 0.5 * 1.45;
        const rm = this.project3D(mx, my, mz, radius, cx, cy);

        if (r1.z > -0.2 || r2.z > -0.2) {
          ctx.strokeStyle = 'rgba(245, 197, 66, 0.28)';
          ctx.lineWidth = 1.2;
          ctx.beginPath();
          ctx.moveTo(r1.x, r1.y);
          ctx.quadraticCurveTo(rm.x, rm.y, r2.x, r2.y);
          ctx.stroke();

          // Traveling Gold Photon on Arc
          const t = arc.progress;
          const px = (1 - t) * (1 - t) * r1.x + 2 * (1 - t) * t * rm.x + t * t * r2.x;
          const py = (1 - t) * (1 - t) * r1.y + 2 * (1 - t) * t * rm.y + t * t * r2.y;

          ctx.fillStyle = '#00f0ff';
          ctx.shadowColor = '#00f0ff';
          ctx.shadowBlur = 10;
          ctx.beginPath();
          ctx.arc(px, py, 3.5, 0, Math.PI * 2);
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      }

      // Render Bullion Hub Nodes
      for (const hub of this.hubs) {
        const p = this.latLonToXYZ(hub.lat, hub.lon);
        const pr = this.project3D(p.x, p.y, p.z, radius, cx, cy);

        if (pr.z > -0.15) {
          const isHovered = this.hoveredHub === hub;
          const pulse = (Math.sin(time * 4) + 1) / 2;

          // Pulsing Ring
          ctx.strokeStyle = hub.color;
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.arc(pr.x, pr.y, 6 + pulse * 8, 0, Math.PI * 2);
          ctx.stroke();

          // Core Node Dot
          ctx.fillStyle = isHovered ? '#ffffff' : hub.color;
          ctx.shadowColor = hub.color;
          ctx.shadowBlur = 14;
          ctx.beginPath();
          ctx.arc(pr.x, pr.y, isHovered ? 5.5 : 4, 0, Math.PI * 2);
          ctx.fill();
          ctx.shadowBlur = 0;

          // Hub Label
          ctx.font = '600 11px JetBrains Mono, monospace';
          ctx.fillStyle = isHovered ? '#ffffff' : '#cbd5e1';
          ctx.fillText(hub.name, pr.x + 12, pr.y + 4);
        }
      }
    }
  }

  /* ============================================================================
     3. Mode 2: Interactive 3D Neural Synapse Cortex (Aureus Brain)
     ============================================================================ */
  class NeuralSynapse {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      this.rotX = 0.2;
      this.rotY = 0;
      this.mouse = { x: 0, y: 0, active: false };
      this.mode = 'PREDATOR'; // HAWK, PREDATOR, RADAR, INQUISITOR
      this.nodes = [];
      this.pulses = [];
      this.initNodes();
      this.bindEvents();
    }

    initNodes() {
      this.nodes = [];
      const count = 380;
      for (let i = 0; i < count; i++) {
        // Bi-hemispheric ellipsoid distribution
        const hemisphere = Math.random() > 0.5 ? 1 : -1;
        const u = Math.random();
        const v = Math.random();
        const theta = u * 2.0 * Math.PI;
        const phi = Math.acos(2.0 * v - 1.0);
        const r = Math.cbrt(Math.random()); // Even volume density

        const x = r * Math.sin(phi) * Math.cos(theta) * 0.65 + (hemisphere * 0.38);
        const y = r * Math.sin(phi) * Math.sin(theta) * 0.75;
        const z = r * Math.cos(phi) * 0.9;

        this.nodes.push({
          x, y, z,
          ox: x, oy: y, oz: z,
          connections: [],
          activity: Math.random()
        });
      }

      // Calculate nearest neighbors for synaptic axons
      for (let i = 0; i < this.nodes.length; i++) {
        for (let j = i + 1; j < this.nodes.length; j++) {
          const dx = this.nodes[i].x - this.nodes[j].x;
          const dy = this.nodes[i].y - this.nodes[j].y;
          const dz = this.nodes[i].z - this.nodes[j].z;
          const d = Math.hypot(dx, dy, dz);
          if (d < 0.26) {
            this.nodes[i].connections.push(j);
          }
        }
      }
    }

    setMode(mode) {
      this.mode = mode;
      audio.playSonar();
      // Trigger mass synaptic flare
      for (let i = 0; i < 24; i++) {
        const start = Math.floor(Math.random() * this.nodes.length);
        this.triggerPulse(start);
      }
    }

    triggerPulse(startIdx) {
      const node = this.nodes[startIdx];
      if (node && node.connections.length > 0) {
        const targetIdx = node.connections[Math.floor(Math.random() * node.connections.length)];
        this.pulses.push({
          from: startIdx,
          to: targetIdx,
          progress: 0,
          speed: 0.035 + Math.random() * 0.04
        });
      }
    }

    bindEvents() {
      this.canvas.addEventListener('mousemove', e => {
        const rect = this.canvas.getBoundingClientRect();
        this.mouse.x = e.clientX - rect.left;
        this.mouse.y = e.clientY - rect.top;
        this.mouse.active = true;
      });
      this.canvas.addEventListener('mouseleave', () => {
        this.mouse.active = false;
      });
      this.canvas.addEventListener('click', () => {
        audio.playLaser();
        for (let i = 0; i < 8; i++) {
          this.triggerPulse(Math.floor(Math.random() * this.nodes.length));
        }
      });
    }

    render() {
      const ctx = this.ctx;
      const w = this.canvas.width;
      const h = this.canvas.height;
      ctx.clearRect(0, 0, w, h);

      this.rotY += 0.0035;
      const radius = Math.min(w, h) * 0.44;
      const cx = w / 2;
      const cy = h / 2;

      // Color scheme according to active Sentinel Mode
      let themeColor = '#00f0ff';
      let themeGlow = 'rgba(0, 240, 255, 0.4)';
      if (this.mode === 'HAWK') { themeColor = '#f5c542'; themeGlow = 'rgba(245, 197, 66, 0.4)'; }
      else if (this.mode === 'RADAR') { themeColor = '#10b981'; themeGlow = 'rgba(16, 185, 129, 0.4)'; }
      else if (this.mode === 'INQUISITOR') { themeColor = '#ef4444'; themeGlow = 'rgba(239, 68, 68, 0.4)'; }

      // Random spontaneous synaptic pulses
      if (Math.random() < 0.25) {
        this.triggerPulse(Math.floor(Math.random() * this.nodes.length));
      }

      // Rotate & Project Nodes
      const cosY = Math.cos(this.rotY);
      const sinY = Math.sin(this.rotY);
      const projected = [];

      for (let i = 0; i < this.nodes.length; i++) {
        const n = this.nodes[i];
        // Rotate around Y
        const rx = n.x * cosY + n.z * sinY;
        const rz = -n.x * sinY + n.z * cosY;

        // Gravitational cursor warp
        let px = cx + rx * radius;
        let py = cy + n.y * radius;
        if (this.mouse.active) {
          const d = Math.hypot(this.mouse.x - px, this.mouse.y - py);
          if (d < 120) {
            const force = (1 - d / 120) * 16;
            px += (this.mouse.x - px) * 0.15;
            py += (this.mouse.y - py) * 0.15;
          }
        }

        projected.push({ x: px, y: py, z: rz, scale: (rz + 1.8) / 2.8 });
      }

      // Render Synaptic Axons
      ctx.lineWidth = 0.8;
      for (let i = 0; i < this.nodes.length; i++) {
        const p1 = projected[i];
        for (const targetIdx of this.nodes[i].connections) {
          if (targetIdx > i) {
            const p2 = projected[targetIdx];
            const avgZ = (p1.z + p2.z) * 0.5;
            const alpha = Math.max(0.04, (avgZ + 1) * 0.18);
            ctx.strokeStyle = `rgba(255, 255, 255, ${alpha})`;
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
          }
        }
      }

      // Render Synaptic Action Potential Pulses
      for (let i = this.pulses.length - 1; i >= 0; i--) {
        const pulse = this.pulses[i];
        pulse.progress += pulse.speed;
        if (pulse.progress >= 1) {
          this.pulses.splice(i, 1);
          continue;
        }
        const p1 = projected[pulse.from];
        const p2 = projected[pulse.to];
        const px = p1.x + (p2.x - p1.x) * pulse.progress;
        const py = p1.y + (p2.y - p1.y) * pulse.progress;

        ctx.fillStyle = themeColor;
        ctx.shadowColor = themeColor;
        ctx.shadowBlur = 8;
        ctx.beginPath();
        ctx.arc(px, py, 2.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      // Render Neurons
      for (let i = 0; i < projected.length; i++) {
        const p = projected[i];
        const alpha = Math.max(0.15, (p.z + 1) * 0.45);
        ctx.fillStyle = p.z > 0 ? themeColor : `rgba(255, 255, 255, ${alpha})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, Math.max(1, 2.4 * p.scale), 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }

  /* ============================================================================
     4. Mode 3: Aureus Vision AI Liquidity Sniper & Predictive Ghost Engine
     ============================================================================ */
  class VisionSniper {
    constructor(canvas, onTradeExecuted) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      this.onTradeExecuted = onTradeExecuted;
      this.laserX = 0;
      this.laserDir = 1;
      this.isExecuting = false;
      this.candles = [];
      this.asianHigh = 2664.50;
      this.asianLow = 2648.20;
      this.initCandles();
    }

    initCandles() {
      this.candles = [
        { o: 2650.0, h: 2653.2, l: 2649.5, c: 2652.8 },
        { o: 2652.8, h: 2655.4, l: 2651.0, c: 2654.2 },
        { o: 2654.2, h: 2656.8, l: 2653.0, c: 2655.9 },
        { o: 2655.9, h: 2658.0, l: 2654.5, c: 2657.4 },
        { o: 2657.4, h: 2659.1, l: 2656.0, c: 2656.8 },
        { o: 2656.8, h: 2661.2, l: 2655.5, c: 2660.4 }, // Asian Range High Test
        { o: 2660.4, h: 2663.0, l: 2659.8, c: 2662.1 },
        { o: 2662.1, h: 2665.4, l: 2661.5, c: 2664.8 }, // Liquidity Sweep Wick
        { o: 2664.8, h: 2666.2, l: 2658.5, c: 2659.2 }, // Violent Institutional Rejection
        { o: 2659.2, h: 2660.0, l: 2654.1, c: 2655.0 },
        { o: 2655.0, h: 2656.5, l: 2651.8, c: 2652.4 }
      ];
    }

    triggerExecution() {
      if (this.isExecuting) return;
      this.isExecuting = true;
      audio.playLaser();

      setTimeout(() => {
        audio.playProfitChime();
        this.isExecuting = false;
        if (this.onTradeExecuted) this.onTradeExecuted(8940.00);
      }, 750);
    }

    render() {
      const ctx = this.ctx;
      const w = this.canvas.width;
      const h = this.canvas.height;
      ctx.clearRect(0, 0, w, h);

      const paddingLeft = 40;
      const paddingRight = 140;
      const paddingTop = 40;
      const paddingBottom = 40;

      const chartW = w - paddingLeft - paddingRight;
      const chartH = h - paddingTop - paddingBottom;

      const minPrice = 2644.0;
      const maxPrice = 2670.0;
      const priceToY = p => paddingTop + (1 - (p - minPrice) / (maxPrice - minPrice)) * chartH;

      // Draw Grid Lines & Price Ticks
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
      ctx.lineWidth = 1;
      for (let p = 2646; p <= 2668; p += 4) {
        const y = priceToY(p);
        ctx.beginPath();
        ctx.moveTo(paddingLeft, y);
        ctx.lineTo(w - paddingRight, y);
        ctx.stroke();

        ctx.font = '10px JetBrains Mono, monospace';
        ctx.fillStyle = '#64748b';
        ctx.fillText(`$${p.toFixed(2)}`, w - paddingRight + 12, y + 4);
      }

      // Draw Asian Range Box (18:00 - 02:00 UTC)
      const asianYTop = priceToY(this.asianHigh);
      const asianYBottom = priceToY(this.asianLow);
      const asianBoxW = chartW * 0.62;

      ctx.fillStyle = 'rgba(245, 197, 66, 0.05)';
      ctx.fillRect(paddingLeft, asianYTop, asianBoxW, asianYBottom - asianYTop);

      ctx.strokeStyle = 'rgba(245, 197, 66, 0.5)';
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(paddingLeft, asianYTop);
      ctx.lineTo(w - paddingRight, asianYTop);
      ctx.moveTo(paddingLeft, asianYBottom);
      ctx.lineTo(w - paddingRight, asianYBottom);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.font = '700 10px JetBrains Mono, monospace';
      ctx.fillStyle = '#f5c542';
      ctx.fillText('ASIAN HIGH: $2,664.50 [STOP CLUSTER POOL]', paddingLeft + 10, asianYTop - 8);
      ctx.fillText('ASIAN LOW: $2,648.20', paddingLeft + 10, asianYBottom + 16);

      // Render Historical Candlesticks
      const candleSpacing = chartW / 15;
      for (let i = 0; i < this.candles.length; i++) {
        const c = this.candles[i];
        const cx = paddingLeft + (i + 1) * candleSpacing;
        const isBull = c.c >= c.o;
        const color = isBull ? '#00f0ff' : '#ec4899';

        const yOpen = priceToY(c.o);
        const yClose = priceToY(c.c);
        const yHigh = priceToY(c.h);
        const yLow = priceToY(c.l);

        // Wick
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(cx, yHigh);
        ctx.lineTo(cx, yLow);
        ctx.stroke();

        // Body
        ctx.fillStyle = color;
        const bodyTop = Math.min(yOpen, yClose);
        const bodyH = Math.max(2, Math.abs(yOpen - yClose));
        ctx.fillRect(cx - 5, bodyTop, 10, bodyH);
      }

      // Render 3 Holographic Predictive Ghost Candles
      const lastX = paddingLeft + (this.candles.length + 1) * candleSpacing;
      const ghostData = [
        { o: 2652.4, h: 2653.8, l: 2646.2, c: 2647.5 },
        { o: 2647.5, h: 2648.5, l: 2642.0, c: 2644.0 },
        { o: 2644.0, h: 2645.0, l: 2640.2, c: 2641.8 }
      ];

      for (let i = 0; i < ghostData.length; i++) {
        const g = ghostData[i];
        const gx = lastX + i * candleSpacing;
        const gyOpen = priceToY(g.o);
        const gyClose = priceToY(g.c);
        const gyHigh = priceToY(g.h);
        const gyLow = priceToY(g.l);

        // Holographic Ghost Wick & Body (Dashed & Glow)
        ctx.strokeStyle = 'rgba(245, 197, 66, 0.4)';
        ctx.setLineDash([3, 3]);
        ctx.beginPath();
        ctx.moveTo(gx, gyHigh);
        ctx.lineTo(gx, gyLow);
        ctx.stroke();

        ctx.fillStyle = 'rgba(245, 197, 66, 0.12)';
        ctx.fillRect(gx - 5, Math.min(gyOpen, gyClose), 10, Math.abs(gyOpen - gyClose));
        ctx.strokeRect(gx - 5, Math.min(gyOpen, gyClose), 10, Math.abs(gyOpen - gyClose));
        ctx.setLineDash([]);
      }

      ctx.font = '600 10px JetBrains Mono, monospace';
      ctx.fillStyle = '#f5c542';
      ctx.fillText('PREDICTIVE GHOST TRAJECTORY (94.2% CONFIDENCE)', lastX - 20, priceToY(2641.0) + 24);

      // Render Moving Gemini Multimodal Vision Laser Scanline
      this.laserX += 2.2 * this.laserDir;
      if (this.laserX > chartW || this.laserX < 0) this.laserDir *= -1;

      const scanX = paddingLeft + this.laserX;
      const grad = ctx.createLinearGradient(scanX - 20, 0, scanX + 20, 0);
      grad.addColorStop(0, 'transparent');
      grad.addColorStop(0.5, 'rgba(0, 240, 255, 0.4)');
      grad.addColorStop(1, 'transparent');

      ctx.fillStyle = grad;
      ctx.fillRect(scanX - 20, paddingTop, 40, chartH);

      ctx.strokeStyle = '#00f0ff';
      ctx.shadowColor = '#00f0ff';
      ctx.shadowBlur = 12;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(scanX, paddingTop);
      ctx.lineTo(scanX, h - paddingBottom);
      ctx.stroke();
      ctx.shadowBlur = 0;
    }
  }

  /* ============================================================================
     5. Mode 4: 4D Gravitational Spacetime Liquidity Well
     ============================================================================ */
  class GravitationalSpacetime {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      this.singularityActive = false;
      this.singularityRadius = 0;
      this.mouse = { x: 0, y: 0, active: false };
      this.bindEvents();
    }

    bindEvents() {
      this.canvas.addEventListener('mousemove', e => {
        const rect = this.canvas.getBoundingClientRect();
        this.mouse.x = e.clientX - rect.left;
        this.mouse.y = e.clientY - rect.top;
        this.mouse.active = true;
      });
      this.canvas.addEventListener('mouseleave', () => {
        this.mouse.active = false;
      });
    }

    triggerSingularity() {
      this.singularityActive = true;
      this.singularityRadius = 1;
      audio.playBreach();
    }

    render() {
      const ctx = this.ctx;
      const w = this.canvas.width;
      const h = this.canvas.height;
      ctx.clearRect(0, 0, w, h);

      const cx = w / 2;
      const cy = h / 2;
      const time = performance.now() * 0.002;

      const rows = 18;
      const cols = 28;

      ctx.strokeStyle = 'rgba(0, 240, 255, 0.22)';
      ctx.lineWidth = 1;

      // Draw Perspective Curvature Mesh
      for (let r = 0; r < rows; r++) {
        ctx.beginPath();
        for (let c = 0; c < cols; c++) {
          const u = (c / (cols - 1)) * 2 - 1; // -1 to 1
          const v = (r / (rows - 1)) * 2 - 1;

          let px = cx + u * (w * 0.46);
          let py = cy + v * (h * 0.38) + 40;

          // Einsteinian Gravitational Well deformation
          const distToCenter = Math.hypot(px - cx, py - cy);
          const well = Math.exp(-distToCenter * 0.012) * 55;
          py += well;

          // Ripple wave
          py += Math.sin(time + distToCenter * 0.03) * 6;

          // Mouse Gravitational Interaction
          if (this.mouse.active) {
            const dm = Math.hypot(px - this.mouse.x, py - this.mouse.y);
            if (dm < 140) {
              py += (1 - dm / 140) * 35;
            }
          }

          if (c === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.stroke();
      }

      // Singularity Event (Accretion Disk)
      if (this.singularityActive) {
        this.singularityRadius += 2.5;
        if (this.singularityRadius > 110) {
          this.singularityActive = false;
        }

        ctx.strokeStyle = '#f5c542';
        ctx.shadowColor = '#f5c542';
        ctx.shadowBlur = 20;
        ctx.beginPath();
        ctx.arc(cx, cy + 50, this.singularityRadius, 0, Math.PI * 2);
        ctx.stroke();
        ctx.shadowBlur = 0;
      }
    }
  }

  /* ============================================================================
     6. Master Cockpit Orchestrator (Wires DOM & Loops)
     ============================================================================ */
  function initCockpit() {
    const deck = document.getElementById('omniscience-deck');
    const canvas = document.getElementById('cockpit-canvas');
    if (!deck || !canvas) return;

    let currentMode = 'globe';
    let globeEngine = null;
    let neuralEngine = null;
    let sniperEngine = null;
    let spacetimeEngine = null;

    // High-DPI Canvas Resizing
    function resizeCanvas() {
      const rect = canvas.parentElement.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      const ctx = canvas.getContext('2d');
      ctx.scale(dpr, dpr);
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Initialize Sub-Engines
    globeEngine = new TacticalGlobe(canvas, hub => {
      const cityEl = document.getElementById('telemetry-hub-name');
      const spreadEl = document.getElementById('telemetry-hub-spread');
      const volEl = document.getElementById('telemetry-hub-vol');
      const statusEl = document.getElementById('telemetry-hub-status');
      if (cityEl) cityEl.textContent = hub.name;
      if (spreadEl) spreadEl.textContent = hub.spread;
      if (volEl) volEl.textContent = hub.vol;
      if (statusEl) statusEl.textContent = hub.status;
    });

    neuralEngine = new NeuralSynapse(canvas);
    sniperEngine = new VisionSniper(canvas, pnl => {
      const pnlVal = document.getElementById('live-pnl-val');
      if (pnlVal) {
        let current = 0;
        const target = pnl;
        const step = target / 30;
        const timer = setInterval(() => {
          current += step;
          if (current >= target) {
            current = target;
            clearInterval(timer);
          }
          pnlVal.textContent = `+$${current.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        }, 20);
      }
    });

    spacetimeEngine = new GravitationalSpacetime(canvas);

    // Mode Tab Buttons
    const tabButtons = document.querySelectorAll('.cockpit-tab-btn');
    tabButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        audio.playClick();
        tabButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentMode = btn.getAttribute('data-mode');

        const hint = document.getElementById('canvas-hint-text');
        if (currentMode === 'globe' && hint) hint.textContent = 'Drag to rotate 3D Earth • Click financial hubs to inspect';
        else if (currentMode === 'neural' && hint) hint.textContent = 'Move cursor to warp neural gravity • Click to fire synapses';
        else if (currentMode === 'sniper' && hint) hint.textContent = 'Gemini Vision AI scanning Asian range stop-loss clusters';
        else if (currentMode === 'spacetime' && hint) hint.textContent = 'Drag cursor across 4D mesh to perturb market spacetime';
      });
    });

    // Fullscreen Toggle
    const fullscreenBtn = document.getElementById('btn-cockpit-fullscreen');
    if (fullscreenBtn) {
      fullscreenBtn.addEventListener('click', () => {
        audio.playBreach();
        deck.classList.toggle('fullscreen-mode');
        resizeCanvas();
      });
    }

    // Sound FX Toggle
    const soundBtn = document.getElementById('btn-cockpit-sound');
    if (soundBtn) {
      soundBtn.addEventListener('click', () => {
        const state = audio.toggle();
        soundBtn.textContent = state ? '🔊 SOUND: ON' : '🔇 SOUND: OFF';
        soundBtn.classList.toggle('active', state);
      });
    }

    // Voice Briefing Trigger
    const speechBtn = document.getElementById('btn-transmit-briefing');
    if (speechBtn) {
      speechBtn.addEventListener('click', () => {
        audio.playSonar();
        audio.speak(
          'Don Aurelius Quantum Cockpit initialized. Commander SM.KANISH authenticated. Council consensus: 4 of 4 unanimous. Asian range stop-loss clusters identified at 2,664 dollars. Eagle-Eye Vision AI is primed for liquidity sweep execution.'
        );
      });
    }

    // Trigger Execution Button (Sniper)
    const execBtn = document.getElementById('btn-simulate-sweep');
    if (execBtn) {
      execBtn.addEventListener('click', () => {
        if (currentMode !== 'sniper') {
          // Switch to sniper tab automatically
          const sniperTab = document.querySelector('[data-mode="sniper"]');
          if (sniperTab) sniperTab.click();
        }
        sniperEngine.triggerExecution();
      });
    }

    // Trigger Singularity Button (Spacetime)
    const singBtn = document.getElementById('btn-trigger-singularity');
    if (singBtn) {
      singBtn.addEventListener('click', () => {
        if (currentMode !== 'spacetime') {
          const stTab = document.querySelector('[data-mode="spacetime"]');
          if (stTab) stTab.click();
        }
        spacetimeEngine.triggerSingularity();
      });
    }

    // Emergency Clean Slate Protocol Button
    const cleanSlateBtn = document.getElementById('btn-cockpit-clean-slate');
    if (cleanSlateBtn) {
      cleanSlateBtn.addEventListener('click', () => {
        audio.playAlarm();
        const conf = confirm('⚠️ COMMANDER AUTHORIZATION REQUIRED:\nInitiate Emergency Clean Slate Protocol? All open positions will be flattened immediately.');
        if (conf) {
          audio.speak('Emergency Clean Slate Protocol activated. All contracts flattened. Capital preserved.');
          alert('🚨 CLEAN SLATE ACTIVE: 0 Active Positions • 100% Cash Defense.');
        }
      });
    }

    // Escape exits fullscreen
    window.addEventListener('keydown', e => {
      if (e.key === 'Escape' && deck.classList.contains('fullscreen-mode')) {
        deck.classList.remove('fullscreen-mode');
        resizeCanvas();
      }
    });

    // Expose Global Breach Cockpit Trigger
    window.breachCockpit = function() {
      audio.init();
      audio.playBreach();
      deck.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setTimeout(() => {
        deck.classList.add('fullscreen-mode');
        resizeCanvas();
        audio.speak('Commander SM.KANISH authenticated. Sovereign Quantum Cockpit breached. All neural arrays active.');
      }, 350);
    };

    // Hotkeys W or O to breach cockpit
    window.addEventListener('keydown', e => {
      if (['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) return;
      if (e.key === 'w' || e.key === 'W' || e.key === 'o' || e.key === 'O') {
        if (!deck.classList.contains('fullscreen-mode')) {
          window.breachCockpit();
        }
      }
    });

    // Master 120 FPS Animation Loop
    function renderLoop() {
      if (currentMode === 'globe') globeEngine.render();
      else if (currentMode === 'neural') neuralEngine.render();
      else if (currentMode === 'sniper') sniperEngine.render();
      else if (currentMode === 'spacetime') spacetimeEngine.render();

      requestAnimationFrame(renderLoop);
    }
    requestAnimationFrame(renderLoop);
  }

  if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', initCockpit);
  } else {
    initCockpit();
  }
})();
