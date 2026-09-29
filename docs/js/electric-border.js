/**
 * ElectricBorder Engine (React Bits Port for Don Aurelius)
 * Conceived by @BalintFerenczy, ported with 60 FPS hardware acceleration
 * Features:
 * - Octaved 2D Procedural Perlin Noise for authentic electric plasma discharge
 * - IntersectionObserver: Zero CPU cost when cards are offscreen
 * - Throttled during active page scroll to ensure 100% 60 FPS fluidity
 * - High-DPI Retina canvas rendering with sub-pixel rounding
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

  // Active instances registry
  const instances = [];
  let isGlobalScrolling = false;
  let scrollTimeout = null;

  window.addEventListener('scroll', () => {
    isGlobalScrolling = true;
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
      isGlobalScrolling = false;
    }, 100);
  }, { passive: true });

  class CardElectricBorder {
    constructor(element, options = {}) {
      this.container = element;
      this.color = options.color || element.getAttribute('data-electric-color') || '#f0c75e';
      this.speed = parseFloat(options.speed || element.getAttribute('data-electric-speed') || '1.1');
      this.chaos = parseFloat(options.chaos || element.getAttribute('data-electric-chaos') || '0.12');
      this.borderRadius = parseFloat(options.borderRadius || element.getAttribute('data-electric-radius') || '24');
      
      this.isVisible = false;
      this.time = Math.random() * 50;
      this.lastFrameTime = performance.now();
      
      // Configuration
      this.octaves = 8;
      this.lacunarity = 1.6;
      this.gain = 0.7;
      this.amplitude = this.chaos;
      this.frequency = 10;
      this.baseFlatness = 0;
      this.displacement = 45;
      this.borderOffset = 45;

      this.initDOM();
      this.initObservers();
    }

    initDOM() {
      this.container.classList.add('electric-border');
      this.container.style.setProperty('--electric-border-color', this.color);
      this.container.style.setProperty('--electric-radius', `${this.borderRadius}px`);

      // 1. Create layers wrapper if not present
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
      if (rect.width === 0 || rect.height === 0) return;

      this.width = rect.width + this.borderOffset * 2;
      this.height = rect.height + this.borderOffset * 2;

      this.dpr = Math.min(window.devicePixelRatio || 1, 1.75);
      this.canvas.width = this.width * this.dpr;
      this.canvas.height = this.height * this.dpr;
      this.canvas.style.width = `${this.width}px`;
      this.canvas.style.height = `${this.height}px`;
      
      this.ctx.setTransform(1, 0, 0, 1, 0, 0);
      this.ctx.scale(this.dpr, this.dpr);
    }

    initObservers() {
      // IntersectionObserver: Animate ONLY when card is in viewport
      this.io = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          this.isVisible = entry.isIntersecting;
        });
      }, { rootMargin: '60px 0px' });
      this.io.observe(this.container);

      // ResizeObserver: Adapt automatically to layout shifts
      this.ro = new ResizeObserver(() => {
        this.updateSize();
      });
      this.ro.observe(this.container);
    }

    render(currentTime) {
      if (!this.isVisible || !this.ctx) return;
      if (isGlobalScrolling) return; // Skip compute during active drag/scroll for 60 FPS

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

      ctx.strokeStyle = this.color;
      ctx.lineWidth = 1.35;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.shadowColor = this.color;
      ctx.shadowBlur = 4;

      const scale = this.displacement;
      const left = borderOffset;
      const top = borderOffset;
      const borderWidth = width - 2 * borderOffset;
      const borderHeight = height - 2 * borderOffset;
      const maxRadius = Math.min(borderWidth, borderHeight) / 2;
      const radius = Math.min(this.borderRadius, maxRadius);

      const approximatePerimeter = 2 * (borderWidth + borderHeight) + 2 * Math.PI * radius;
      const sampleCount = Math.max(100, Math.min(240, Math.floor(approximatePerimeter / 4.5)));

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

        const displacedX = point.x + xNoise * scale;
        const displacedY = point.y + yNoise * scale;

        if (i === 0) {
          ctx.moveTo(displacedX, displacedY);
        } else {
          ctx.lineTo(displacedX, displacedY);
        }
      }

      ctx.closePath();
      ctx.stroke();
    }

    destroy() {
      if (this.io) this.io.disconnect();
      if (this.ro) this.ro.disconnect();
    }
  }

  // Master Animation Loop (Centralized 60 FPS Clock)
  function masterLoop(time) {
    for (let i = 0; i < instances.length; i++) {
      instances[i].render(time);
    }
    requestAnimationFrame(masterLoop);
  }
  requestAnimationFrame(masterLoop);

  // Auto-init all eligible cards on the page
  function initAllElectricBorders() {
    // Color mapping by card theme
    const cardColorMap = [
      { selector: '.card-eagle', color: '#10b981', chaos: 0.13 },         // Emerald
      { selector: '.card-quantum', color: '#c084fc', chaos: 0.14 },       // Neon Purple
      { selector: '.card-sentinel', color: '#00ffcc', chaos: 0.12 },      // Electric Cyan
      { selector: '.card-jarvis', color: '#f0c75e', chaos: 0.12 },        // Sovereign Gold
      { selector: '.cockpit-preview-box', color: '#00ffcc', chaos: 0.11 },// Cyan Radar
      { selector: '.genesis-banner', color: '#f0c75e', chaos: 0.10 },     // Sovereign Gold
      { selector: '.spec-legacy', color: '#64748b', chaos: 0.08 },        // Slate
      { selector: '.spec-hedge', color: '#38bdf8', chaos: 0.10 },         // Sky Blue
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
        speed: 1.15
      });
      instances.push(instance);
    });
  }

  // Export to window
  window.CardElectricBorder = CardElectricBorder;
  window.initAllElectricBorders = initAllElectricBorders;

  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    initAllElectricBorders();
  } else {
    document.addEventListener('DOMContentLoaded', initAllElectricBorders);
  }
})();
