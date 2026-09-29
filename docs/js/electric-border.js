/**
 * ElectricBorder Engine (React Bits Port for Don Aurelius)
 * Conceived by @BalintFerenczy, enhanced for 60-120 FPS mobile & desktop hardware acceleration
 * 
 * Features:
 * - Direct Element Dimension Mapping: Completely eliminates shrink-wrap & 50% width clamp bugs
 * - Dual-Pass Incandescent Plasma Stroke: Saturated neon color aura + White-hot electric core
 * - Symmetrically Centered Perlin Noise: Sparks dance both outward and inward around the card rim
 * - Dynamic Card Geometry: Extracts computed border-radius per-device (18px on mobile, 24px on desktop)
 * - Self-Healing Size Tracking: Automatically resyncs canvas if font loads or layout reflows
 * - IntersectionObserver + Touch Throttling: Pauses during active inertial touch-swipes for 100% fluid scroll
 */

(function () {
  'use strict';

  // Math & Noise primitives
  function random(x) {
    const val = (Math.sin(x * 12.9898) * 43758.5453) % 1;
    return val < 0 ? val + 1 : val;
  }

  function noise2D(x, y) {
    const i = Math.floor(x);
    const j = Math.floor(y);
    const fx = x - i;
    const fy = y - j;

    const a = random(i + j * 57);
    const b = random(i + 1 + j * 57);
    const c = random(i + (j + 1) * 57);
    const d = random(i + 1 + (j + 1) * 57);

    const ux = fx * fx * (3.0 - 2.0 * fx);
    const uy = fy * fy * (3.0 - 2.0 * fy);

    return a * (1 - ux) * (1 - uy) + b * ux * (1 - uy) + c * (1 - ux) * uy + d * ux * uy;
  }

  function octavedNoise(x, octaves, lacunarity, gain, baseAmplitude, baseFrequency, time, seed, baseFlatness) {
    let y = 0;
    let amplitude = baseAmplitude;
    let frequency = baseFrequency;

    for (let i = 0; i < octaves; i++) {
      let octaveAmplitude = amplitude;
      if (i === 0) {
        octaveAmplitude *= baseFlatness;
      }
      y += octaveAmplitude * noise2D(frequency * x + seed * 100, time * frequency * 0.3);
      frequency *= lacunarity;
      amplitude *= gain;
    }

    return y;
  }

  function getCornerPoint(centerX, centerY, radius, startAngle, arcLength, progress) {
    const angle = startAngle + progress * arcLength;
    return {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle)
    };
  }

  function getRoundedRectPoint(t, left, top, width, height, radius) {
    const straightWidth = width - 2 * radius;
    const straightHeight = height - 2 * radius;
    const cornerArc = (Math.PI * radius) / 2;
    const totalPerimeter = 2 * straightWidth + 2 * straightHeight + 4 * cornerArc;
    const distance = t * totalPerimeter;

    let accumulated = 0;

    // Top edge
    if (distance <= accumulated + straightWidth) {
      const progress = (distance - accumulated) / straightWidth;
      return { x: left + radius + progress * straightWidth, y: top };
    }
    accumulated += straightWidth;

    // Top-right corner
    if (distance <= accumulated + cornerArc) {
      const progress = (distance - accumulated) / cornerArc;
      return getCornerPoint(left + width - radius, top + radius, radius, -Math.PI / 2, Math.PI / 2, progress);
    }
    accumulated += cornerArc;

    // Right edge
    if (distance <= accumulated + straightHeight) {
      const progress = (distance - accumulated) / straightHeight;
      return { x: left + width, y: top + radius + progress * straightHeight };
    }
    accumulated += straightHeight;

    // Bottom-right corner
    if (distance <= accumulated + cornerArc) {
      const progress = (distance - accumulated) / cornerArc;
      return getCornerPoint(left + width - radius, top + height - radius, radius, 0, Math.PI / 2, progress);
    }
    accumulated += cornerArc;

    // Bottom edge
    if (distance <= accumulated + straightWidth) {
      const progress = (distance - accumulated) / straightWidth;
      return { x: left + width - radius - progress * straightWidth, y: top + height };
    }
    accumulated += straightWidth;

    // Bottom-left corner
    if (distance <= accumulated + cornerArc) {
      const progress = (distance - accumulated) / cornerArc;
      return getCornerPoint(left + radius, top + height - radius, radius, Math.PI / 2, Math.PI / 2, progress);
    }
    accumulated += cornerArc;

    // Left edge
    if (distance <= accumulated + straightHeight) {
      const progress = (distance - accumulated) / straightHeight;
      return { x: left, y: top + height - radius - progress * straightHeight };
    }
    accumulated += straightHeight;

    // Top-left corner
    const progress = (distance - accumulated) / cornerArc;
    return getCornerPoint(left + radius, top + radius, radius, Math.PI, Math.PI / 2, progress);
  }

  // Active instances registry & touch/scroll throttle
  const instances = [];
  let isGlobalScrolling = false;
  let scrollTimeout = null;

  const handleScrollInteraction = () => {
    isGlobalScrolling = true;
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
      isGlobalScrolling = false;
    }, 100);
  };

  window.addEventListener('scroll', handleScrollInteraction, { passive: true });
  window.addEventListener('touchmove', handleScrollInteraction, { passive: true });

  class CardElectricBorder {
    constructor(element, options = {}) {
      this.container = element;
      this.color = options.color || element.getAttribute('data-electric-color') || '#f0c75e';
      this.speed = parseFloat(options.speed || element.getAttribute('data-electric-speed') || '1.2');
      this.chaos = parseFloat(options.chaos || element.getAttribute('data-electric-chaos') || '0.12');

      this.isVisible = false;
      this.time = Math.random() * 50;
      this.lastFrameTime = performance.now();

      // Mobile Responsive Baseline Parameters
      this.isMobile = window.innerWidth <= 768;
      this.octaves = this.isMobile ? 5 : 7;
      this.lacunarity = 1.6;
      this.gain = 0.7;
      this.amplitude = this.chaos;
      this.frequency = 10;
      this.baseFlatness = 0;
      this.displacement = this.isMobile ? 12 : 16;
      this.borderOffset = this.isMobile ? 16 : 24;
      this.borderRadius = this.isMobile ? 18 : 24;

      this.initDOM();
      this.initObservers();
    }

    initDOM() {
      this.container.classList.add('electric-border');
      this.container.style.setProperty('--electric-border-color', this.color);

      // 1. Create ambient glow layers wrapper if not present
      if (!this.container.querySelector('.eb-layers')) {
        const layers = document.createElement('div');
        layers.className = 'eb-layers';
        layers.innerHTML = `
          <div class="eb-glow-1"></div>
          <div class="eb-glow-2"></div>
          <div class="eb-background-glow"></div>
        `;
        this.container.insertBefore(layers, this.container.firstChild);
      }

      // 2. Create canvas container if not present
      let canvasBox = this.container.querySelector('.eb-canvas-container');
      if (!canvasBox) {
        canvasBox = document.createElement('div');
        canvasBox.className = 'eb-canvas-container';
        this.canvas = document.createElement('canvas');
        this.canvas.className = 'eb-canvas';
        canvasBox.appendChild(this.canvas);
        this.container.insertBefore(canvasBox, this.container.firstChild);
      } else {
        this.canvas = canvasBox.querySelector('.eb-canvas');
      }

      this.ctx = this.canvas.getContext('2d', { alpha: true, desynchronized: true });
      this.updateSize();
    }

    updateSize() {
      if (!this.container || !this.canvas || !this.ctx) return;
      const rect = this.container.getBoundingClientRect();
      const cardW = Math.round(rect.width || this.container.offsetWidth);
      const cardH = Math.round(rect.height || this.container.offsetHeight);
      if (cardW === 0 || cardH === 0) return;

      this.isMobile = window.innerWidth <= 768;
      // Border offset: extra margin around card so sparks never clip
      this.borderOffset = this.isMobile ? 16 : 24;
      // Displacement: physical spark reach
      this.displacement = this.isMobile ? 12 : 16;
      this.octaves = this.isMobile ? 5 : 7;

      // Extract dynamic border radius from computed style (18px mobile, 24px desktop)
      try {
        const style = window.getComputedStyle(this.container);
        const parsedR = parseFloat(style.borderRadius);
        if (!isNaN(parsedR) && parsedR > 0) {
          this.borderRadius = parsedR;
        } else {
          this.borderRadius = this.isMobile ? 18 : 24;
        }
      } catch (e) {
        this.borderRadius = this.isMobile ? 18 : 24;
      }
      this.container.style.setProperty('--electric-radius', `${this.borderRadius}px`);

      this.cardWidth = cardW;
      this.cardHeight = cardH;
      this.width = cardW + this.borderOffset * 2;
      this.height = cardH + this.borderOffset * 2;

      // Position the canvas container with exact negative offsets to overhang card symmetrically
      const canvasBox = this.canvas.parentElement;
      if (canvasBox) {
        canvasBox.style.position = 'absolute';
        canvasBox.style.top = `-${this.borderOffset}px`;
        canvasBox.style.left = `-${this.borderOffset}px`;
        canvasBox.style.width = `${this.width}px`;
        canvasBox.style.height = `${this.height}px`;
      }

      // DPR capping: 1.5x on mobile to conserve thermal budget, 2x on desktop
      this.dpr = Math.min(window.devicePixelRatio || 1, this.isMobile ? 1.5 : 2);
      this.canvas.width = Math.round(this.width * this.dpr);
      this.canvas.height = Math.round(this.height * this.dpr);
      this.canvas.style.width = `${this.width}px`;
      this.canvas.style.height = `${this.height}px`;

      this.ctx.setTransform(1, 0, 0, 1, 0, 0);
      this.ctx.scale(this.dpr, this.dpr);
    }

    initObservers() {
      // IntersectionObserver: Animate ONLY when card is in or near the viewport
      this.io = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          this.isVisible = entry.isIntersecting;
        });
      }, { rootMargin: '60px 0px' });
      this.io.observe(this.container);

      // ResizeObserver: Adapt automatically to layout shifts & viewport changes
      this.ro = new ResizeObserver(() => {
        this.updateSize();
      });
      this.ro.observe(this.container);
    }

    render(currentTime) {
      if (!this.isVisible || !this.ctx) return;
      if (isGlobalScrolling) return; // Skip compute during active drag/touch-scroll for 100% 60-120 FPS
      if (document.hidden) return; // Skip when tab is in background or screen is off

      // Self-healing check: if card size changed (e.g. font loaded, window resize)
      const currentW = Math.round(this.container.offsetWidth);
      const currentH = Math.round(this.container.offsetHeight);
      if (Math.abs(currentW - this.cardWidth) > 2 || Math.abs(currentH - this.cardHeight) > 2) {
        this.updateSize();
      }

      const deltaTime = Math.min((currentTime - this.lastFrameTime) / 1000, 0.1);
      this.time += deltaTime * this.speed;
      this.lastFrameTime = currentTime;

      const ctx = this.ctx;
      const width = this.width;
      const height = this.height;
      const borderOffset = this.borderOffset;

      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      ctx.scale(this.dpr, this.dpr);

      const scale = this.displacement;
      const left = borderOffset;
      const top = borderOffset;
      const borderWidth = width - 2 * borderOffset;
      const borderHeight = height - 2 * borderOffset;
      const maxRadius = Math.min(borderWidth, borderHeight) / 2;
      const radius = Math.min(this.borderRadius, maxRadius);

      const approximatePerimeter = 2 * (borderWidth + borderHeight) + 2 * Math.PI * radius;
      const sampleCount = this.isMobile
        ? Math.max(70, Math.min(130, Math.floor(approximatePerimeter / 6.0)))
        : Math.max(100, Math.min(220, Math.floor(approximatePerimeter / 4.2)));

      ctx.beginPath();

      for (let i = 0; i <= sampleCount; i++) {
        const progress = i / sampleCount;
        const point = getRoundedRectPoint(progress, left, top, borderWidth, borderHeight, radius);

        const xNoise = octavedNoise(
          progress * 8,
          this.octaves,
          this.lacunarity,
          this.gain,
          this.amplitude,
          this.frequency,
          this.time,
          0,
          this.baseFlatness
        );

        const yNoise = octavedNoise(
          progress * 8,
          this.octaves,
          this.lacunarity,
          this.gain,
          this.amplitude,
          this.frequency,
          this.time,
          1,
          this.baseFlatness
        );

        // Center noise symmetrically around 0 so sparks dance inward AND outward across the card rim
        const centeredX = (xNoise - 0.122) / 0.08;
        const centeredY = (yNoise - 0.122) / 0.08;

        const displacedX = point.x + centeredX * scale;
        const displacedY = point.y + centeredY * scale;

        if (i === 0) {
          ctx.moveTo(displacedX, displacedY);
        } else {
          ctx.lineTo(displacedX, displacedY);
        }
      }

      ctx.closePath();

      // Pass 1: Vibrant Saturated Neon Electric Aura
      ctx.strokeStyle = this.color;
      ctx.lineWidth = this.isMobile ? 2.2 : 2.6;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.shadowColor = this.color;
      ctx.shadowBlur = this.isMobile ? 7 : 10;
      ctx.stroke();

      // Pass 2: White-Hot Incandescent Lightning Core
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = this.isMobile ? 0.9 : 1.1;
      ctx.shadowColor = '#ffffff';
      ctx.shadowBlur = 2;
      ctx.stroke();
    }

    destroy() {
      if (this.io) this.io.disconnect();
      if (this.ro) this.ro.disconnect();
    }
  }

  // Master Animation Loop (Centralized 60-120 FPS Clock)
  function masterLoop(time) {
    for (let i = 0; i < instances.length; i++) {
      instances[i].render(time);
    }
    requestAnimationFrame(masterLoop);
  }
  requestAnimationFrame(masterLoop);

  // Auto-init all eligible cards on the page
  function initAllElectricBorders() {
    // Sovereign color mapping by card theme
    const cardColorMap = [
      { selector: '.card-eagle', color: '#10b981', chaos: 0.13 },         // Emerald
      { selector: '.card-quantum', color: '#c084fc', chaos: 0.14 },       // Neon Purple
      { selector: '.card-sentinel', color: '#00ffcc', chaos: 0.12 },      // Electric Cyan
      { selector: '.card-jarvis', color: '#f0c75e', chaos: 0.12 },        // Sovereign Gold
      { selector: '.cockpit-preview-box', color: '#00ffcc', chaos: 0.11 },// Cyan Radar
      { selector: '.genesis-banner', color: '#f0c75e', chaos: 0.12 },     // Sovereign Gold
      { selector: '.spec-legacy', color: '#64748b', chaos: 0.09 },        // Slate
      { selector: '.spec-hedge', color: '#38bdf8', chaos: 0.11 },         // Sky Blue
      { selector: '.spec-aureus', color: '#f0c75e', chaos: 0.14 },        // Sovereign Gold
      { selector: '.agent-card:nth-child(1)', color: '#f59e0b', chaos: 0.12 }, // Agent Hawk: Amber
      { selector: '.agent-card:nth-child(2)', color: '#00ffcc', chaos: 0.12 }, // Agent Radar: Cyan
      { selector: '.agent-card:nth-child(3)', color: '#ef4444', chaos: 0.14 }, // Agent Predator: Crimson
      { selector: '.agent-card:nth-child(4)', color: '#a855f7', chaos: 0.12 }, // Agent Inquisitor: Purple
      { selector: '.google-card', color: '#00ffcc', chaos: 0.11 },        // Google Cyan
      { selector: '.founder-grid', color: '#f0c75e', chaos: 0.13 },       // Founder SM.KANISH: Gold
      { selector: '.verification-card', color: '#f0c75e', chaos: 0.11 },  // Verification: Gold
      { selector: '.telemetry-bar', color: '#00ffcc', chaos: 0.10 }       // Telemetry Bar: Cyan
    ];

    const cards = document.querySelectorAll(
      '.apple-liquid-card, .genesis-card, .tilt-card, [data-electric-border]'
    );

    cards.forEach(card => {
      // Prevent duplicate attachment
      if (card.hasAttribute('data-electric-attached')) return;
      card.setAttribute('data-electric-attached', 'true');

      let assignedColor = '#f0c75e';
      let assignedChaos = 0.12;

      // Find matching theme or check custom attributes
      for (let rule of cardColorMap) {
        if (card.matches(rule.selector)) {
          assignedColor = rule.color;
          assignedChaos = rule.chaos;
          break;
        }
      }

      if (card.hasAttribute('data-electric-color')) {
        assignedColor = card.getAttribute('data-electric-color');
      }

      const instance = new CardElectricBorder(card, {
        color: assignedColor,
        chaos: assignedChaos,
        borderRadius: 24,
        speed: 1.2
      });
      instances.push(instance);
    });
  }

  // Window resize & orientation change triggers global size refresh
  window.addEventListener('resize', () => {
    for (let i = 0; i < instances.length; i++) {
      instances[i].updateSize();
    }
  }, { passive: true });

  window.addEventListener('orientationchange', () => {
    setTimeout(() => {
      for (let i = 0; i < instances.length; i++) {
        instances[i].updateSize();
      }
    }, 150);
  }, { passive: true });

  // Export to window
  window.CardElectricBorder = CardElectricBorder;
  window.initAllElectricBorders = initAllElectricBorders;

  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    initAllElectricBorders();
  } else {
    document.addEventListener('DOMContentLoaded', initAllElectricBorders);
  }
})();
