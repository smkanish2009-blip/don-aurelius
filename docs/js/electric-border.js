/**
 * ElectricBorder Engine (React Bits Port for Don Aurelius)
 * Conceived by @BalintFerenczy, enhanced for 60-120 FPS mobile & desktop hardware acceleration
 * Features:
 * - Octaved 2D Procedural Perlin Noise for authentic electric plasma discharge
 * - IntersectionObserver: Zero CPU/GPU cost when cards are offscreen
 * - Mobile Touch/Scroll Throttling: Automatically pauses canvas compute during active touch-drag
 *   and inertial scrolling to guarantee 100% fluid 60-120 FPS scroll performance
 * - Dynamic Card Geometry: Extracts computed border-radius per-device (18px on mobile, 24px on desktop)
 * - Safe Viewport Margins: Tight 10px offset on mobile prevents horizontal overflow while keeping arcs intact
 * - High-DPI Retina canvas scaling with mobile DPR capping (1.5x) to eliminate thermal throttling
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
    }, 120);
  };

  window.addEventListener('scroll', handleScrollInteraction, { passive: true });
  window.addEventListener('touchmove', handleScrollInteraction, { passive: true });

  class CardElectricBorder {
    constructor(element, options = {}) {
      this.container = element;
      this.color = options.color || element.getAttribute('data-electric-color') || '#f0c75e';
      this.speed = parseFloat(options.speed || element.getAttribute('data-electric-speed') || '1.15');
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
      this.displacement = this.isMobile ? 10 : 32;
      this.borderOffset = this.isMobile ? 10 : 32;
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
      if (rect.width === 0 || rect.height === 0) return;

      this.isMobile = window.innerWidth <= 768;
      this.borderOffset = this.isMobile ? 10 : 32;
      this.displacement = this.isMobile ? 10 : 32;
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

      this.width = Math.round(rect.width + this.borderOffset * 2);
      this.height = Math.round(rect.height + this.borderOffset * 2);

      // DPR capping: 1.5x on mobile to conserve thermal budget, 1.75x on desktop
      this.dpr = Math.min(window.devicePixelRatio || 1, this.isMobile ? 1.5 : 1.75);
      this.canvas.width = Math.round(this.width * this.dpr);
      this.canvas.height = Math.round(this.height * this.dpr);
      this.canvas.style.width = `${this.width}px`;
      this.canvas.style.height = `${this.height}px`;

      this.ctx.setTransform(1, 0, 0, 1, 0, 0);
      this.ctx.scale(this.dpr, this.dpr);
    }

    initObservers() {
      // IntersectionObserver: Animate ONLY when card is in or very near the viewport
      this.io = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          this.isVisible = entry.isIntersecting;
        });
      }, { rootMargin: '40px 0px' });
      this.io.observe(this.container);

      // ResizeObserver: Adapt automatically to orientation change & layout shifts
      this.ro = new ResizeObserver(() => {
        this.updateSize();
      });
      this.ro.observe(this.container);
    }

    render(currentTime) {
      if (!this.isVisible || !this.ctx) return;
      if (isGlobalScrolling) return; // Skip compute during active drag/touch-scroll for 100% 60-120 FPS
      if (document.hidden) return; // Skip when tab is in background or screen is off

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
      ctx.lineWidth = this.isMobile ? 1.2 : 1.35;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.shadowColor = this.color;
      ctx.shadowBlur = this.isMobile ? 3 : 4;

      const scale = this.displacement;
      const left = borderOffset;
      const top = borderOffset;
      const borderWidth = width - 2 * borderOffset;
      const borderHeight = height - 2 * borderOffset;
      const maxRadius = Math.min(borderWidth, borderHeight) / 2;
      const radius = Math.min(this.borderRadius, maxRadius);

      const approximatePerimeter = 2 * (borderWidth + borderHeight) + 2 * Math.PI * radius;
      const sampleCount = this.isMobile
        ? Math.max(50, Math.min(100, Math.floor(approximatePerimeter / 7.5)))
        : Math.max(90, Math.min(220, Math.floor(approximatePerimeter / 4.5)));

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
