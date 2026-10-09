/* ==============================================================================
   DON AURELIUS • APPLE 3D WEBGL & INTERACTIVE SCROLL SYSTEM (v6.0)
   Synthesized from Apple Developer Design (HIG) & MotionSites Standards
   Hardware-Accelerated 120 FPS Three.js Scene • Scroll-Driven Cinematic Telemetry
   ============================================================================== */

(function () {
  'use strict';

  /* ============================================================================
     1. CHAPTER DEFINITIONS FOR THE APPLE LIQUID GLASS SCROLL HUD
     ============================================================================ */
  const CHAPTERS = [
    { id: 'overview', index: '01', title: 'OVERVIEW', subtitle: 'Sovereign Genesis' },
    { id: 'symphony-studio', index: '02', title: 'SYMPHONY', subtitle: 'Visual Quant Logic' },
    { id: 'genesis', index: '03', title: 'GENESIS SUITE', subtitle: '4 Core Inventions' },
    { id: 'architectural-specs', index: '04', title: 'SPECS', subtitle: '0.38ms LD4 Bridge' },
    { id: 'performance-backtest', index: '05', title: 'BACKTEST', subtitle: '1,000 Monte Carlo Paths' },
    { id: 'war-room', index: '06', title: 'WAR ROOM', subtitle: 'Tactical Cockpit' },
    { id: 'terminal-access', index: '07', title: 'TERMINAL', subtitle: 'Instant Deployment' }
  ];

  let activeChapterIndex = 0;
  let isScrolling = false;
  let scrollTimeout = null;

  /* ============================================================================
     2. PROCEDURAL APPLE HAPTIC AUDIO (Zero dependencies)
     ============================================================================ */
  let audioCtx = null;
  function playAppleHapticClick(frequency = 1200, duration = 0.035) {
    try {
      if (!audioCtx) {
        const AudioClass = window.AudioContext || window.webkitAudioContext;
        if (AudioClass) audioCtx = new AudioClass();
      }
      if (audioCtx && audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
      if (!audioCtx) return;

      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(frequency, audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(350, audioCtx.currentTime + duration);

      gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
      gain.gain.linearRampToValueAtTime(0.001, audioCtx.currentTime + duration);

      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch (e) {
      // Audio fallback safe
    }
  }

  /* ============================================================================
     3. BUILD & INJECT THE APPLE LIQUID GLASS FLOATING SCROLL HUD
     ============================================================================ */
  function injectAppleScrollHud() {
    if (document.getElementById('apple-scroll-hud')) return;

    const hud = document.createElement('div');
    hud.id = 'apple-scroll-hud';
    hud.className = 'apple-scroll-hud';
    hud.setAttribute('role', 'navigation');
    hud.setAttribute('aria-label', 'Apple Chapter Navigation');

    hud.innerHTML = `
      <div class="hud-progress-ring">
        <svg class="hud-progress-svg" viewBox="0 0 28 28">
          <defs>
            <linearGradient id="hudGoldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#F5D061" />
              <stop offset="100%" stop-color="#E5A638" />
            </linearGradient>
          </defs>
          <circle class="hud-progress-track" cx="14" cy="14" r="12" />
          <circle class="hud-progress-bar" id="hud-progress-bar" cx="14" cy="14" r="12" />
        </svg>
        <div class="hud-indicator-dot"></div>
      </div>
      <div class="hud-chapter-info">
        <div class="hud-chapter-index" id="hud-chapter-index">CH. 01 // OVERVIEW</div>
        <div class="hud-chapter-title" id="hud-chapter-title">Sovereign Genesis</div>
      </div>
      <div class="hud-quick-nav" id="hud-quick-nav">
        ${CHAPTERS.map((ch, idx) => `
          <a href="#${ch.id}" class="hud-nav-item ${idx === 0 ? 'active' : ''}" data-index="${idx}">
            <span>${ch.index}. ${ch.title}</span>
            <div class="nav-dot"></div>
          </a>
        `).join('')}
      </div>
    `;

    document.body.appendChild(hud);

    // Quick jump event listeners with smooth spring scroll
    hud.querySelectorAll('.hud-nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = item.getAttribute('href').substring(1);
        const targetElem = document.getElementById(targetId);
        if (targetElem) {
          playAppleHapticClick(1400);
          targetElem.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  /* ============================================================================
     4. UPDATE SCROLL PROGRESS & ACTIVE CHAPTER
     ============================================================================ */
  function updateScrollMetrics() {
    const progressBar = document.getElementById('hud-progress-bar');
    const indexLabel = document.getElementById('hud-chapter-index');
    const titleLabel = document.getElementById('hud-chapter-title');

    const totalScroll = document.documentElement.scrollHeight - window.innerHeight;
    const currentScroll = window.scrollY || window.pageYOffset;
    const scrollRatio = totalScroll > 0 ? Math.min(1, Math.max(0, currentScroll / totalScroll)) : 0;

    // Circumference for r=12 is 2 * PI * 12 ≈ 75.398
    if (progressBar) {
      const offset = 75.4 * (1 - scrollRatio);
      progressBar.style.strokeDashoffset = offset;
    }

    // Determine current active chapter
    let currentIdx = 0;
    const scrollMiddle = currentScroll + window.innerHeight * 0.35;

    for (let i = 0; i < CHAPTERS.length; i++) {
      const elem = document.getElementById(CHAPTERS[i].id);
      if (elem) {
        const top = elem.offsetTop;
        const height = elem.offsetHeight;
        if (scrollMiddle >= top && scrollMiddle < top + height) {
          currentIdx = i;
          break;
        } else if (scrollMiddle >= top + height && i === CHAPTERS.length - 1) {
          currentIdx = i;
        }
      }
    }

    if (currentIdx !== activeChapterIndex) {
      activeChapterIndex = currentIdx;
      const chapter = CHAPTERS[activeChapterIndex];
      if (indexLabel) indexLabel.textContent = `CH. ${chapter.index} // ${chapter.title}`;
      if (titleLabel) titleLabel.textContent = chapter.subtitle;

      // Update quick nav active class
      document.querySelectorAll('.hud-nav-item').forEach((item, idx) => {
        if (idx === activeChapterIndex) {
          item.classList.add('active');
        } else {
          item.classList.remove('active');
        }
      });

      playAppleHapticClick(900 + currentIdx * 120, 0.025);

      // Notify 3D engine of chapter shift
      if (window.apple3DEngine) {
        window.apple3DEngine.onChapterChange(activeChapterIndex, scrollRatio);
      }
    }
  }

  /* ============================================================================
     5. THREE.JS 3D QUANTUM CORE ENGINE (120 FPS / INTERACTIVE MOUSE & SCROLL)
     ============================================================================ */
  class AppleQuantum3DEngine {
    constructor() {
      this.canvas = null;
      this.renderer = null;
      this.scene = null;
      this.camera = null;
      this.coreGroup = null;
      this.gimbalGroup = null;
      this.particles = null;
      this.vectorLines = [];
      this.innerCoreMesh = null;
      this.outerIcosaMesh = null;
      this.lightGold = null;
      this.lightCyan = null;

      this.isDragging = false;
      this.prevMouse = { x: 0, y: 0 };
      this.mouseVelocity = { x: 0, y: 0 };
      this.targetRotation = { x: 0, y: 0 };
      this.currentMode = 'CORE'; // CORE | VECTORS | WIREFRAME | GIMBAL

      this.scrollProgress = 0;
      this.activeChapter = 0;
      this.animId = null;
    }

    init() {
      this.canvas = document.getElementById('stage-3d-canvas');
      if (!this.canvas || typeof THREE === 'undefined') {
        console.warn('Three.js or stage-3d-canvas not ready for Apple 3D Engine.');
        return;
      }

      this.setupContainer();
      this.setupScene();
      this.setupGeometry();
      this.setupLighting();
      this.setupEvents();
      this.animate();
    }

    setupContainer() {
      // Wrap the existing stage in the upgraded master squircle container
      const parent = this.canvas.parentElement;
      if (parent && !parent.classList.contains('hero-3d-stage-master')) {
        parent.classList.add('hero-3d-stage-master');
        this.canvas.classList.add('hero-3d-canvas-element');

        // Inject Stage HUD Controls
        const hudOverlay = document.createElement('div');
        hudOverlay.className = 'stage-hud-overlay';
        hudOverlay.innerHTML = `
          <div class="stage-hud-badge">
            <span style="color:#10B981;">●</span> 3D QUANTUM AUREUS MATRIX
          </div>
          <div class="stage-hud-controls">
            <button class="stage-btn-control active" data-mode="CORE">CORE</button>
            <button class="stage-btn-control" data-mode="VECTORS">VECTORS</button>
            <button class="stage-btn-control" data-mode="WIREFRAME">WIRE</button>
            <button class="stage-btn-control" data-mode="GIMBAL">GIMBAL</button>
          </div>
        `;
        parent.appendChild(hudOverlay);

        const bottomHud = document.createElement('div');
        bottomHud.className = 'stage-bottom-telemetry';
        bottomHud.innerHTML = `
          <span>DRAG TO ORBIT • SCROLL CO-INTEGRATION ACTIVE</span>
          <span id="stage-3d-fps">120 FPS • WEBGL</span>
        `;
        parent.appendChild(bottomHud);

        // Control clicks
        hudOverlay.querySelectorAll('.stage-btn-control').forEach(btn => {
          btn.addEventListener('click', (e) => {
            e.stopPropagation();
            hudOverlay.querySelectorAll('.stage-btn-control').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            this.setMode(btn.dataset.mode);
            playAppleHapticClick(1500);
          });
        });
      }
    }

    setupScene() {
      const width = this.canvas.clientWidth || 980;
      const height = this.canvas.clientHeight || 380;

      this.scene = new THREE.Scene();
      this.camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 1000);
      this.camera.position.set(0, 0, 22);

      this.renderer = new THREE.WebGLRenderer({
        canvas: this.canvas,
        alpha: true,
        antialias: true,
        powerPreference: 'high-performance'
      });
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      this.renderer.setSize(width, height);

      this.coreGroup = new THREE.Group();
      this.scene.add(this.coreGroup);
    }

    setupGeometry() {
      // 1. Central Multifaceted Quantum Core (Icosahedron + Octahedron)
      const icosaGeom = new THREE.IcosahedronGeometry(4.8, 1);
      const icosaMat = new THREE.MeshStandardMaterial({
        color: 0xF5D061,
        metalness: 0.85,
        roughness: 0.22,
        wireframe: false,
        flatShading: true
      });
      this.outerIcosaMesh = new THREE.Mesh(icosaGeom, icosaMat);
      this.coreGroup.add(this.outerIcosaMesh);

      // 2. Wireframe Lattice Overlay
      const wireMat = new THREE.MeshBasicMaterial({
        color: 0xFFFFFF,
        wireframe: true,
        transparent: true,
        opacity: 0.35
      });
      const wireMesh = new THREE.Mesh(icosaGeom, wireMat);
      wireMesh.scale.set(1.002, 1.002, 1.002);
      this.coreGroup.add(wireMesh);

      // 3. Inner Quantum Tesseract (Octahedron with Cyan luminescence)
      const octGeom = new THREE.OctahedronGeometry(3.0, 0);
      const octMat = new THREE.MeshStandardMaterial({
        color: 0x38BDF8,
        emissive: 0x0C4A6E,
        roughness: 0.15,
        metalness: 0.9,
        transparent: true,
        opacity: 0.85
      });
      this.innerCoreMesh = new THREE.Mesh(octGeom, octMat);
      this.coreGroup.add(this.innerCoreMesh);

      // 4. Gyroscopic Aureus Gimbal Rings
      this.gimbalGroup = new THREE.Group();
      this.coreGroup.add(this.gimbalGroup);

      const ringConfigs = [
        { radius: 6.8, tube: 0.08, color: 0xF5D061, rotX: Math.PI / 2.5, rotY: 0 },
        { radius: 7.6, tube: 0.06, color: 0xE5A638, rotX: 0, rotY: Math.PI / 3 },
        { radius: 8.4, tube: 0.04, color: 0x38BDF8, rotX: Math.PI / 4, rotY: Math.PI / 4 }
      ];

      ringConfigs.forEach(conf => {
        const ringGeom = new THREE.TorusGeometry(conf.radius, conf.tube, 16, 80);
        const ringMat = new THREE.MeshStandardMaterial({
          color: conf.color,
          metalness: 0.9,
          roughness: 0.2
        });
        const ring = new THREE.Mesh(ringGeom, ringMat);
        ring.rotation.set(conf.rotX, conf.rotY, 0);
        this.gimbalGroup.add(ring);
      });

      // 5. Floating Gold Particle Matrix (1,200 particle field)
      const particleCount = 1200;
      const particlePositions = new Float32Array(particleCount * 3);
      const particleColors = new Float32Array(particleCount * 3);

      for (let i = 0; i < particleCount; i++) {
        const r = 9 + Math.random() * 8;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos((Math.random() * 2) - 1);

        particlePositions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
        particlePositions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
        particlePositions[i * 3 + 2] = r * Math.cos(phi);

        // Mix Gold and Cyan
        if (Math.random() > 0.25) {
          particleColors[i * 3] = 0.96;     // R
          particleColors[i * 3 + 1] = 0.81; // G
          particleColors[i * 3 + 2] = 0.38; // B
        } else {
          particleColors[i * 3] = 0.22;     // R
          particleColors[i * 3 + 1] = 0.74; // G
          particleColors[i * 3 + 2] = 0.97; // B
        }
      }

      const pGeom = new THREE.BufferGeometry();
      pGeom.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
      pGeom.setAttribute('color', new THREE.BufferAttribute(particleColors, 3));

      const pMat = new THREE.PointsMaterial({
        size: 0.16,
        vertexColors: true,
        transparent: true,
        opacity: 0.75,
        blending: THREE.AdditiveBlending
      });
      this.particles = new THREE.Points(pGeom, pMat);
      this.scene.add(this.particles);

      // 6. Stochastic Monte Carlo Trajectory Splines
      for (let i = 0; i < 6; i++) {
        const points = [];
        const startX = -9 + Math.random() * 2;
        const endX = 9 + Math.random() * 2;
        const steps = 14;

        for (let s = 0; s <= steps; s++) {
          const t = s / steps;
          const x = startX + (endX - startX) * t;
          const y = (Math.sin(t * Math.PI * 2 + i) * 3) + (Math.random() - 0.5) * 1.5;
          const z = (Math.cos(t * Math.PI * 2 + i) * 3) + (Math.random() - 0.5) * 1.5;
          points.push(new THREE.Vector3(x, y, z));
        }

        const curve = new THREE.CatmullRomCurve3(points);
        const tubeGeom = new THREE.TubeGeometry(curve, 32, 0.04, 8, false);
        const tubeMat = new THREE.MeshBasicMaterial({
          color: i % 2 === 0 ? 0xF5D061 : 0x10B981,
          transparent: true,
          opacity: 0.55
        });
        const splineMesh = new THREE.Mesh(tubeGeom, tubeMat);
        this.coreGroup.add(splineMesh);
        this.vectorLines.push(splineMesh);
      }
    }

    setupLighting() {
      // Warm Imperial Gold Specular Key Light
      this.lightGold = new THREE.PointLight(0xFFE484, 2.8, 60);
      this.lightGold.position.set(12, 14, 16);
      this.scene.add(this.lightGold);

      // Cold Institutional Blue Fill Light
      this.lightCyan = new THREE.PointLight(0x38BDF8, 2.0, 60);
      this.lightCyan.position.set(-14, -10, -12);
      this.scene.add(this.lightCyan);

      // Soft Ambient
      const ambient = new THREE.AmbientLight(0x1E293B, 0.8);
      this.scene.add(ambient);
    }

    setupEvents() {
      window.addEventListener('resize', () => {
        if (!this.canvas || !this.renderer || !this.camera) return;
        const w = this.canvas.clientWidth || 980;
        const h = this.canvas.clientHeight || 380;
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(w, h);
      }, { passive: true });

      // Interactive Pointer / Mouse Drag & Tilt
      const onPointerDown = (e) => {
        this.isDragging = true;
        this.prevMouse.x = e.clientX || (e.touches && e.touches[0].clientX);
        this.prevMouse.y = e.clientY || (e.touches && e.touches[0].clientY);
      };

      const onPointerMove = (e) => {
        const clientX = e.clientX || (e.touches && e.touches[0].clientX);
        const clientY = e.clientY || (e.touches && e.touches[0].clientY);

        if (this.isDragging) {
          const deltaX = clientX - this.prevMouse.x;
          const deltaY = clientY - this.prevMouse.y;
          this.mouseVelocity.x = deltaX * 0.008;
          this.mouseVelocity.y = deltaY * 0.008;
          this.coreGroup.rotation.y += this.mouseVelocity.x;
          this.coreGroup.rotation.x += this.mouseVelocity.y;
          this.prevMouse.x = clientX;
          this.prevMouse.y = clientY;
        } else {
          // Hover parallax tilt
          const rect = this.canvas.getBoundingClientRect();
          const normX = (clientX - rect.left) / rect.width - 0.5;
          const normY = (clientY - rect.top) / rect.height - 0.5;
          this.targetRotation.y = normX * 0.6;
          this.targetRotation.x = normY * 0.4;
        }
      };

      const onPointerUp = () => {
        this.isDragging = false;
      };

      this.canvas.addEventListener('mousedown', onPointerDown);
      window.addEventListener('mousemove', onPointerMove, { passive: true });
      window.addEventListener('mouseup', onPointerUp);

      this.canvas.addEventListener('touchstart', onPointerDown, { passive: true });
      window.addEventListener('touchmove', onPointerMove, { passive: true });
      window.addEventListener('touchend', onPointerUp);
    }

    setMode(mode) {
      this.currentMode = mode;
      if (!this.outerIcosaMesh) return;

      if (mode === 'WIREFRAME') {
        this.outerIcosaMesh.material.wireframe = true;
        this.innerCoreMesh.material.wireframe = true;
      } else {
        this.outerIcosaMesh.material.wireframe = false;
        this.innerCoreMesh.material.wireframe = false;
      }

      if (mode === 'VECTORS') {
        this.vectorLines.forEach(v => {
          v.scale.set(1.4, 1.4, 1.4);
          v.material.opacity = 0.9;
        });
      } else {
        this.vectorLines.forEach(v => {
          v.scale.set(1, 1, 1);
          v.material.opacity = 0.55;
        });
      }
    }

    onChapterChange(chapterIndex, scrollRatio) {
      this.activeChapter = chapterIndex;
      this.scrollProgress = scrollRatio;

      // Adjust camera distance and core scale dynamically per chapter
      if (this.camera && this.coreGroup) {
        const targetZ = 22 + Math.sin(scrollRatio * Math.PI) * 4;
        this.camera.position.z = targetZ;

        // Color shifts depending on active narrative chapter
        if (chapterIndex === 2) {
          // Genesis Suite: Boost cyan lumination
          if (this.lightCyan) this.lightCyan.intensity = 3.5;
        } else {
          if (this.lightCyan) this.lightCyan.intensity = 2.0;
        }
      }
    }

    animate() {
      this.animId = requestAnimationFrame(() => this.animate());

      if (!this.coreGroup) return;

      const time = Date.now() * 0.001;

      // Continuous Gyro & Orbit Rotation
      if (!this.isDragging) {
        const speed = this.currentMode === 'GIMBAL' ? 0.025 : 0.006;
        this.coreGroup.rotation.y += speed;
        this.coreGroup.rotation.x += Math.sin(time * 0.5) * 0.002;

        // Smooth Lerp toward mouse parallax tilt
        this.coreGroup.rotation.y += (this.targetRotation.y - this.coreGroup.rotation.y * 0.1) * 0.05;
        this.coreGroup.rotation.x += (this.targetRotation.x - this.coreGroup.rotation.x * 0.1) * 0.05;
      }

      // Gimbal Counter-rotation
      if (this.gimbalGroup) {
        this.gimbalGroup.rotation.z += 0.012;
        this.gimbalGroup.rotation.x -= 0.008;
      }

      // Pulsing Inner Quantum Tesseract
      if (this.innerCoreMesh) {
        const scalePulse = 1 + Math.sin(time * 3) * 0.08;
        this.innerCoreMesh.scale.set(scalePulse, scalePulse, scalePulse);
        this.innerCoreMesh.rotation.y -= 0.018;
      }

      // Swirling Particle Matrix
      if (this.particles) {
        this.particles.rotation.y += 0.002;
        this.particles.rotation.x += 0.001;
      }

      // Orbiting lights for dynamic specular reflections
      if (this.lightGold) {
        this.lightGold.position.x = Math.sin(time * 0.8) * 16;
        this.lightGold.position.z = Math.cos(time * 0.8) * 16;
      }
      if (this.lightCyan) {
        this.lightCyan.position.x = Math.cos(time * 0.6) * -16;
        this.lightCyan.position.z = Math.sin(time * 0.6) * -16;
      }

      this.renderer.render(this.scene, this.camera);
    }
  }

  /* ============================================================================
     6. CARD SPECULAR SHEEN & MOUSE FOLLOWER (APPLE LIQUID GLASS SPEC)
     ============================================================================ */
  function initAppleCardSheen() {
    const cards = document.querySelectorAll('.apple-squircle-card, .apple-liquid-card, .tilt-card, .c-bento-card, .metric-glass-card');

    cards.forEach(card => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        card.style.setProperty('--mouse-x', `${x}%`);
        card.style.setProperty('--mouse-y', `${y}%`);
      }, { passive: true });
    });
  }

  /* ============================================================================
     7. SCROLL OBSERVER FOR 3D PERSPECTIVE REVEALS
     ============================================================================ */
  function initScrollPerspectiveReveals() {
    const targets = document.querySelectorAll('.reveal-3d, .c-bento-card, .telemetry-bar, .composer-hero-metrics, .section-title-wrap');

    targets.forEach(el => el.classList.add('scroll-reveal-item'));

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-revealed');
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -40px 0px'
    });

    targets.forEach(el => observer.observe(el));
  }

  /* ============================================================================
     8. GLOBAL INITIALIZATION
     ============================================================================ */
  function initializeAppleExperience() {
    // 1. Inject Scroll HUD
    injectAppleScrollHud();

    // 2. Initialize Three.js 3D Engine
    window.apple3DEngine = new AppleQuantum3DEngine();
    window.apple3DEngine.init();

    // 3. Initialize Card Sheen & Perspective Reveals
    initAppleCardSheen();
    initScrollPerspectiveReveals();

    // 4. Bind window scroll for metrics
    window.addEventListener('scroll', () => {
      updateScrollMetrics();

      // Fast scroll velocity detection for subtle physical compression
      document.body.classList.add('is-scrolling-fast');
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        document.body.classList.remove('is-scrolling-fast');
      }, 150);
    }, { passive: true });

    // Initial pass
    updateScrollMetrics();
  }

  if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', initializeAppleExperience);
  } else {
    initializeAppleExperience();
  }

})();
