/**
 * BUTTERMAX ENGINE • DON AURELIUS SOVEREIGN MATRIX
 * Features:
 * 1. Studio Freight Lenis Smooth Inertia Scroll with Navigation Offset Correction.
 * 2. Interactive Magnetic Fluid Cursor (Difference-blend, elastic expansion, dynamic badges).
 * 3. 3D Card Tilt Physics & Real-Time Hairline Spotlight Border Tracking.
 * 4. Interactive Quantum Grid Waves & Spark Physics on #Stage Canvas.
 * 5. Fullscreen Curtain Menu Controller.
 * Architected by SM.KANISH.
 */

(function () {
  'use strict';

  // ============================================================================
  // 1. Lenis Smooth Scroll with Smart Anchor Offset Correction
  // ============================================================================
  let lenisInstance = null;

  function initSmoothScroll() {
    if (window.Lenis) {
      startLenis();
    } else {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1.0.42/dist/lenis.min.js';
      script.onload = startLenis;
      document.head.appendChild(script);
    }
  }

  function startLenis() {
    try {
      lenisInstance = new window.Lenis({
        duration: 1.15,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        orientation: 'vertical',
        gestureOrientation: 'vertical',
        smoothWheel: true,
        wheelMultiplier: 1.0,
        touchMultiplier: 1.8
      });

      function raf(time) {
        lenisInstance.raf(time);
        requestAnimationFrame(raf);
      }
      requestAnimationFrame(raf);
      window.lenisInstance = lenisInstance;

      // Handle smooth anchor clicks with 90px header offset
      document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener('click', function (e) {
          const targetId = this.getAttribute('href');
          if (targetId && targetId !== '#') {
            const targetEl = document.querySelector(targetId);
            if (targetEl) {
              e.preventDefault();
              lenisInstance.scrollTo(targetEl, { offset: -90, duration: 1.2 });
              if (history.pushState) {
                history.pushState(null, null, targetId);
              }
            }
          }
        });
      });
    } catch (e) {
      console.warn('Lenis scroll fallback active:', e);
    }
  }

  // ============================================================================
  // 2. Interactive Magnetic Fluid Cursor System
  // ============================================================================
  function initMagneticCursor() {
    // Only enable on desktop/fine pointers
    if (window.matchMedia('(hover: none) or (pointer: coarse)').matches) return;

    let dot = document.querySelector('.bx-cursor-dot');
    let ring = document.querySelector('.bx-cursor-ring');

    if (!dot) {
      dot = document.createElement('div');
      dot.className = 'bx-cursor-dot';
      document.body.appendChild(dot);
    }

    if (!ring) {
      ring = document.createElement('div');
      ring.className = 'bx-cursor-ring';
      const badge = document.createElement('span');
      badge.className = 'bx-cursor-badge';
      badge.textContent = 'VIEW';
      ring.appendChild(badge);
      document.body.appendChild(ring);
    }

    const badge = ring.querySelector('.bx-cursor-badge');

    let mouseX = -100;
    let mouseY = -100;
    let ringX = -100;
    let ringY = -100;
    let isVisible = false;

    window.addEventListener('mousemove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
      if (!isVisible) {
        isVisible = true;
        dot.style.opacity = '1';
        ring.style.opacity = '1';
      }
      dot.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0) translate(-50%, -50%)`;
    });

    window.addEventListener('mouseleave', () => {
      isVisible = false;
      dot.style.opacity = '0';
      ring.style.opacity = '0';
    });

    function renderCursor() {
      // Lerp ring position for buttery inertia
      ringX += (mouseX - ringX) * 0.16;
      ringY += (mouseY - ringY) * 0.16;
      ring.style.transform = `translate3d(${ringX}px, ${ringY}px, 0) translate(-50%, -50%)`;
      requestAnimationFrame(renderCursor);
    }
    requestAnimationFrame(renderCursor);

    // Hover detection on interactive elements
    const interactiveSelectors = [
      'a',
      'button',
      '.bx-btn-pill',
      '.bx-grid-item',
      '.genesis-card',
      '.spec-card',
      '.war-card',
      '.agent-card',
      '.theater-screen-wrap',
      '.hero-3d-stage',
      '.faq-question-btn',
      '.cockpit-btn'
    ].join(',');

    document.addEventListener('mouseover', (e) => {
      const target = e.target.closest(interactiveSelectors);
      if (target) {
        ring.classList.add('is-hovering');

        // Contextual badge determination
        let label = 'VIEW';
        if (target.getAttribute('data-cursor')) {
          label = target.getAttribute('data-cursor');
        } else if (target.closest('#war-room') || target.classList.contains('war-card') || target.classList.contains('agent-card')) {
          label = 'BREACH';
        } else if (target.closest('#installation-theater') || target.classList.contains('theater-screen-wrap')) {
          label = 'PLAY';
        } else if (target.closest('#hero-stage') || target.classList.contains('hero-3d-stage')) {
          label = 'ROTATE';
        } else if (target.classList.contains('faq-question-btn')) {
          label = 'EXPAND';
        } else if (target.getAttribute('href') && target.getAttribute('href').includes('t.me')) {
          label = 'CONNECT';
        } else if (target.classList.contains('bx-grid-item')) {
          label = 'INSPECT';
        }
        if (badge) badge.textContent = label;
      }
    });

    document.addEventListener('mouseout', (e) => {
      const target = e.target.closest(interactiveSelectors);
      if (target) {
        ring.classList.remove('is-hovering');
      }
    });

    // Magnetic pull physics for pill buttons
    document.querySelectorAll('.bx-btn-pill, .bx-menu-circle-btn').forEach((btn) => {
      btn.addEventListener('mousemove', (e) => {
        const rect = btn.getBoundingClientRect();
        const relX = e.clientX - (rect.left + rect.width / 2);
        const relY = e.clientY - (rect.top + rect.height / 2);
        btn.style.transform = `translate(${relX * 0.22}px, ${relY * 0.22}px)`;
      });

      btn.addEventListener('mouseleave', () => {
        btn.style.transform = '';
      });
    });
  }

  // ============================================================================
  // 3. 3D Card Tilt & Real-Time Hairline Spotlight Border Tracking
  // ============================================================================
  function initCardTiltSpotlight() {
    const cards = document.querySelectorAll(
      '.bx-grid-item, .genesis-card, .spec-card, .founder-card, .war-card, .agent-card, .theater-stage-box, .telemetry-bar, .cockpit-preview-box'
    );

    cards.forEach((card) => {
      card.addEventListener('mouseenter', () => {
        card.style.transition = 'none';
      });

      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Pass coordinates to CSS variable for hairline spotlight
        card.style.setProperty('--mouse-x', `${x}px`);
        card.style.setProperty('--mouse-y', `${y}px`);

        // Compute 3D tilt angles
        const tiltX = (x / rect.width - 0.5) * 2;
        const tiltY = (y / rect.height - 0.5) * 2;

        card.style.transform = `perspective(1000px) rotateX(${-tiltY * 5}deg) rotateY(${tiltX * 5}deg) translateZ(4px)`;
      });

      card.addEventListener('mouseleave', () => {
        card.style.transition = 'transform 0.55s cubic-bezier(0.215, 0.61, 0.355, 1)';
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
        card.style.setProperty('--mouse-x', '-999px');
        card.style.setProperty('--mouse-y', '-999px');
      });
    });
  }

  // ============================================================================
  // 4. Interactive Quantum Grid Waves & Spark Physics (#Stage Canvas)
  // ============================================================================
  function initBackgroundStage() {
    const canvas = document.getElementById('Stage');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width = 0;
    let height = 0;

    let mouse = { x: -9999, y: -9999, vx: 0, vy: 0, lastX: -9999, lastY: -9999, active: false };
    let gridNodes = [];
    let sparks = [];

    const spacing = 75;

    function resize() {
      width = window.innerWidth;
      height = window.innerHeight;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      ctx.scale(dpr, dpr);
      buildGrid();
    }

    function buildGrid() {
      gridNodes = [];
      const cols = Math.ceil(width / spacing) + 1;
      const rows = Math.ceil(height / spacing) + 1;

      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          gridNodes.push({
            originX: c * spacing,
            originY: r * spacing,
            x: c * spacing,
            y: r * spacing,
            vx: 0,
            vy: 0,
            c: c,
            r: r
          });
        }
      }
    }

    window.addEventListener('resize', resize);

    window.addEventListener('mousemove', (e) => {
      mouse.vx = e.clientX - mouse.lastX;
      mouse.vy = e.clientY - mouse.lastY;
      mouse.lastX = e.clientX;
      mouse.lastY = e.clientY;
      mouse.x = e.clientX;
      mouse.y = e.clientY;
      mouse.active = true;

      // Spawn kinetic quantum sparks on fast mouse movements
      const speed = Math.sqrt(mouse.vx * mouse.vx + mouse.vy * mouse.vy);
      if (speed > 8 && sparks.length < 80) {
        for (let i = 0; i < 2; i++) {
          sparks.push({
            x: mouse.x + (Math.random() - 0.5) * 20,
            y: mouse.y + (Math.random() - 0.5) * 20,
            vx: (Math.random() - 0.5) * 3 + mouse.vx * 0.1,
            vy: (Math.random() - 0.5) * 3 + mouse.vy * 0.1,
            life: 1.0,
            color: Math.random() > 0.4 ? 'rgba(255, 214, 0, ' : 'rgba(0, 240, 255, '
          });
        }
      }
    });

    window.addEventListener('mouseleave', () => {
      mouse.active = false;
      mouse.x = -9999;
      mouse.y = -9999;
    });

    resize();

    function animate() {
      ctx.clearRect(0, 0, width, height);

      // 1. Update and draw grid vertices with spring tension
      const cols = Math.ceil(width / spacing) + 1;
      const rows = Math.ceil(height / spacing) + 1;

      for (let i = 0; i < gridNodes.length; i++) {
        const node = gridNodes[i];

        // Mouse displacement wave
        if (mouse.active) {
          const dx = node.x - mouse.x;
          const dy = node.y - mouse.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          const maxDist = 160;

          if (dist < maxDist && dist > 1) {
            const force = (1 - dist / maxDist) * 12;
            node.vx += (dx / dist) * force;
            node.vy += (dy / dist) * force;
          }
        }

        // Spring force returning node to origin
        const homeX = node.originX - node.x;
        const homeY = node.originY - node.y;
        node.vx += homeX * 0.08;
        node.vy += homeY * 0.08;

        // Damping
        node.vx *= 0.82;
        node.vy *= 0.82;

        node.x += node.vx;
        node.y += node.vy;
      }

      // 2. Draw subtle hairline connecting grid lines
      ctx.lineWidth = 1;
      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          const idx = r * cols + c;
          const node = gridNodes[idx];
          if (!node) continue;

          // Horizontal wire
          if (c < cols - 1) {
            const rightNode = gridNodes[idx + 1];
            if (rightNode) {
              const dx = node.x - mouse.x;
              const dy = node.y - mouse.y;
              const dist = Math.sqrt(dx * dx + dy * dy);
              const highlight = dist < 200 ? (1 - dist / 200) * 0.16 : 0.02;

              ctx.strokeStyle = `rgba(255, 214, 0, ${highlight})`;
              ctx.beginPath();
              ctx.moveTo(node.x, node.y);
              ctx.lineTo(rightNode.x, rightNode.y);
              ctx.stroke();
            }
          }

          // Vertical wire
          if (r < rows - 1) {
            const bottomNode = gridNodes[idx + cols];
            if (bottomNode) {
              const dx = node.x - mouse.x;
              const dy = node.y - mouse.y;
              const dist = Math.sqrt(dx * dx + dy * dy);
              const highlight = dist < 200 ? (1 - dist / 200) * 0.16 : 0.02;

              ctx.strokeStyle = `rgba(255, 214, 0, ${highlight})`;
              ctx.beginPath();
              ctx.moveTo(node.x, node.y);
              ctx.lineTo(bottomNode.x, bottomNode.y);
              ctx.stroke();
            }
          }
        }
      }

      // 3. Render and update quantum sparks
      for (let s = sparks.length - 1; s >= 0; s--) {
        const spark = sparks[s];
        spark.x += spark.vx;
        spark.y += spark.vy;
        spark.life -= 0.035;

        if (spark.life <= 0) {
          sparks.splice(s, 1);
          continue;
        }

        ctx.fillStyle = spark.color + (spark.life * 0.7) + ')';
        ctx.beginPath();
        ctx.arc(spark.x, spark.y, 1.8, 0, Math.PI * 2);
        ctx.fill();
      }

      requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
  }

  // ============================================================================
  // 5. Fullscreen Curtain Menu Controller
  // ============================================================================
  function initCurtainMenu() {
    const menuBtn = document.getElementById('bx-menu-btn');
    const curtain = document.getElementById('bx-curtain-overlay');
    if (!menuBtn || !curtain) return;

    function toggleMenu() {
      const isOpen = curtain.classList.contains('open');
      if (isOpen) {
        curtain.classList.remove('open');
        menuBtn.classList.remove('open');
        document.body.style.overflow = '';
      } else {
        curtain.classList.add('open');
        menuBtn.classList.add('open');
        document.body.style.overflow = 'hidden';
      }
    }

    menuBtn.addEventListener('click', toggleMenu);

    document.querySelectorAll('.bx-curtain-link').forEach((link) => {
      link.addEventListener('click', () => {
        curtain.classList.remove('open');
        menuBtn.classList.remove('open');
        document.body.style.overflow = '';
      });
    });

    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && curtain.classList.contains('open')) {
        toggleMenu();
      }
    });
  }

  // ============================================================================
  // 6. Master Init Execution
  // ============================================================================
  function init() {
    initSmoothScroll();
    initMagneticCursor();
    initCardTiltSpotlight();
    initBackgroundStage();
    initCurtainMenu();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
