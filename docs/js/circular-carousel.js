/**
 * CircularCarousel (Pure Vanilla Engine)
 * High-performance 3D Spatial Cylinder Carousel matching React Bits specification
 * Conceived for Don Aurelius Sovereign Syndicate
 */

(function () {
  'use strict';

  const PRESETS = {
    cylinder: {
      axis: 'y',
      tilt: -5,
      perspective: 2500,
      curve: 1,
      spread: 1,
      inward: false,
      billboard: false,
      backfaces: true,
      window: 0
    },
    orbit: {
      axis: 'y',
      tilt: -16,
      perspective: 1500,
      curve: 0,
      spread: 1.45,
      inward: false,
      billboard: true,
      backfaces: false,
      window: 0
    },
    wheel: {
      axis: 'x',
      tilt: 0,
      perspective: 1800,
      curve: 0,
      spread: 1,
      inward: false,
      billboard: false,
      backfaces: true,
      window: 1.7
    },
    panorama: {
      axis: 'y',
      tilt: 0,
      perspective: 0,
      curve: 1,
      spread: 1,
      inward: true,
      billboard: false,
      backfaces: false,
      window: 0
    }
  };

  const INTRO_LENGTH = { assemble: 1500, rise: 1400, spin: 1800, none: 0 };
  const TILES = 8;
  const OVERLAP = 2.5;
  const DRAG_THRESHOLD = 5;
  const SPRING = 118;
  const SETTLE_SPEED = 9;
  const CAPTION_SPACE = 76;
  const TO_RAD = Math.PI / 180;

  const clamp = (v, min, max) => Math.min(max, Math.max(min, v));
  const wrap = deg => ((((deg + 180) % 360) + 360) % 360) - 180;
  const easeOut = t => 1 - Math.pow(1 - t, 4);
  const easeOutQuint = t => 1 - Math.pow(1 - t, 5);

  const rotateX = (p, deg) => {
    const r = deg * TO_RAD;
    const c = Math.cos(r);
    const s = Math.sin(r);
    return [p[0], p[1] * c - p[2] * s, p[1] * s + p[2] * c];
  };

  const rotateY = (p, deg) => {
    const r = deg * TO_RAD;
    const c = Math.cos(r);
    const s = Math.sin(r);
    return [p[0] * c + p[2] * s, p[1], -p[0] * s + p[2] * c];
  };

  function initCircularCarousel(container, options = {}) {
    if (!container) return;

    const items = options.items || [];
    if (!items.length) return;

    const count = items.length;
    const preset = options.preset || 'cylinder';
    const shape = PRESETS[preset] ? preset : 'cylinder';
    const layout = PRESETS[shape];
    const axis = layout.axis;
    const tiltValue = options.tilt !== undefined ? options.tilt : layout.tilt;
    const curveValue = layout.billboard ? 0 : clamp(options.curve !== undefined ? options.curve : layout.curve, 0, 1);
    const cardWidth = options.cardWidth || 220;
    const aspectRatio = options.aspectRatio || 1;
    const gap = options.gap !== undefined ? options.gap : 25;
    const autoplay = options.autoplay || 'drift';
    const speed = options.speed !== undefined ? options.speed : 14;
    const interval = Math.max(0.5, options.interval || 3);
    const direction = options.direction || 'left';
    const draggable = options.draggable !== false;
    const momentum = clamp(options.momentum !== undefined ? options.momentum : 0.6, 0, 1);
    const snap = options.snap !== false;
    const pauseOnHover = options.pauseOnHover !== false;
    const focusOnClick = options.focusOnClick !== false;
    const parallax = clamp(options.parallax !== undefined ? options.parallax : 0.3, 0, 1);
    const stretch = clamp(options.stretch !== undefined ? options.stretch : 0.5, 0, 1);
    const depthFade = clamp(options.depthFade !== undefined ? options.depthFade : 0.55, 0, 1);
    const fadeColor = options.fadeColor || '#020306';
    const innerShade = clamp(options.innerShade !== undefined ? options.innerShade : 0.6, 0, 1);
    const cornerRadius = options.cornerRadius !== undefined ? options.cornerRadius : 14;
    const captions = options.captions !== false;
    const intro = options.intro || 'rise';

    const cardW = Math.max(40, cardWidth);
    const cardH = cardW / clamp(aspectRatio, 0.2, 5);
    const along = axis === 'x' ? cardH : cardW;
    const step = 360 / count;

    // Radius calculation
    const n = Math.max(count, 3);
    const pitch = (along + gap) * layout.spread;
    const chord = pitch / (2 * Math.sin(Math.PI / n));
    const arc = (n * pitch) / (2 * Math.PI);
    const radius = Math.max(chord + (arc - chord) * curveValue, along * 0.6);
    const perspective = layout.inward ? radius : (options.perspective !== undefined ? options.perspective : layout.perspective);

    // Tiles calculation
    const total = curveValue > 0.001 ? TILES : 1;
    const length = along / total;
    const bend = curveValue > 0.001 ? radius / curveValue : 0;
    const tiles = Array.from({ length: total }, (_, index) => {
      const start = index * length - (index > 0 ? OVERLAP / 2 : 0);
      const end = (index + 1) * length + (index < total - 1 ? OVERLAP / 2 : 0);
      const center = (start + end) / 2 - along / 2;
      const alpha = bend ? center / bend : 0;
      const shift = bend ? bend * Math.sin(alpha) : center;
      const sink = bend ? bend * (1 - Math.cos(alpha)) : 0;
      const depth = layout.inward ? sink : -sink;
      const turn = ((layout.inward ? -alpha : alpha) * 180) / Math.PI;
      const move =
        axis === 'x'
          ? `translate3d(0px, ${shift}px, ${depth}px) rotateX(${-turn}deg)`
          : `translate3d(${shift}px, 0px, ${depth}px) rotateY(${turn}deg)`;
      return { index, total, start, end, size: end - start, move };
    });

    // Build DOM structure
    container.innerHTML = '';
    const root = document.createElement('div');
    root.className = `circular-carousel ${options.className || ''}`.trim();
    root.style.setProperty('--cc-fade', fadeColor);
    root.style.setProperty('--cc-radius', `${Math.max(0, cornerRadius)}px`);
    root.style.setProperty('--cc-inner', (1 - innerShade).toFixed(3));
    root.setAttribute('role', 'region');
    root.setAttribute('aria-roledescription', 'carousel');
    root.setAttribute('aria-label', 'Don Aurelius Syndicate Matrix');
    root.setAttribute('tabindex', '0');
    root.setAttribute('data-axis', axis);
    root.setAttribute('data-shape', shape);
    if (draggable) root.setAttribute('data-draggable', '');

    const view = document.createElement('div');
    view.className = 'circular-carousel__view';

    const stage = document.createElement('div');
    stage.className = 'circular-carousel__stage';

    const camera = document.createElement('div');
    camera.className = 'circular-carousel__camera';

    const ring = document.createElement('div');
    ring.className = 'circular-carousel__ring';

    const cardElements = [];

    items.forEach((item, index) => {
      const card = document.createElement('div');
      card.className = 'circular-carousel__card';
      card.setAttribute('data-cc-index', String(index));
      card.setAttribute('role', 'group');
      card.setAttribute('aria-roledescription', 'slide');
      card.setAttribute('aria-label', `${item.title || item.alt || `Item ${index + 1}`}, ${index + 1} of ${count}`);

      tiles.forEach(tile => {
        card.appendChild(renderTile(item, tile, false, along, cardW, cardH, axis));
      });
      if (layout.backfaces) {
        tiles.forEach(tile => {
          card.appendChild(renderTile(item, tile, true, along, cardW, cardH, axis));
        });
      }

      ring.appendChild(card);
      cardElements.push(card);
    });

    camera.appendChild(ring);
    stage.appendChild(camera);
    view.appendChild(stage);
    root.appendChild(view);

    // Caption Element
    let captionEl = null;
    let titleEl = null;
    let subtitleEl = null;
    let countEl = null;

    if (captions) {
      captionEl = document.createElement('div');
      captionEl.className = 'circular-carousel__caption';
      captionEl.setAttribute('aria-hidden', 'true');

      const titleWrap = document.createElement('span');
      titleWrap.className = 'circular-carousel__title';
      titleEl = document.createElement('span');
      titleEl.className = 'circular-carousel__title-text';
      subtitleEl = document.createElement('span');
      subtitleEl.className = 'circular-carousel__subtitle';
      titleWrap.appendChild(titleEl);
      titleWrap.appendChild(subtitleEl);

      countEl = document.createElement('span');
      countEl.className = 'circular-carousel__count';

      // 2 reel digits
      const digitsEl = document.createElement('span');
      digitsEl.className = 'circular-carousel__digits';
      for (let d = 0; d < 2; d++) {
        const digitBox = document.createElement('span');
        digitBox.className = 'circular-carousel__digit';
        const reel = document.createElement('span');
        reel.className = 'circular-carousel__reel';
        for (let num = 0; num <= 9; num++) {
          const nSpan = document.createElement('span');
          nSpan.textContent = String(num);
          reel.appendChild(nSpan);
        }
        digitBox.appendChild(reel);
        digitsEl.appendChild(digitBox);
      }

      const slash = document.createElement('span');
      slash.className = 'circular-carousel__slash';
      slash.textContent = '/';

      const totalSpan = document.createElement('span');
      totalSpan.textContent = String(count).padStart(2, '0');

      countEl.appendChild(digitsEl);
      countEl.appendChild(slash);
      countEl.appendChild(totalSpan);

      captionEl.appendChild(titleWrap);
      captionEl.appendChild(countEl);
      root.appendChild(captionEl);
    }

    const liveRegion = document.createElement('div');
    liveRegion.className = 'circular-carousel__live';
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    root.appendChild(liveRegion);

    container.appendChild(root);

    // State
    const dragSign = layout.inward ? -1 : 1;
    const directionSign = (direction === 'right' ? 1 : -1) * dragSign;

    const state = {
      angle: 0,
      velocity: 0,
      target: null,
      dir: directionSign,
      press: null,
      drag: false,
      hover: false,
      pointer: { inside: false, x: 0, y: 0 },
      yaw: 0,
      pitch: 0,
      intro: null,
      introDone: false,
      holdUntil: 0,
      stepAt: 0,
      suppressClick: false,
      wheelTimer: 0,
      fit: 1,
      shift: 0,
      drop: 0,
      last: 0,
      active: -1,
      ready: false
    };

    let raf = 0;
    let isVisible = true;

    function renderTile(item, tile, back, along, cardW, cardH, axis) {
      const strip = back ? tile.total - 1 - tile.index : tile.index;
      const first = strip === 0;
      const last = strip === tile.total - 1;
      const r = 'var(--cc-radius, 14px)';
      const frameRadius =
        axis === 'x'
          ? `${first ? r : '0px'} ${first ? r : '0px'} ${last ? r : '0px'} ${last ? r : '0px'}`
          : `${first ? r : '0px'} ${last ? r : '0px'} ${last ? r : '0px'} ${first ? r : '0px'}`;
      const offset = back ? along - tile.end : tile.start;
      const size = tile.size;
      const box =
        axis === 'x'
          ? { left: `${-cardW / 2}px`, top: `${-size / 2}px`, width: `${cardW}px`, height: `${size}px` }
          : { left: `${-size / 2}px`, top: `${-cardH / 2}px`, width: `${size}px`, height: `${cardH}px` };
      const photoStyle =
        axis === 'x'
          ? { left: '0px', top: `${-offset}px`, width: `${cardW}px`, height: `${cardH}px` }
          : { left: `${-offset}px`, top: '0px', width: `${cardW}px`, height: `${cardH}px` };
      const flip = axis === 'x' ? ' rotateX(180deg)' : ' rotateY(180deg)';

      const tileEl = document.createElement('div');
      tileEl.className = 'circular-carousel__tile';
      tileEl.setAttribute('aria-hidden', 'true');
      Object.assign(tileEl.style, box);
      tileEl.style.transform = tile.move + (back ? flip : '');

      const frameEl = document.createElement('div');
      frameEl.className = 'circular-carousel__frame';
      frameEl.style.height = axis === 'x' ? `${size}px` : `${cardH}px`;
      frameEl.style.borderRadius = frameRadius;

      const imgEl = document.createElement('img');
      imgEl.className = 'circular-carousel__photo';
      imgEl.src = item.src;
      imgEl.alt = '';
      imgEl.draggable = false;
      imgEl.decoding = 'async';
      Object.assign(imgEl.style, photoStyle);
      frameEl.appendChild(imgEl);

      if (back) {
        const innerEl = document.createElement('div');
        innerEl.className = 'circular-carousel__inner';
        frameEl.appendChild(innerEl);
      }

      const shadeEl = document.createElement('div');
      shadeEl.className = 'circular-carousel__shade';
      frameEl.appendChild(shadeEl);

      tileEl.appendChild(frameEl);
      return tileEl;
    }

    function nearest(angle) {
      return Math.round(angle / step) * step;
    }

    function measure() {
      const rect = root.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      const room = captions ? CAPTION_SPACE : 0;
      const width = rect.width * 0.94;
      const height = (rect.height - room) * 0.92;
      const P = perspective;
      let minX = Infinity;
      let maxX = -Infinity;
      let minY = Infinity;
      let maxY = -Infinity;

      if (layout.inward) {
        minX = -width / 2;
        maxX = width / 2;
        minY = -cardH / 2;
        maxY = cardH / 2;
      } else {
        const corners = [
          [-cardW / 2, -cardH / 2],
          [cardW / 2, -cardH / 2],
          [-cardW / 2, cardH / 2],
          [cardW / 2, cardH / 2]
        ];
        const limit = layout.window ? layout.window * step : 180;
        for (let a = -limit; a <= limit; a += limit / 24) {
          for (const [cx, cy] of corners) {
            let p;
            if (axis === 'x') {
              p = rotateX([cx, cy, radius], -a);
              p = [p[0], p[1], p[2] - radius];
              p = rotateY(p, tiltValue);
            } else if (layout.billboard) {
              const c = rotateY([0, 0, radius], a);
              p = [c[0] + cx, cy, c[2] - radius];
              p = rotateX(p, tiltValue);
            } else {
              p = rotateY([cx, cy, radius], a);
              p = [p[0], p[1], p[2] - radius];
              p = rotateX(p, tiltValue);
            }
            if (p[2] >= P * 0.95) continue;
            const k = P / (P - p[2]);
            minX = Math.min(minX, p[0] * k);
            maxX = Math.max(maxX, p[0] * k);
            minY = Math.min(minY, p[1] * k);
            maxY = Math.max(maxY, p[1] * k);
          }
        }
      }
      const spanX = Math.max(maxX - minX, 1);
      const spanY = Math.max(maxY - minY, 1);
      const fit = Math.min(1, width / spanX, height / spanY);
      state.fit = fit;
      state.shift = -((minY + maxY) / 2) * fit - room / 2;
      state.drop = axis === 'x' ? (rect.width / fit) * 0.55 + cardW : (rect.height / fit) * 0.55 + cardH;
      stage.style.perspective = `${P}px`;
      stage.style.transform = `translate3d(0, ${state.shift}px, 0) scale(${fit})`;
    }

    function introCard(elapsed, landing) {
      if (!state.intro) return { radius: 1, lift: 0 };
      const type = state.intro.type;
      const reach = Math.abs(wrap(landing + state.angle));
      if (type === 'assemble') {
        const delay = (reach / 180) * 420;
        const p = easeOut(clamp((elapsed - delay) / 1080, 0, 1));
        return { radius: 1 + 0.6 * (1 - p), lift: 0 };
      }
      if (type === 'rise') {
        const delay = (reach / 180) * 480;
        const p = easeOutQuint(clamp((elapsed - delay) / 900, 0, 1));
        return { radius: 1, lift: (1 - p) * state.drop };
      }
      if (type === 'spin') {
        const p = easeOut(clamp(elapsed / INTRO_LENGTH.spin, 0, 1));
        return { radius: 1 + 0.28 * (1 - p), lift: 0 };
      }
      return { radius: 1, lift: 0 };
    }

    function advance(dt, now) {
      if (!state.introDone && state.ready) {
        if (!state.intro) {
          if (intro === 'none') state.introDone = true;
          else state.intro = { type: intro, start: now };
        }
        if (state.intro && now - state.intro.start >= INTRO_LENGTH[state.intro.type]) {
          state.intro = null;
          state.introDone = true;
        }
      }

      const paused = (pauseOnHover && state.hover) || state.drag || now < state.holdUntil;
      const cruise = autoplay === 'drift' && !paused && !state.intro ? speed * state.dir : 0;
      let busy = Boolean(state.intro) || state.drag;

      if (state.drag || state.intro) {
        state.velocity = state.drag ? state.velocity : 0;
      } else if (state.target !== null) {
        let remaining = dt;
        const damping = 2 * Math.sqrt(SPRING);
        while (remaining > 0) {
          const h = Math.min(remaining, 1 / 240);
          const accel = SPRING * (state.target - state.angle) - damping * state.velocity;
          state.velocity += accel * h;
          state.angle += state.velocity * h;
          remaining -= h;
        }
        if (Math.abs(state.target - state.angle) < 0.004 && Math.abs(state.velocity) < 0.03) {
          state.angle = state.target;
          state.velocity = 0;
          state.target = null;
        }
        busy = true;
      } else {
        const tau = 0.18 + momentum * 1.5;
        state.velocity += (cruise - state.velocity) * (1 - Math.exp(-dt / tau));
        state.angle += state.velocity * dt;
        if (cruise === 0 && snap && Math.abs(state.velocity) < SETTLE_SPEED) {
          state.target = nearest(state.angle);
        }
        busy = busy || cruise !== 0 || Math.abs(state.velocity) > 0.01 || state.target !== null;
      }

      if (autoplay === 'step' && !paused && !state.intro && state.introDone) {
        if (!state.stepAt) state.stepAt = now + interval * 1000;
        if (now >= state.stepAt) {
          state.target = (state.target ?? nearest(state.angle)) + step * state.dir;
          state.stepAt = now + interval * 1000;
        }
        busy = true;
      } else {
        state.stepAt = 0;
      }

      if (now < state.holdUntil) busy = true;

      const ease = 1 - Math.exp(-dt / 0.35);
      const aimYaw = state.pointer.inside ? state.pointer.x * parallax * 9 : 0;
      const aimPitch = state.pointer.inside ? -state.pointer.y * parallax * 6 : 0;
      state.yaw += (aimYaw - state.yaw) * ease;
      state.pitch += (aimPitch - state.pitch) * ease;
      if (Math.abs(aimYaw - state.yaw) > 0.01 || Math.abs(aimPitch - state.pitch) > 0.01) busy = true;

      return busy;
    }

    function updateCaption(index) {
      if (!captions || !captionEl) return;
      const cur = items[index];
      if (!cur) return;
      titleEl.textContent = cur.title || cur.alt || `Item ${index + 1}`;
      subtitleEl.textContent = cur.subtitle || '';
      subtitleEl.style.display = cur.subtitle ? 'block' : 'none';

      // Update digit reels
      const str = String(index + 1).padStart(2, '0');
      const reels = countEl.querySelectorAll('.circular-carousel__reel');
      reels.forEach((reel, i) => {
        reel.style.transform = `translateY(${-Number(str[i]) * 10}%)`;
      });

      liveRegion.textContent = `${cur.title || cur.alt || `Item ${index + 1}`}, ${index + 1} of ${count}`;
    }

    function render(now) {
      const elapsed = state.intro ? now - state.intro.start : 0;
      const swell = 1 + stretch * 0.12 * Math.min(1, Math.abs(state.velocity) / 420);
      let spinOffset = 0;
      if (state.intro?.type === 'spin') {
        const p = easeOut(clamp(elapsed / INTRO_LENGTH.spin, 0, 1));
        spinOffset = -300 * state.dir * (1 - p);
      } else if (state.intro?.type === 'assemble') {
        const p = easeOut(clamp(elapsed / INTRO_LENGTH.assemble, 0, 1));
        spinOffset = -32 * state.dir * (1 - p);
      }
      const angle = state.angle + spinOffset;
      const R = radius * swell;

      if (axis === 'x') {
        camera.style.transform = `translate3d(0, 0, ${-R}px) rotateY(${tiltValue + state.yaw}deg) rotateX(${state.pitch}deg)`;
        ring.style.transform = `rotateX(${-angle}deg)`;
      } else if (layout.inward) {
        camera.style.transform = `translate3d(0, 0, ${perspective - 1}px) rotateX(${tiltValue + state.pitch}deg) rotateY(${state.yaw}deg)`;
        ring.style.transform = `rotateY(${angle}deg)`;
      } else {
        camera.style.transform = `translate3d(0, 0, ${-R}px) rotateX(${tiltValue + state.pitch}deg) rotateY(${state.yaw}deg)`;
        ring.style.transform = `rotateY(${angle}deg)`;
      }

      for (let index = 0; index < count; index++) {
        const card = cardElements[index];
        if (!card) continue;
        const base = index * step;
        const mod = introCard(elapsed, base);
        const r = R * mod.radius;
        let transform;
        if (axis === 'x') {
          transform = `rotateX(${-base}deg) translateZ(${r}px)`;
        } else if (layout.inward) {
          transform = `rotateY(${base}deg) translateZ(${-r}px)`;
        } else {
          transform = `rotateY(${base}deg) translateZ(${r}px)`;
          if (layout.billboard) transform += ` rotateY(${-(base + angle)}deg)`;
        }
        if (mod.lift) transform += axis === 'x' ? ` translateX(${mod.lift}px)` : ` translateY(${mod.lift}px)`;
        card.style.transform = transform;

        const world = wrap(base + angle);
        const facing = Math.cos(world * TO_RAD);
        if (layout.inward) card.style.visibility = Math.abs(world) > 86 ? 'hidden' : '';
        const fade = depthFade * Math.pow((1 - facing) / 2, 1.25);
        card.style.setProperty('--cc-depth', fade.toFixed(3));
      }

      const activeIndex = ((Math.round(-state.angle / step) % count) + count) % count || 0;
      if (activeIndex !== state.active) {
        state.active = activeIndex;
        updateCaption(activeIndex);
        if (options.onChange) options.onChange(activeIndex);
      }
    }

    function frame(now) {
      raf = 0;
      const dt = state.last ? Math.min((now - state.last) / 1000, 0.05) : 1 / 60;
      state.last = now;
      const busy = advance(dt, now);
      render(now);
      if (busy && isVisible && !document.hidden) {
        raf = requestAnimationFrame(frame);
      } else {
        state.last = 0;
      }
    }

    function wake() {
      if (!raf && isVisible && !document.hidden) {
        raf = requestAnimationFrame(frame);
      }
    }

    // Pointer events
    function updatePointer(e) {
      const rect = root.getBoundingClientRect();
      state.pointer.x = clamp(((e.clientX - rect.left) / rect.width) * 2 - 1, -1, 1);
      state.pointer.y = clamp(((e.clientY - rect.top) / rect.height) * 2 - 1, -1, 1);
    }

    root.addEventListener('pointerdown', e => {
      state.suppressClick = false;
      if (!draggable || e.button !== 0) return;
      state.press = {
        id: e.pointerId,
        x: e.clientX,
        y: e.clientY,
        angle: state.angle,
        moved: false,
        origin: 0,
        samples: [{ time: performance.now(), angle: state.angle }]
      };
    });

    root.addEventListener('pointermove', e => {
      if (e.pointerType === 'mouse') {
        state.pointer.inside = true;
        updatePointer(e);
      }
      const press = state.press;
      if (!press || press.id !== e.pointerId) {
        wake();
        return;
      }
      const delta = axis === 'x' ? e.clientY - press.y : e.clientX - press.x;
      const cross = axis === 'x' ? e.clientX - press.x : e.clientY - press.y;
      if (!press.moved) {
        if (Math.abs(delta) < DRAG_THRESHOLD) return;
        if (Math.abs(cross) > Math.abs(delta) * 1.2 && e.pointerType !== 'mouse') {
          state.press = null;
          return;
        }
        press.moved = true;
        press.origin = delta;
        state.drag = true;
        state.target = null;
        state.velocity = 0;
        root.setAttribute('data-dragging', '');
        try {
          root.setPointerCapture(e.pointerId);
        } catch (_) {}
      }
      const perPixel = 180 / (Math.PI * radius * state.fit);
      state.angle = press.angle + (delta - press.origin) * perPixel * (layout.inward ? -1 : 1);
      const now = performance.now();
      press.samples.push({ time: now, angle: state.angle });
      while (press.samples.length > 2 && now - press.samples[0].time > 110) press.samples.shift();
      wake();
    });

    function releasePointer(e) {
      const press = state.press;
      if (!press || press.id !== e.pointerId) return;
      state.press = null;
      if (!press.moved) return;
      state.drag = false;
      root.removeAttribute('data-dragging');
      state.suppressClick = true;

      const first = press.samples[0];
      const last = press.samples[press.samples.length - 1];
      const span = (last.time - first.time) / 1000;
      const velocity = span > 0.008 ? clamp((last.angle - first.angle) / span, -1400, 1400) : 0;
      state.velocity = velocity;
      if (Math.abs(velocity) > 60) state.dir = Math.sign(velocity);
      const coasting = autoplay === 'drift' && !(pauseOnHover && state.hover && e.pointerType === 'mouse');
      if (snap && !coasting) {
        const tau = 0.18 + momentum * 1.5;
        state.target = Math.round((state.angle + velocity * tau * 0.55) / step) * step;
      }
      wake();
    }

    root.addEventListener('pointerup', releasePointer);
    root.addEventListener('pointercancel', releasePointer);

    root.addEventListener('pointerenter', e => {
      if (e.pointerType !== 'mouse') return;
      state.hover = true;
      wake();
    });

    root.addEventListener('pointerleave', e => {
      if (e.pointerType === 'mouse') {
        state.hover = false;
        state.pointer.inside = false;
      }
      wake();
    });

    root.addEventListener('click', e => {
      if (state.suppressClick) {
        state.suppressClick = false;
        return;
      }
      const card = e.target.closest('[data-cc-index]');
      if (!card) return;
      const idx = Number(card.getAttribute('data-cc-index'));
      if (focusOnClick) {
        let tgt = -idx * step;
        tgt += 360 * Math.round((state.angle - tgt) / 360);
        state.target = tgt;
        state.holdUntil = performance.now() + 2800;
        wake();
      }
      if (options.onItemClick) options.onItemClick(items[idx], idx);
    });

    root.addEventListener('keydown', e => {
      const forward = axis === 'x' ? 'ArrowDown' : 'ArrowRight';
      const backward = axis === 'x' ? 'ArrowUp' : 'ArrowLeft';
      if (e.key === forward) {
        const base = state.target ?? Math.round(state.angle / step) * step;
        state.target = base - step * (layout.inward ? -1 : 1);
        state.holdUntil = performance.now() + 2800;
        wake();
      } else if (e.key === backward) {
        const base = state.target ?? Math.round(state.angle / step) * step;
        state.target = base + step * (layout.inward ? -1 : 1);
        state.holdUntil = performance.now() + 2800;
        wake();
      } else if (e.key === 'Home') {
        state.target = 0;
        state.holdUntil = performance.now() + 2800;
        wake();
      } else if (e.key === 'End') {
        state.target = -(count - 1) * step;
        state.holdUntil = performance.now() + 2800;
        wake();
      } else if (e.key === 'Enter' || e.key === ' ') {
        if (options.onItemClick && state.active >= 0) {
          options.onItemClick(items[state.active], state.active);
        }
      } else {
        return;
      }
      e.preventDefault();
    });

    root.addEventListener('wheel', e => {
      if (!draggable) return;
      const delta = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : 0;
      if (!delta) return;
      e.preventDefault();
      const perPixel = 180 / (Math.PI * radius * state.fit);
      state.target = null;
      state.angle -= delta * perPixel * (layout.inward ? -1 : 1);
      state.velocity = -delta * perPixel * (layout.inward ? -1 : 1) * 30;
      state.holdUntil = performance.now() + 1600;
      clearTimeout(state.wheelTimer);
      state.wheelTimer = setTimeout(() => {
        if (snap) state.target = nearest(state.angle + state.velocity * 0.12);
        wake();
      }, 140);
      wake();
    }, { passive: false });

    // Resize & Intersection Observers
    const ro = new ResizeObserver(() => {
      measure();
      wake();
    });
    ro.observe(root);

    const io = new IntersectionObserver(([entry]) => {
      isVisible = entry.isIntersecting;
      if (isVisible) wake();
      else {
        cancelAnimationFrame(raf);
        raf = 0;
        state.last = 0;
      }
    });
    io.observe(root);

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        cancelAnimationFrame(raf);
        raf = 0;
        state.last = 0;
      } else {
        wake();
      }
    });

    // Preload first few images then trigger ready
    const loadPromises = items.slice(0, 8).map(it => {
      return new Promise(res => {
        const im = new Image();
        im.decoding = 'async';
        im.onload = () => (im.decode ? im.decode().then(res, res) : res());
        im.onerror = res;
        im.src = it.src;
      });
    });

    const timeout = new Promise(res => setTimeout(res, 2000));
    Promise.race([Promise.all(loadPromises), timeout]).then(() => {
      state.ready = true;
      root.setAttribute('data-ready', '');
      measure();
      render(performance.now());
      wake();
    });

    measure();
    render(performance.now());
    wake();

    return {
      focusIndex: idx => {
        let tgt = -idx * step;
        tgt += 360 * Math.round((state.angle - tgt) / 360);
        state.target = tgt;
        state.holdUntil = performance.now() + 2800;
        wake();
      },
      destroy: () => {
        cancelAnimationFrame(raf);
        ro.disconnect();
        io.disconnect();
        container.innerHTML = '';
      }
    };
  }

  window.initCircularCarousel = initCircularCarousel;
})();
