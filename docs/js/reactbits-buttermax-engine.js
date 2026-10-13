/* ==============================================================================
   DON AURELIUS • REACTBITS & BUTTERMAX QUANTUM INTERACTION ENGINE (v7.0)
   Zero AI Slop • Apple Liquid Glass Specular Shaders • 120 FPS Interaction
   Copyright © 2026 SM.KANISH. All Rights Reserved.
   ============================================================================== */

(function () {
  'use strict';

  /* ============================================================================
     1. PROCEDURAL WEB AUDIO ACOUSTIC SYNTHESIZER (ZERO EXTERNAL DEPENDENCY)
     ============================================================================ */
  class AureusAudioEngine {
    constructor() {
      this.ctx = null;
      this.isMuted = false;
      this.soundtrackAudio = null;
      this.isPlayingSoundtrack = false;
      this.waveformAnimId = null;
    }

    initContext() {
      if (!this.ctx) {
        const AudioClass = window.AudioContext || window.webkitAudioContext;
        if (AudioClass) {
          this.ctx = new AudioClass();
        }
      }
      if (this.ctx && this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
    }

    playClick(freq = 1400, duration = 0.03) {
      if (this.isMuted) return;
      try {
        this.initContext();
        if (!this.ctx) return;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(320, this.ctx.currentTime + duration);

        gain.gain.setValueAtTime(0.09, this.ctx.currentTime);
        gain.gain.linearRampToValueAtTime(0.001, this.ctx.currentTime + duration);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + duration);
      } catch (e) {}
    }

    playChirp() {
      if (this.isMuted) return;
      try {
        this.initContext();
        if (!this.ctx) return;

        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(880, now);
        osc.frequency.exponentialRampToValueAtTime(1760, now + 0.08);

        gain.gain.setValueAtTime(0.06, now);
        gain.gain.linearRampToValueAtTime(0.001, now + 0.08);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(now + 0.08);
      } catch (e) {}
    }

    playHarmonicChime() {
      if (this.isMuted) return;
      try {
        this.initContext();
        if (!this.ctx) return;

        const chords = [523.25, 659.25, 783.99, 1046.50]; // C Major Chord
        chords.forEach((f, idx) => {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          const start = this.ctx.currentTime + idx * 0.04;
          const dur = 0.45;

          osc.type = 'sine';
          osc.frequency.setValueAtTime(f, start);

          gain.gain.setValueAtTime(0.05, start);
          gain.gain.exponentialRampToValueAtTime(0.001, start + dur);

          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(start);
          osc.stop(start + dur);
        });
      } catch (e) {}
    }

    toggleMute() {
      this.isMuted = !this.isMuted;
      const btn = document.getElementById('dock-audio-toggle');
      if (btn) {
        if (this.isMuted) {
          btn.classList.add('muted');
          btn.setAttribute('aria-label', 'Sound Effects Muted (Click to Unmute)');
        } else {
          btn.classList.remove('muted');
          btn.setAttribute('aria-label', 'Sound Effects Active (Click to Mute)');
          this.playClick(1600);
        }
      }
      return this.isMuted;
    }

    setupSoundtrackPlayer() {
      this.soundtrackAudio = new Audio('assets/cinematic_soundtrack_60s.wav');
      this.soundtrackAudio.preload = 'metadata';
      this.soundtrackAudio.volume = 0.65;

      const playBtn = document.getElementById('btn-media-soundtrack-play');
      const timeLabel = document.getElementById('media-soundtrack-time');

      if (!playBtn) return;

      playBtn.addEventListener('click', () => {
        if (!this.isPlayingSoundtrack) {
          this.initContext();
          this.soundtrackAudio.play().then(() => {
            this.isPlayingSoundtrack = true;
            playBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>`;
            this.startWaveformVisualizer();
          }).catch(err => {
            console.log('Audio playback permission required:', err);
          });
        } else {
          this.soundtrackAudio.pause();
          this.isPlayingSoundtrack = false;
          playBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>`;
          this.stopWaveformVisualizer();
        }
      });

      this.soundtrackAudio.addEventListener('timeupdate', () => {
        if (timeLabel && this.soundtrackAudio.duration) {
          const cur = Math.floor(this.soundtrackAudio.currentTime);
          const dur = Math.floor(this.soundtrackAudio.duration) || 60;
          timeLabel.textContent = `00:${cur < 10 ? '0' + cur : cur} / 00:${dur < 10 ? '0' + dur : dur}`;
        }
      });

      this.soundtrackAudio.addEventListener('ended', () => {
        this.isPlayingSoundtrack = false;
        playBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>`;
        this.stopWaveformVisualizer();
      });
    }

    startWaveformVisualizer() {
      const canvas = document.getElementById('media-waveform-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const width = canvas.width = canvas.offsetWidth;
      const height = canvas.height = canvas.offsetHeight;

      const bars = 48;
      const barWidth = width / bars;
      let phase = 0;

      const draw = () => {
        ctx.clearRect(0, 0, width, height);
        phase += 0.08;

        for (let i = 0; i < bars; i++) {
          const wave = Math.sin(phase + i * 0.28) * 0.5 + 0.5;
          const noise = Math.random() * 0.25;
          const h = (wave + noise) * (height * 0.75) + 4;
          const y = (height - h) / 2;

          const grad = ctx.createLinearGradient(0, y, 0, y + h);
          grad.addColorStop(0, '#FFE58F');
          grad.addColorStop(0.5, '#F5D061');
          grad.addColorStop(1, '#D4A017');

          ctx.fillStyle = grad;
          ctx.fillRect(i * barWidth + 2, y, barWidth - 4, h);
        }

        if (this.isPlayingSoundtrack) {
          this.waveformAnimId = requestAnimationFrame(draw);
        }
      };

      this.waveformAnimId = requestAnimationFrame(draw);
    }

    stopWaveformVisualizer() {
      if (this.waveformAnimId) {
        cancelAnimationFrame(this.waveformAnimId);
      }
      const canvas = document.getElementById('media-waveform-canvas');
      if (canvas) {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    }
  }

  const audio = new AureusAudioEngine();
  window.aureusAudio = audio;

  /* ============================================================================
     2. MULTI-STAGE APPLE / BLOOMBERG TERMINAL BOOT SEQUENCE
     ============================================================================ */
  function initTerminalPreloader() {
    const preloader = document.getElementById('terminal-boot-preloader');
    if (!preloader) return;

    const fillBar = document.getElementById('boot-progress-fill');
    const counter = document.getElementById('boot-counter-percent');
    const skipBtn = document.getElementById('btn-skip-boot');
    const logs = [
      document.getElementById('boot-log-1'),
      document.getElementById('boot-log-2'),
      document.getElementById('boot-log-3'),
      document.getElementById('boot-log-4'),
      document.getElementById('boot-log-5')
    ];

    let progress = 0;
    const duration = 2400; // 2.4s total boot
    const start = performance.now();

    function updateBoot(now) {
      const elapsed = now - start;
      progress = Math.min(100, Math.floor((elapsed / duration) * 100));

      if (fillBar) fillBar.style.width = progress + '%';
      if (counter) counter.textContent = progress + '%';

      // Reveal logs sequentially
      if (progress >= 15 && logs[0] && !logs[0].classList.contains('visible')) {
        logs[0].classList.add('visible', 'active');
        audio.playClick(900);
      }
      if (progress >= 38 && logs[1] && !logs[1].classList.contains('visible')) {
        if (logs[0]) logs[0].classList.remove('active');
        logs[1].classList.add('visible', 'active');
        audio.playClick(1100);
      }
      if (progress >= 62 && logs[2] && !logs[2].classList.contains('visible')) {
        if (logs[1]) logs[1].classList.remove('active');
        logs[2].classList.add('visible', 'active');
        audio.playClick(1300);
      }
      if (progress >= 85 && logs[3] && !logs[3].classList.contains('visible')) {
        if (logs[2]) logs[2].classList.remove('active');
        logs[3].classList.add('visible', 'active');
        audio.playClick(1500);
      }
      if (progress >= 98 && logs[4] && !logs[4].classList.contains('visible')) {
        if (logs[3]) logs[3].classList.remove('active');
        logs[4].classList.add('visible', 'active');
        audio.playHarmonicChime();
      }

      if (progress < 100) {
        requestAnimationFrame(updateBoot);
      } else {
        setTimeout(dismissPreloader, 350);
      }
    }

    function dismissPreloader() {
      preloader.classList.add('boot-complete');
      setTimeout(() => {
        preloader.style.display = 'none';
      }, 750);
    }

    if (skipBtn) {
      skipBtn.addEventListener('click', () => {
        audio.playClick(1600);
        dismissPreloader();
      });
    }

    requestAnimationFrame(updateBoot);
  }

  /* ============================================================================
     3. REACTBITS SPOTLIGHT CARD ENGINE (120 FPS RAF THROTTLED)
     ============================================================================ */
  function initSpotlightCards() {
    const selector = '.reactbits-spotlight-card, .genesis-card, .symphony-node-box, .cockpit-stat-tile, .agent-card, .security-card, .plan-card';
    const cards = document.querySelectorAll(selector);

    cards.forEach(card => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        card.style.setProperty('--mouse-x', `${x}px`);
        card.style.setProperty('--mouse-y', `${y}px`);
      }, { passive: true });
    });
  }

  /* ============================================================================
     4. REACTBITS 3D TILT PHYSICS CONTROLLER
     ============================================================================ */
  function init3DTiltCards() {
    const tiltCards = document.querySelectorAll('.reactbits-tilt-card');

    tiltCards.forEach(card => {
      let isHovered = false;

      card.addEventListener('mouseenter', () => {
        isHovered = true;
      });

      card.addEventListener('mousemove', (e) => {
        if (!isHovered) return;
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const deltaX = (x - centerX) / centerX;
        const deltaY = (y - centerY) / centerY;

        const maxTilt = 8; // degrees
        const tiltX = -deltaY * maxTilt;
        const tiltY = deltaX * maxTilt;

        card.style.transform = `perspective(1000px) rotateX(${tiltX.toFixed(2)}deg) rotateY(${tiltY.toFixed(2)}deg) scale3d(1.02, 1.02, 1.02)`;
      }, { passive: true });

      card.addEventListener('mouseleave', () => {
        isHovered = false;
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
      });
    });
  }

  /* ============================================================================
     5. REACTBITS DECRYPTED TEXT SCRAMBLER
     ============================================================================ */
  function initDecryptedText() {
    const glyphs = 'ABCDEF0123456789XAUUSD#%$&@§ΨΩ';
    const elements = document.querySelectorAll('.reactbits-decrypted-text');

    elements.forEach(el => {
      const originalText = el.getAttribute('data-original') || el.textContent.trim();
      el.setAttribute('data-original', originalText);
      let interval = null;

      function scramble() {
        let iteration = 0;
        clearInterval(interval);
        audio.playClick(1800, 0.015);

        interval = setInterval(() => {
          el.textContent = originalText
            .split('')
            .map((char, index) => {
              if (index < iteration) {
                return originalText[index];
              }
              if (char === ' ') return ' ';
              return glyphs[Math.floor(Math.random() * glyphs.length)];
            })
            .join('');

          if (iteration >= originalText.length) {
            clearInterval(interval);
          }
          iteration += 1 / 2;
        }, 30);
      }

      el.addEventListener('mouseenter', scramble);
    });
  }

  /* ============================================================================
     6. CLICK SPARK EMITTER ENGINE
     ============================================================================== */
  function initClickSparks() {
    document.addEventListener('click', (e) => {
      // Find if clicked element or parent has spark class or is button
      const target = e.target.closest('.skeuo-btn-master, .skeuo-btn-secondary, .btn-tg, .stage-btn-control, .btn-header-shortcuts, .hud-nav-item');
      if (!target) return;

      audio.playClick(1500, 0.025);

      const count = 8;
      const colors = ['#F5D061', '#38BDF8', '#FFF', '#FFE58F'];

      for (let i = 0; i < count; i++) {
        const particle = document.createElement('div');
        particle.className = 'spark-particle';

        const color = colors[Math.floor(Math.random() * colors.length)];
        particle.style.color = color;
        particle.style.left = `${e.clientX}px`;
        particle.style.top = `${e.clientY}px`;

        const angle = (Math.PI * 2 / count) * i + (Math.random() * 0.4 - 0.2);
        const distance = 25 + Math.random() * 35;
        const tx = Math.cos(angle) * distance;
        const ty = Math.sin(angle) * distance;

        particle.style.setProperty('--tx', `${tx}px`);
        particle.style.setProperty('--ty', `${ty}px`);

        document.body.appendChild(particle);
        setTimeout(() => particle.remove(), 650);
      }
    });
  }

  /* ============================================================================
     7. CRYPTOGRAPHIC SHA-256 CONSENT FINGERPRINT GENERATOR
     ============================================================================ */
  async function computeSHA256(message) {
    const msgBuffer = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  function initSovereignLegalModals() {
    const shieldBtn = document.getElementById('btn-open-legal-shield');
    const licenseBtn = document.getElementById('btn-open-commercial-license');
    const shieldModal = document.getElementById('sovereign-legal-modal');
    const licenseModal = document.getElementById('commercial-license-modal');

    const closeBtns = document.querySelectorAll('.btn-close-modal, .sovereign-modal-overlay');

    if (shieldBtn && shieldModal) {
      shieldBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        audio.playChirp();
        
        // Generate live hash
        const sampleText = "DON_AURELIUS_CFTC_4.41_NFA_2-29_SOVEREIGN_NON_FIDUCIARY_ACCORD_2026_" + Date.now();
        const hash = await computeSHA256(sampleText);
        const hashEl = document.getElementById('legal-sha256-hash');
        if (hashEl) hashEl.textContent = 'SHA-256: ' + hash;

        shieldModal.classList.add('active');
      });
    }

    if (licenseBtn && licenseModal) {
      licenseBtn.addEventListener('click', (e) => {
        e.preventDefault();
        audio.playChirp();
        licenseModal.classList.add('active');
      });
    }

    closeBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        if (e.target === btn || btn.classList.contains('btn-close-modal')) {
          audio.playClick(1000);
          if (shieldModal) shieldModal.classList.remove('active');
          if (licenseModal) licenseModal.classList.remove('active');
        }
      });
    });

    // Anti-Piracy Hardware Binding Simulator Logic
    const bindBtn = document.getElementById('btn-simulate-hw-bind');
    const bindOutput = document.getElementById('hw-bind-result');
    if (bindBtn && bindOutput) {
      bindBtn.addEventListener('click', async () => {
        audio.playClick(1400);
        bindBtn.disabled = true;
        bindBtn.textContent = 'Computing Fingerprint...';

        setTimeout(async () => {
          const hwUUID = 'HW-' + Math.random().toString(36).substring(2, 10).toUpperCase();
          const mt5Acc = 'MT5-' + Math.floor(100000 + Math.random() * 900000);
          const sig = await computeSHA256(hwUUID + mt5Acc);

          bindOutput.innerHTML = `
            <div style="color: #10B981; font-weight: 700; margin-bottom: 4px;">✓ HARDWARE MACHINE BINDING SUCCESSFUL</div>
            <div>BIND_UUID: <span style="color:#FFF;">${hwUUID}</span></div>
            <div>MT5_TERMINAL: <span style="color:#FFF;">${mt5Acc}</span></div>
            <div>CRYPTOGRAPHIC_SEAL: <span style="color:var(--gold-pure);">${sig.substring(0, 32)}...</span></div>
            <div style="margin-top:6px; font-size:0.75rem; color:rgba(255,255,255,0.6);">Anti-tamper kernel lock active. Unauthorized machine replication prohibited.</div>
          `;
          bindBtn.disabled = false;
          bindBtn.textContent = 'Regenerate Hardware Binding';
          audio.playHarmonicChime();
        }, 600);
      });
    }
  }

  /* ============================================================================
     8. DOCUMENT INITIALIZATION ORCHESTRATOR
     ============================================================================ */
  function initAll() {
    initTerminalPreloader();
    initSpotlightCards();
    init3DTiltCards();
    initDecryptedText();
    initClickSparks();
    initSovereignLegalModals();
    audio.setupSoundtrackPlayer();

    // Wire Sound toggle in dock
    const audioToggle = document.getElementById('dock-audio-toggle');
    if (audioToggle) {
      audioToggle.addEventListener('click', () => {
        audio.toggleMute();
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }
})();
