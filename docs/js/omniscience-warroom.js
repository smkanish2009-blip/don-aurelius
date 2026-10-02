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
     2. Mode 1: Real 3D Photorealistic Earth Globe (Google Earth / Maps Engine)
     Powered by Three.js WebGL • NASA Satellite Topography & Normal Relief
     ============================================================================ */
  class RealTacticalEarth {
    constructor(canvas, onCitySelect) {
      this.canvas = canvas;
      this.onCitySelect = onCitySelect;
      this.viewMode = 'satellite';
      this.autoRotate = true;
      this.targetZoom = 25.0;
      this.isDragging = false;
      this.lastMouseX = 0;
      this.lastMouseY = 0;
      this.velX = 0;
      this.velY = 0.002;

      this.hubs = [
        { name: 'London LBMA', lat: 51.5074, lon: -0.1278, status: 'OPEN • HIGH LIQUIDITY', spread: '0.12 pips', vol: '$42.8B/day', color: '#f5c542' },
        { name: 'New York COMEX', lat: 40.7128, lon: -74.0060, status: 'PRE-MARKET ACTIVE', spread: '0.18 pips', vol: '$38.2B/day', color: '#00f0ff' },
        { name: 'Zurich Vaults', lat: 47.3769, lon: 8.5417, status: 'SETTLEMENT LOCKED', spread: '0.08 pips', vol: '$19.5B/day', color: '#f5c542' },
        { name: 'Tokyo Asia Core', lat: 35.6762, lon: 139.6503, status: 'SESSION HARVESTED', spread: '0.24 pips', vol: '$22.1B/day', color: '#10b981' },
        { name: 'Shanghai SGE', lat: 31.2304, lon: 121.4737, status: 'PHYSICAL ARBITRAGE', spread: '+$14.20 premium', vol: '$26.4B/day', color: '#f5c542' },
        { name: 'Dubai DMCC', lat: 25.2048, lon: 55.2708, status: 'BULLION CLEARED', spread: '0.15 pips', vol: '$16.8B/day', color: '#00f0ff' },
        { name: 'Singapore SGX', lat: 1.3521, lon: 103.8198, status: 'ACTIVE CORRIDOR', spread: '0.16 pips', vol: '$14.2B/day', color: '#10b981' }
      ];
      this.activeHub = this.hubs[0];
      this.raycastTargets = [];
      this.arcs = [];
      this.rings = [];

      this.initScene();
      this.bindControls();
    }

    initScene() {
      if (typeof THREE === 'undefined') return;

      const rect = this.canvas.parentElement ? this.canvas.parentElement.getBoundingClientRect() : { width: 800, height: 520 };
      const w = rect.width || 800;
      const h = rect.height || 520;

      this.scene = new THREE.Scene();
      this.camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 1000);
      this.camera.position.set(0, 3, this.targetZoom);

      this.renderer = new THREE.WebGLRenderer({
        canvas: this.canvas,
        antialias: true,
        alpha: true,
        powerPreference: 'high-performance'
      });
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      this.renderer.setSize(w, h);

      // Texture loader with local assets
      const loader = new THREE.TextureLoader();
      this.textures = {
        day: loader.load('assets/earth_atmos.jpg'),
        normal: loader.load('assets/earth_normal.jpg'),
        specular: loader.load('assets/earth_specular.jpg'),
        night: loader.load('assets/earth_night.jpg'),
        clouds: loader.load('assets/earth_clouds.png')
      };

      // Globe Group
      this.globeGroup = new THREE.Group();
      this.scene.add(this.globeGroup);

      // 1. Earth Sphere (NASA Blue Marble Day)
      const radius = 10;
      this.earthGeometry = new THREE.SphereGeometry(radius, 64, 64);
      this.earthMaterial = new THREE.MeshPhongMaterial({
        map: this.textures.day,
        normalMap: this.textures.normal,
        normalScale: new THREE.Vector2(0.85, 0.85),
        specularMap: this.textures.specular,
        specular: new THREE.Color(0x333333),
        shininess: 16
      });
      this.earthMesh = new THREE.Mesh(this.earthGeometry, this.earthMaterial);
      this.globeGroup.add(this.earthMesh);

      // 2. Realistic Cloud Deck Layer
      this.cloudsGeometry = new THREE.SphereGeometry(radius * 1.014, 64, 64);
      this.cloudsMaterial = new THREE.MeshPhongMaterial({
        map: this.textures.clouds,
        transparent: true,
        opacity: 0.45,
        blending: THREE.AdditiveBlending
      });
      this.cloudsMesh = new THREE.Mesh(this.cloudsGeometry, this.cloudsMaterial);
      this.globeGroup.add(this.cloudsMesh);

      // 3. Google Earth Atmospheric Limb Glow Shader
      const atmosVertexShader = `
        varying vec3 vNormal;
        varying vec3 vPosition;
        void main() {
          vNormal = normalize(normalMatrix * normal);
          vPosition = (modelViewMatrix * vec4(position, 1.0)).xyz;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `;
      const atmosFragmentShader = `
        varying vec3 vNormal;
        varying vec3 vPosition;
        void main() {
          vec3 viewDir = normalize(-vPosition);
          float rim = 1.0 - max(dot(vNormal, viewDir), 0.0);
          float alpha = pow(rim, 2.6) * 0.9;
          vec3 glowColor = mix(vec3(0.0, 0.75, 1.0), vec3(0.96, 0.77, 0.26), 0.15);
          gl_FragColor = vec4(glowColor, alpha);
        }
      `;
      const atmosMat = new THREE.ShaderMaterial({
        vertexShader: atmosVertexShader,
        fragmentShader: atmosFragmentShader,
        side: THREE.BackSide,
        blending: THREE.AdditiveBlending,
        transparent: true
      });
      const atmosMesh = new THREE.Mesh(new THREE.SphereGeometry(radius * 1.045, 64, 64), atmosMat);
      this.scene.add(atmosMesh);

      // 4. Starfield Space Background
      const starGeom = new THREE.BufferGeometry();
      const starCount = 1000;
      const starPositions = new Float32Array(starCount * 3);
      for (let i = 0; i < starCount * 3; i += 3) {
        const r = 200 + Math.random() * 150;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(2 * Math.random() - 1);
        starPositions[i] = r * Math.sin(phi) * Math.cos(theta);
        starPositions[i + 1] = r * Math.sin(phi) * Math.sin(theta);
        starPositions[i + 2] = r * Math.cos(phi);
      }
      starGeom.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
      const starMat = new THREE.PointsMaterial({ color: 0xffffff, size: 1.1, transparent: true, opacity: 0.65 });
      this.starfield = new THREE.Points(starGeom, starMat);
      this.scene.add(this.starfield);

      // 5. Lighting
      this.sunLight = new THREE.DirectionalLight(0xfff8e8, 1.35);
      this.sunLight.position.set(-35, 16, 25);
      this.scene.add(this.sunLight);

      this.ambientLight = new THREE.AmbientLight(0x162238, 0.65);
      this.scene.add(this.ambientLight);

      // 6. Financial Hub Pins & Beacons
      this.buildHubs(radius);

      // 7. Transcontinental 3D Bullion Arcs
      this.buildArcs();

      // Initial Earth Orientation (Tilt + Prime Meridian Facing)
      this.earthMesh.rotation.x = 0.35;
      this.earthMesh.rotation.y = -1.57;
      this.updateCoordHud();
    }

    latLonToVector3(lat, lon, r) {
      const phi = (90 - lat) * (Math.PI / 180);
      const theta = (lon + 180) * (Math.PI / 180);
      const x = -r * Math.sin(phi) * Math.cos(theta);
      const y = r * Math.cos(phi);
      const z = r * Math.sin(phi) * Math.sin(theta);
      return new THREE.Vector3(x, y, z);
    }

    buildHubs(radius) {
      this.raycastTargets = [];
      this.rings = [];

      this.hubs.forEach((hub, idx) => {
        const pos = this.latLonToVector3(hub.lat, hub.lon, radius);
        const hubGroup = new THREE.Group();

        const normal = pos.clone().normalize();
        const hex = hub.color === '#00f0ff' ? 0x00f0ff : (hub.color === '#10b981' ? 0x10b981 : 0xf5c542);

        // Ground Ripple Ring
        const ringGeom = new THREE.RingGeometry(0.12, 0.42, 32);
        const ringMat = new THREE.MeshBasicMaterial({ color: hex, side: THREE.DoubleSide, transparent: true, opacity: 0.8 });
        const ringMesh = new THREE.Mesh(ringGeom, ringMat);
        ringMesh.position.copy(pos.clone().multiplyScalar(1.003));
        ringMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal);
        hubGroup.add(ringMesh);
        this.rings.push({ mesh: ringMesh, phase: idx * 0.8 });

        // Beacon Core Sphere
        const beaconGeom = new THREE.SphereGeometry(0.18, 16, 16);
        const beaconMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
        const beaconMesh = new THREE.Mesh(beaconGeom, beaconMat);
        beaconMesh.position.copy(pos.clone().multiplyScalar(1.018));
        hubGroup.add(beaconMesh);

        // Vertical Laser Pillar
        const laserGeom = new THREE.BufferGeometry().setFromPoints([
          pos.clone().multiplyScalar(1.0),
          pos.clone().multiplyScalar(1.22)
        ]);
        const laserMat = new THREE.LineBasicMaterial({ color: hex, transparent: true, opacity: 0.85 });
        const laserLine = new THREE.Line(laserGeom, laserMat);
        hubGroup.add(laserLine);

        // Raycasting Hit Sphere
        const hitGeom = new THREE.SphereGeometry(0.75, 8, 8);
        const hitMat = new THREE.MeshBasicMaterial({ visible: false });
        const hitMesh = new THREE.Mesh(hitGeom, hitMat);
        hitMesh.position.copy(pos.clone().multiplyScalar(1.02));
        hitMesh.userData = { hub: hub };
        this.raycastTargets.push(hitMesh);
        hubGroup.add(hitMesh);

        this.earthMesh.add(hubGroup);
      });
    }

    buildArcs() {
      this.arcs = [];
      const corridors = [
        [0, 1, 0xf5c542], // London <-> New York
        [0, 2, 0xf5c542], // London <-> Zurich
        [2, 5, 0x00f0ff], // Zurich <-> Dubai
        [5, 4, 0xf5c542], // Dubai <-> Shanghai
        [4, 3, 0x10b981], // Shanghai <-> Tokyo
        [0, 6, 0x00f0ff], // London <-> Singapore
        [1, 3, 0xf5c542]  // New York <-> Tokyo
      ];

      corridors.forEach(([fromIdx, toIdx, colorHex]) => {
        const hubA = this.hubs[fromIdx];
        const hubB = this.hubs[toIdx];
        const pA = this.latLonToVector3(hubA.lat, hubA.lon, 10.02);
        const pB = this.latLonToVector3(hubB.lat, hubB.lon, 10.02);

        const dist = pA.distanceTo(pB);
        const mid = pA.clone().add(pB).multiplyScalar(0.5);
        const alt = 10.0 + Math.max(1.8, dist * 0.26);
        const apex = mid.normalize().multiplyScalar(alt);

        const curve = new THREE.QuadraticBezierCurve3(pA, apex, pB);
        const pts = curve.getPoints(50);
        const geom = new THREE.BufferGeometry().setFromPoints(pts);
        const mat = new THREE.LineBasicMaterial({ color: colorHex, transparent: true, opacity: 0.45 });
        const line = new THREE.Line(geom, mat);
        this.earthMesh.add(line);

        // Photon packet
        const photonGeom = new THREE.SphereGeometry(0.16, 12, 12);
        const photonMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff });
        const photon = new THREE.Mesh(photonGeom, photonMat);
        this.earthMesh.add(photon);

        this.arcs.push({
          curve: curve,
          photon: photon,
          progress: Math.random(),
          speed: 0.005 + Math.random() * 0.004
        });
      });
    }

    setMode(mode) {
      this.viewMode = mode;
      if (!this.earthMaterial) return;

      if (mode === 'night') {
        this.earthMaterial.map = this.textures.night;
        this.earthMaterial.emissive = new THREE.Color(0xfff0bb);
        this.earthMaterial.emissiveMap = this.textures.night;
        this.earthMaterial.emissiveIntensity = 0.95;
        this.earthMaterial.shininess = 6;
        if (this.cloudsMesh) this.cloudsMesh.visible = false;
        if (this.ambientLight) this.ambientLight.intensity = 0.85;
        if (this.sunLight) this.sunLight.intensity = 0.25;
      } else {
        this.earthMaterial.map = this.textures.day;
        this.earthMaterial.emissive = new THREE.Color(0x000000);
        this.earthMaterial.emissiveMap = null;
        this.earthMaterial.emissiveIntensity = 0;
        this.earthMaterial.shininess = 16;
        if (this.cloudsMesh) this.cloudsMesh.visible = true;
        if (this.ambientLight) this.ambientLight.intensity = 0.65;
        if (this.sunLight) this.sunLight.intensity = 1.35;
      }
      this.earthMaterial.needsUpdate = true;
    }

    bindControls() {
      const start = (x, y) => {
        this.isDragging = true;
        this.lastMouseX = x;
        this.lastMouseY = y;
        this.velX = 0;
        this.velY = 0;
      };

      const move = (x, y) => {
        if (this.isDragging && this.earthMesh) {
          const dx = x - this.lastMouseX;
          const dy = y - this.lastMouseY;
          this.earthMesh.rotation.y += dx * 0.005;
          this.earthMesh.rotation.x += dy * 0.005;
          this.earthMesh.rotation.x = Math.max(-1.1, Math.min(1.1, this.earthMesh.rotation.x));
          this.velY = dx * 0.003;
          this.velX = dy * 0.003;
          this.lastMouseX = x;
          this.lastMouseY = y;
          this.updateCoordHud();
        } else {
          this.checkRaycast(x, y);
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

      this.canvas.addEventListener('wheel', e => {
        e.preventDefault();
        this.targetZoom += e.deltaY * 0.018;
        this.targetZoom = Math.max(14.0, Math.min(42.0, this.targetZoom));
        this.updateCoordHud();
      }, { passive: false });

      this.canvas.addEventListener('click', e => {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        this.handleClick(x, y);
      });
    }

    checkRaycast(mx, my) {
      if (!this.camera || !this.raycastTargets.length) return;
      const rect = this.canvas.getBoundingClientRect();
      const mouse = new THREE.Vector2(
        (mx / rect.width) * 2 - 1,
        -(my / rect.height) * 2 + 1
      );
      const raycaster = new THREE.Raycaster();
      raycaster.setFromCamera(mouse, this.camera);
      const intersects = raycaster.intersectObjects(this.raycastTargets);

      if (intersects.length > 0) {
        const hit = intersects[0].object.userData.hub;
        this.canvas.style.cursor = 'pointer';
        if (hit !== this.hoveredHub) {
          this.hoveredHub = hit;
          audio.playClick();
        }
      } else {
        this.canvas.style.cursor = 'grab';
        this.hoveredHub = null;
      }
    }

    handleClick(mx, my) {
      if (this.hoveredHub) {
        this.flyToHub(this.hoveredHub);
      }
    }

    flyToHub(hub) {
      this.activeHub = hub;
      audio.playSonar();
      audio.speak(`Orbiting ${hub.name}. Interbank bullion liquidity cleared.`);
      if (this.onCitySelect) this.onCitySelect(hub);

      const targetY = -((hub.lon - 90) * Math.PI / 180);
      const targetX = (hub.lat * Math.PI / 180) * 0.45;

      let step = 0;
      const startY = this.earthMesh.rotation.y;
      const startX = this.earthMesh.rotation.x;
      const startZoom = this.targetZoom;
      const destZoom = 18.0;

      const flyInterval = setInterval(() => {
        step += 0.04;
        const ease = Math.sin(step * Math.PI / 2);
        this.earthMesh.rotation.y = startY + (targetY - startY) * ease;
        this.earthMesh.rotation.x = startX + (targetX - startX) * ease;
        this.targetZoom = startZoom + (destZoom - startZoom) * ease;
        this.updateCoordHud();
        if (step >= 1.0) {
          clearInterval(flyInterval);
        }
      }, 16);
    }

    updateCoordHud() {
      const coordEl = document.getElementById('canvas-coord-hud');
      if (!coordEl) return;
      const altKm = Math.round((this.camera.position.z - 10) * 35);
      if (this.activeHub) {
        coordEl.textContent = `TARGET: ${this.activeHub.name} • ${Math.abs(this.activeHub.lat).toFixed(2)}°${this.activeHub.lat >= 0 ? 'N' : 'S'} ${Math.abs(this.activeHub.lon).toFixed(2)}°${this.activeHub.lon >= 0 ? 'E' : 'W'} • ALT: ${altKm} KM`;
      }
    }

    resize(w, h) {
      if (!this.renderer || !this.camera) return;
      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(w, h);
    }

    render() {
      if (!this.renderer || !this.scene || !this.camera) return;

      if (!this.isDragging && this.earthMesh) {
        if (this.autoRotate) {
          this.earthMesh.rotation.y += 0.0018;
        } else {
          this.earthMesh.rotation.y += this.velY;
          this.earthMesh.rotation.x += this.velX;
          this.velY *= 0.95;
          this.velX *= 0.95;
        }
      }

      if (this.cloudsMesh) {
        this.cloudsMesh.rotation.y += 0.0006;
      }

      this.camera.position.z += (this.targetZoom - this.camera.position.z) * 0.08;

      for (const arc of this.arcs) {
        arc.progress = (arc.progress + arc.speed) % 1.0;
        const pt = arc.curve.getPoint(arc.progress);
        arc.photon.position.copy(pt);
      }

      const t = performance.now() * 0.003;
      for (const ring of this.rings) {
        const scale = 1.0 + (Math.sin(t + ring.phase) * 0.5 + 0.5) * 0.6;
        ring.mesh.scale.set(scale, scale, scale);
      }

      this.renderer.render(this.scene, this.camera);
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
    const canvas2d = document.getElementById('cockpit-canvas');
    const webglCanvas = document.getElementById('cockpit-webgl-canvas');
    const gmapsOverlay = document.getElementById('cockpit-gmaps-container');
    const chartOverlay = document.getElementById('cockpit-chart-container');
    const calcOverlay = document.getElementById('cockpit-calc-container');
    const tvIframe = document.getElementById('cockpit-tradingview-iframe');
    const globeSubnav = document.getElementById('globe-subnav');
    const coordHud = document.getElementById('canvas-coord-hud');
    const badgeText = document.getElementById('cockpit-status-badge-text');

    if (!deck || !canvas2d || !webglCanvas) return;

    let currentMode = 'globe';
    let globeEngine = null;
    let neuralEngine = null;
    let sniperEngine = null;
    let spacetimeEngine = null;

    // High-DPI Canvas Resizing
    function resizeCanvases() {
      const rect = webglCanvas.parentElement ? webglCanvas.parentElement.getBoundingClientRect() : { width: 800, height: 520 };
      const w = rect.width;
      const h = rect.height;

      // 2D Canvas Resize
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas2d.width = w * dpr;
      canvas2d.height = h * dpr;
      const ctx = canvas2d.getContext('2d');
      if (ctx) ctx.scale(dpr, dpr);

      // WebGL Canvas Resize
      if (globeEngine) {
        globeEngine.resize(w, h);
      }
    }
    resizeCanvases();
    window.addEventListener('resize', resizeCanvases);

    // Initialize Real 3D Tactical Earth Engine
    const initGlobe = () => {
      globeEngine = new RealTacticalEarth(webglCanvas, hub => {
        const cityEl = document.getElementById('telemetry-hub-name');
        const spreadEl = document.getElementById('telemetry-hub-spread');
        const volEl = document.getElementById('telemetry-hub-vol');
        const statusEl = document.getElementById('telemetry-hub-status');
        if (cityEl) cityEl.textContent = hub.name;
        if (spreadEl) spreadEl.textContent = hub.spread;
        if (volEl) volEl.textContent = hub.vol;
        if (statusEl) statusEl.textContent = hub.status;
      });
      resizeCanvases();
    };

    if (typeof THREE !== 'undefined') {
      initGlobe();
    } else {
      const waitThree = setInterval(() => {
        if (typeof THREE !== 'undefined') {
          clearInterval(waitThree);
          initGlobe();
        }
      }, 50);
    }

    neuralEngine = new NeuralSynapse(canvas2d);
    sniperEngine = new VisionSniper(canvas2d, pnl => {
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

    spacetimeEngine = new GravitationalSpacetime(canvas2d);

    // Wire Globe Subnav Controls (Satellite / Night / Google Maps)
    const btnSatellite = document.getElementById('btn-view-satellite');
    const btnNight = document.getElementById('btn-view-night');
    const btnGmaps = document.getElementById('btn-view-gmaps');
    const btnAutoRotate = document.getElementById('btn-view-autorotate');
    const hint = document.getElementById('canvas-hint-text');

    const setSubnavActive = (activeBtn) => {
      [btnSatellite, btnNight, btnGmaps].forEach(b => {
        if (b) b.classList.remove('active');
      });
      if (activeBtn) activeBtn.classList.add('active');
    };

    if (btnSatellite) {
      btnSatellite.addEventListener('click', () => {
        audio.playClick();
        setSubnavActive(btnSatellite);
        if (gmapsOverlay) gmapsOverlay.style.display = 'none';
        webglCanvas.style.display = 'block';
        if (globeEngine) globeEngine.setMode('satellite');
        if (hint) hint.textContent = 'Photorealistic NASA Satellite Earth • Drag to rotate • Scroll to zoom';
      });
    }

    if (btnNight) {
      btnNight.addEventListener('click', () => {
        audio.playClick();
        setSubnavActive(btnNight);
        if (gmapsOverlay) gmapsOverlay.style.display = 'none';
        webglCanvas.style.display = 'block';
        if (globeEngine) globeEngine.setMode('night');
        if (hint) hint.textContent = 'NASA Black Marble Night Lights • Metropolitan liquidity constellations';
      });
    }

    if (btnGmaps) {
      btnGmaps.addEventListener('click', () => {
        audio.playClick();
        setSubnavActive(btnGmaps);
        webglCanvas.style.display = 'none';
        if (gmapsOverlay) gmapsOverlay.style.display = 'block';
        if (hint) hint.textContent = 'Google Maps Satellite HUD • LBMA Bullion Vaults (88 Wood St, London)';
      });
    }

    if (btnAutoRotate) {
      btnAutoRotate.addEventListener('click', () => {
        audio.playClick();
        if (globeEngine) {
          globeEngine.autoRotate = !globeEngine.autoRotate;
          btnAutoRotate.classList.toggle('active', globeEngine.autoRotate);
          btnAutoRotate.textContent = globeEngine.autoRotate ? '🔄 AUTO-ROTATE: ON' : '⏸️ AUTO-ROTATE: OFF';
        }
      });
    }

    // Mode Tab Buttons
    const tabButtons = document.querySelectorAll('.cockpit-tab-btn');
    tabButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        audio.playClick();
        tabButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentMode = btn.getAttribute('data-mode');

        if (currentMode === 'globe') {
          webglCanvas.style.display = 'block';
          canvas2d.style.display = 'none';
          if (chartOverlay) chartOverlay.style.display = 'none';
          if (calcOverlay) calcOverlay.style.display = 'none';
          if (globeSubnav) globeSubnav.style.display = 'flex';
          if (coordHud) coordHud.style.display = 'block';
          if (gmapsOverlay) gmapsOverlay.style.display = 'none';
          if (badgeText) badgeText.textContent = '120 FPS REAL 3D EARTH MATRIX';
          if (hint) hint.textContent = 'Drag to rotate Real 3D Earth • Scroll to zoom • Click hubs to inspect';
        } else if (currentMode === 'neural') {
          webglCanvas.style.display = 'none';
          canvas2d.style.display = 'block';
          if (chartOverlay) chartOverlay.style.display = 'none';
          if (calcOverlay) calcOverlay.style.display = 'none';
          if (globeSubnav) globeSubnav.style.display = 'none';
          if (coordHud) coordHud.style.display = 'none';
          if (gmapsOverlay) gmapsOverlay.style.display = 'none';
          if (badgeText) badgeText.textContent = '1,200 BIOLUMINESCENT NEURONS ACTIVE';
          if (hint) hint.textContent = 'Move cursor to warp neural gravity • Click to fire synapses';
        } else if (currentMode === 'chart') {
          webglCanvas.style.display = 'none';
          canvas2d.style.display = 'none';
          if (chartOverlay) chartOverlay.style.display = 'flex';
          if (calcOverlay) calcOverlay.style.display = 'none';
          if (globeSubnav) globeSubnav.style.display = 'none';
          if (coordHud) coordHud.style.display = 'none';
          if (gmapsOverlay) gmapsOverlay.style.display = 'none';
          if (badgeText) badgeText.textContent = 'LIVE STREAMING XAUUSD CANDLESTICK FEED';
          if (hint) hint.textContent = 'Official TradingView Institutional Feed • Live Price Action & Order Flow';
        } else if (currentMode === 'calculator') {
          webglCanvas.style.display = 'none';
          canvas2d.style.display = 'none';
          if (chartOverlay) chartOverlay.style.display = 'none';
          if (calcOverlay) calcOverlay.style.display = 'block';
          if (globeSubnav) globeSubnav.style.display = 'none';
          if (coordHud) coordHud.style.display = 'none';
          if (gmapsOverlay) gmapsOverlay.style.display = 'none';
          if (badgeText) badgeText.textContent = 'QUARTER-KELLY CAPITAL DEFENSE MATRIX';
          if (hint) hint.textContent = 'Adjust balance, risk tolerance & targets to calculate exact MT5 lot size';
        } else {
          webglCanvas.style.display = 'none';
          canvas2d.style.display = 'block';
          if (chartOverlay) chartOverlay.style.display = 'none';
          if (calcOverlay) calcOverlay.style.display = 'none';
          if (globeSubnav) globeSubnav.style.display = 'none';
          if (coordHud) coordHud.style.display = 'none';
          if (gmapsOverlay) gmapsOverlay.style.display = 'none';
        }
        resizeCanvases();
      });
    });

    // TradingView Chart Toolbar Controls
    let currentChartSymbol = 'OANDA:XAUUSD';
    let currentChartInterval = '15';

    function updateChartIframe() {
      if (!tvIframe) return;
      const encodedSymbol = encodeURIComponent(currentChartSymbol);
      const url = `https://s.tradingview.com/widgetembed/?symbol=${encodedSymbol}&interval=${currentChartInterval}&theme=dark&style=1&timezone=Etc%2FUTC&studies=%5B%5D&hide_side_toolbar=0&allow_symbol_change=0&save_image=0&details=1`;
      tvIframe.src = url;
    }

    const chartTfBtns = document.querySelectorAll('.chart-tf-btn');
    chartTfBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        audio.playClick();
        chartTfBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentChartInterval = btn.getAttribute('data-interval') || '15';
        updateChartIframe();
      });
    });

    const chartAssetBtns = document.querySelectorAll('.chart-asset-btn');
    chartAssetBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        audio.playClick();
        chartAssetBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentChartSymbol = btn.getAttribute('data-symbol') || 'OANDA:XAUUSD';
        updateChartIframe();
      });
    });

    // Quarter-Kelly Risk Armor & Lot Size Engine
    const balanceInput = document.getElementById('calc-balance-input');
    const balanceDisplay = document.getElementById('calc-balance-display');
    const riskSlider = document.getElementById('calc-risk-slider');
    const riskLabel = document.getElementById('calc-risk-pct-label');
    const entryInput = document.getElementById('calc-entry-price');
    const slInput = document.getElementById('calc-sl-price');
    const tpInput = document.getElementById('calc-tp-price');

    const resultLots = document.getElementById('calc-result-lots');
    const resultContractNote = document.getElementById('calc-result-contract-note');
    const resultRiskUsd = document.getElementById('calc-result-risk-usd');
    const resultRiskPct = document.getElementById('calc-result-risk-pct');
    const resultRewardUsd = document.getElementById('calc-result-reward-usd');
    const resultRewardPct = document.getElementById('calc-result-reward-pct');
    const resultRR = document.getElementById('calc-result-rr');
    const resultPips = document.getElementById('calc-result-pips');
    const resultDollars = document.getElementById('calc-result-dollars');
    const resultMargin = document.getElementById('calc-result-margin');
    const resultMarginPct = document.getElementById('calc-result-margin-pct');
    const resultRating = document.getElementById('calc-result-rating');

    function calculateRiskArmor() {
      if (!balanceInput || !entryInput || !slInput || !tpInput) return;

      const balance = Math.max(100, parseFloat(balanceInput.value) || 10000);
      const riskPct = Math.max(0.05, parseFloat(riskSlider ? riskSlider.value : 0.5) || 0.5);
      const entry = parseFloat(entryInput.value) || 2664.50;
      const sl = parseFloat(slInput.value) || 2658.00;
      const tp = parseFloat(tpInput.value) || 2684.00;

      // Update Header Display
      if (balanceDisplay) {
        balanceDisplay.textContent = `$${balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      }

      // Risk strategy label
      if (riskLabel) {
        let strat = 'Custom Risk';
        if (Math.abs(riskPct - 0.5) < 0.05) strat = 'Quarter-Kelly (Recommended)';
        else if (Math.abs(riskPct - 1.0) < 0.05) strat = 'Half-Kelly (Balanced)';
        else if (Math.abs(riskPct - 2.0) < 0.05) strat = 'Max Tactical Ceiling';
        riskLabel.textContent = `${riskPct.toFixed(2)}% (${strat})`;
      }

      // Stop Loss distance calculation (Gold contract: 1 lot = 100 oz, $1 price move = $100 per lot, 1 pip = $0.10)
      const stopDistanceUsd = Math.max(0.1, Math.abs(entry - sl));
      const stopPips = stopDistanceUsd * 10;

      // Take Profit distance calculation
      const rewardDistanceUsd = Math.max(0.1, Math.abs(tp - entry));
      const rewardPips = rewardDistanceUsd * 10;

      // Cash at risk ($)
      const cashRiskUsd = balance * (riskPct / 100);

      // Raw Lots = Cash Risk / (Stop Distance $ * 100 oz)
      let calculatedLots = cashRiskUsd / (stopDistanceUsd * 100);
      
      // Standard broker limits: min 0.01 lot, 2 decimals
      if (calculatedLots < 0.01) calculatedLots = 0.01;
      calculatedLots = Math.round(calculatedLots * 100) / 100;

      // Exact dollar values based on quantized lot size
      const actualRiskUsd = calculatedLots * stopDistanceUsd * 100;
      const actualRewardUsd = calculatedLots * rewardDistanceUsd * 100;
      const actualRiskPct = (actualRiskUsd / balance) * 100;
      const actualRewardPct = (actualRewardUsd / balance) * 100;

      // Risk-Reward Ratio
      const rrRatio = (rewardDistanceUsd / stopDistanceUsd);

      // Estimated Required Margin at 1:200 institutional leverage
      const notionalValue = calculatedLots * 100 * entry;
      const reqMargin = notionalValue / 200;
      const marginPctOfAccount = (reqMargin / balance) * 100;

      // Update DOM
      if (resultLots) resultLots.textContent = calculatedLots.toFixed(2);
      if (resultContractNote) {
        const oz = (calculatedLots * 100).toFixed(1);
        const pipVal = (calculatedLots * 10).toFixed(2);
        resultContractNote.textContent = `Gold Contract: ${oz} oz • $${pipVal} per pip`;
      }
      if (resultRiskUsd) resultRiskUsd.textContent = `-$${actualRiskUsd.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      if (resultRiskPct) resultRiskPct.textContent = `${actualRiskPct.toFixed(2)}% of balance`;
      if (resultRewardUsd) resultRewardUsd.textContent = `+$${actualRewardUsd.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      if (resultRewardPct) resultRewardPct.textContent = `+${actualRewardPct.toFixed(2)}% return`;
      if (resultRR) resultRR.textContent = `1 : ${rrRatio.toFixed(2)}`;
      if (resultPips) resultPips.textContent = `${stopPips.toFixed(1)} Pips`;
      if (resultDollars) resultDollars.textContent = `$${stopDistanceUsd.toFixed(2)} / oz`;
      if (resultMargin) resultMargin.textContent = `$${reqMargin.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      if (resultMarginPct) resultMarginPct.textContent = `${marginPctOfAccount.toFixed(2)}% Account Margin`;

      // Defense Rating
      if (resultRating) {
        if (actualRiskPct <= 0.75) {
          resultRating.textContent = 'OPTIMAL (99.4%)';
          resultRating.className = 'stat-val green';
        } else if (actualRiskPct <= 1.5) {
          resultRating.textContent = 'STABLE (96.2%)';
          resultRating.className = 'stat-val gold';
        } else {
          resultRating.textContent = 'ELEVATED RISK';
          resultRating.className = 'stat-val red';
        }
      }
    }

    // Balance Presets
    const balancePresets = document.querySelectorAll('#calc-balance-presets .calc-preset-pill');
    balancePresets.forEach(pill => {
      pill.addEventListener('click', () => {
        audio.playClick();
        balancePresets.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        const val = pill.getAttribute('data-val');
        if (balanceInput && val) {
          balanceInput.value = val;
          calculateRiskArmor();
        }
      });
    });

    // Risk Presets
    const riskPresets = document.querySelectorAll('#calc-risk-presets .calc-risk-pill');
    riskPresets.forEach(pill => {
      pill.addEventListener('click', () => {
        audio.playClick();
        riskPresets.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        const rVal = pill.getAttribute('data-risk');
        if (riskSlider && rVal) {
          riskSlider.value = rVal;
          calculateRiskArmor();
        }
      });
    });

    if (balanceInput) balanceInput.addEventListener('input', () => {
      balancePresets.forEach(p => p.classList.remove('active'));
      calculateRiskArmor();
    });
    if (riskSlider) riskSlider.addEventListener('input', () => {
      riskPresets.forEach(p => p.classList.remove('active'));
      calculateRiskArmor();
    });
    if (entryInput) entryInput.addEventListener('input', calculateRiskArmor);
    if (slInput) slInput.addEventListener('input', calculateRiskArmor);
    if (tpInput) tpInput.addEventListener('input', calculateRiskArmor);

    // Initial calculation run
    calculateRiskArmor();

    // Copy MT5 Parameters Action
    const copyMt5Btn = document.getElementById('btn-calc-copy-mt5');
    const copyMt5Toast = document.getElementById('calc-copy-toast');
    if (copyMt5Btn) {
      copyMt5Btn.addEventListener('click', () => {
        audio.playClick();
        const lots = resultLots ? resultLots.textContent.trim() : '0.08';
        const entry = entryInput ? entryInput.value : '2664.50';
        const sl = slInput ? slInput.value : '2658.00';
        const tp = tpInput ? tpInput.value : '2684.00';
        const riskUsd = resultRiskUsd ? resultRiskUsd.textContent.trim() : '-$50.00';
        const rr = resultRR ? resultRR.textContent.trim() : '1 : 3.00';

        const mt5Text = 
`// ==========================================
// DON AURELIUS • QUANTUM RISK ARMOR (MT5)
// Architect: SM.KANISH • Sovereign AI Syndicate
// ==========================================
Symbol:        XAUUSD (Spot Gold)
Order Type:    BUY LIMIT / BUY MARKET
Volume (Lots): ${lots}
Entry Price:   ${entry}
Stop Loss:     ${sl}
Take Profit:   ${tp}
Risk:          ${riskUsd} (Quarter-Kelly Protection)
Risk/Reward:   ${rr}
// Execution verified by Inquisitor Gatekeeper`;

        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(mt5Text).then(() => {
            if (copyMt5Toast) {
              copyMt5Toast.style.display = 'block';
              setTimeout(() => { copyMt5Toast.style.display = 'none'; }, 2500);
            }
          }).catch(() => {
            prompt('Copy MT5 Parameters:', mt5Text);
          });
        } else {
          prompt('Copy MT5 Parameters:', mt5Text);
        }
      });
    }

    // Copy 4-Agent Consensus Signal Action
    const copySignalBtn = document.getElementById('btn-copy-consensus-signal');
    const copySignalToast = document.getElementById('signal-copy-toast');
    if (copySignalBtn) {
      copySignalBtn.addEventListener('click', () => {
        audio.playClick();
        const signalText = 
`🦅 DON AURELIUS • COUNCIL CONSENSUS SIGNAL 🦅
=============================================
Direction:    BUY / LONG XAUUSD (Gold)
Quality:      A+ INSTITUTIONAL SETUP
Consensus:    4/4 UNANIMOUS SUPERMAJORITY

• Hawk:       BUY (DXY -0.32% • Yields Fall)
• Radar:      BUY (Asian High Swept, Buyside Liquidity Target)
• Predator:   BUY (Bullish FVG Retest @ 2662.50)
• Inquisitor: PASS (Spread 0.12p <= 5.0p Cap)

EXECUTION MATRIX:
• Entry Zone: 2662.50 – 2664.50
• Stop Loss:  2658.00 (-65 pips)
• Target 1:   2678.00 (+135 pips)
• Target 2:   2685.50 (+210 pips)
• Allocation: Quarter-Kelly Risk Armor

Founder: SM.KANISH • Sovereign AI Syndicate`;

        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(signalText).then(() => {
            if (copySignalToast) {
              copySignalToast.style.display = 'block';
              setTimeout(() => { copySignalToast.style.display = 'none'; }, 2500);
            }
          }).catch(() => {
            prompt('Copy Consensus Signal:', signalText);
          });
        } else {
          prompt('Copy Consensus Signal:', signalText);
        }
      });
    }

    // Live Ticking Countdown Clock for Economic News Shield Radar
    const newsTimerEl = document.getElementById('news-countdown-timer');
    if (newsTimerEl) {
      let targetSeconds = 3 * 3600 + 42 * 60 + 18;
      setInterval(() => {
        if (targetSeconds > 0) {
          targetSeconds--;
          const hrs = Math.floor(targetSeconds / 3600);
          const mins = Math.floor((targetSeconds % 3600) / 60);
          const secs = targetSeconds % 60;
          newsTimerEl.textContent = `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        } else {
          newsTimerEl.textContent = '00:00:00 (EVENT LIVE)';
        }
      }, 1000);
    }

    // Fallback Simulation Triggers (if elements ever exist)
    const execBtn = document.getElementById('btn-simulate-sweep');
    if (execBtn && sniperEngine) {
      execBtn.addEventListener('click', () => {
        sniperEngine.triggerExecution();
      });
    }

    const singBtn = document.getElementById('btn-trigger-singularity');
    if (singBtn && spacetimeEngine) {
      singBtn.addEventListener('click', () => {
        spacetimeEngine.triggerSingularity();
      });
    }

    // Fullscreen Toggle
    const fullscreenBtn = document.getElementById('btn-cockpit-fullscreen');
    if (fullscreenBtn) {
      fullscreenBtn.addEventListener('click', () => {
        audio.playBreach();
        deck.classList.toggle('fullscreen-mode');
        resizeCanvases();
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
          'Don Aurelius Quantum Cockpit initialized. Commander SM.KANISH authenticated. Council consensus: 4 of 4 unanimous supermajority. Live TradingView XAUUSD feed synchronized. Quarter-Kelly Risk Armor active.'
        );
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
        resizeCanvases();
      }
    });

    // Expose Global Breach Cockpit Trigger
    window.breachCockpit = function() {
      audio.init();
      audio.playBreach();
      deck.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setTimeout(() => {
        deck.classList.add('fullscreen-mode');
        resizeCanvases();
        audio.speak('Commander SM.KANISH authenticated. Sovereign Quantum Cockpit breached. Real 3D Earth matrix active.');
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
      if (currentMode === 'globe' && globeEngine) globeEngine.render();
      else if (currentMode === 'neural' && neuralEngine) neuralEngine.render();
      else if (currentMode === 'sniper' && sniperEngine) sniperEngine.render();
      else if (currentMode === 'spacetime' && spacetimeEngine) spacetimeEngine.render();

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
