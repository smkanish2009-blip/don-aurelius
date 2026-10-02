/**
 * BUTTERMAX ENGINE • DON AURELIUS SOVEREIGN MATRIX
 * Lenis Inertia Scroll, Interactive Stage Physics, Curtain Navigation,
 * and Liquid Interaction Layer. Architected by SM.KANISH.
 */

(function () {
  'use strict';

  // --- 1. Dynamic Lenis Smooth Scroll Integration ---
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
      const lenis = new window.Lenis({
        duration: 1.15,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        orientation: 'vertical',
        gestureOrientation: 'vertical',
        smoothWheel: true,
        wheelMultiplier: 1.0,
        touchMultiplier: 1.8
      });

      function raf(time) {
        lenis.raf(time);
        requestAnimationFrame(raf);
      }
      requestAnimationFrame(raf);
      window.lenisInstance = lenis;
    } catch (e) {
      console.warn('Lenis scroll fallback active:', e);
    }
  }

  // --- 2. Buttermax Curtain Fullscreen Menu ---
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

  // --- 3. Interactive Background Stage (#Stage) ---
  function initBackgroundStage() {
    const canvas = document.getElementById('Stage');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width = 0;
    let height = 0;
    let particles = [];
    let mouse = { x: -9999, y: -9999, active: false };

    function resize() {
      width = window.innerWidth;
      height = window.innerHeight;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      ctx.scale(dpr, dpr);
      createParticles();
    }

    function createParticles() {
      particles = [];
      const count = Math.min(60, Math.floor(width / 24));
      for (let i = 0; i < count; i++) {
        particles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.4,
          vy: (Math.random() - 0.5) * 0.4,
          size: Math.random() * 2 + 1,
          color: Math.random() > 0.4 ? 'rgba(255, 214, 0, ' : 'rgba(0, 240, 255, ',
          alpha: Math.random() * 0.4 + 0.1
        });
      }
    }

    window.addEventListener('resize', resize);
    window.addEventListener('mousemove', (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
      mouse.active = true;
    });
    window.addEventListener('mouseleave', () => {
      mouse.active = false;
    });

    resize();

    function animate() {
      ctx.clearRect(0, 0, width, height);

      // Subtle background grid lines
      ctx.strokeStyle = 'rgba(255, 214, 0, 0.02)';
      ctx.lineWidth = 1;
      const step = 80;
      for (let x = 0; x < width; x += step) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += step) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Draw and connect particles
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        // Mouse attraction
        if (mouse.active) {
          const dx = mouse.x - p.x;
          const dy = mouse.y - p.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 140) {
            p.x += (dx / dist) * 0.8;
            p.y += (dy / dist) * 0.8;
          }
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.color + p.alpha + ')';
        ctx.fill();
      }

      requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
  }

  // --- 4. Initialize Everything on DOM Ready ---
  function init() {
    initSmoothScroll();
    initCurtainMenu();
    initBackgroundStage();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
