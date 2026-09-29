---
name: apple-liquid-glass
description: Authentic Apple Liquid Glass & VisionOS Glassmorphism engineering skill. Defines the exact multi-layered specular borders, SVG optical refraction, vibrancy saturation filters, concentric squircles, and MotionSites Apple-style kinetic landing page architectures.
---

# Apple Liquid Glass & VisionOS Design System (MotionSites Tier)

## 1. Core Aesthetic Philosophy
Apple's **Liquid Glass** (VisionOS / macOS Sequoia / iOS 18+) transcends flat glassmorphism. It models physical light interaction through multi-layered optical physics:
- **Refraction & Dispersion:** Light bends through the edges of the substrate, warping background elements slightly via SVG displacement maps.
- **Vibrancy (Dynamic Saturation):** Background colors don't become muddy or washed out; they are boosted with `saturate(180%) contrast(108%)`.
- **Razor-Thin Specular Rim (Diamond Bevel):** Machined micro-highlight on the top edge (`inset 0 1px 1px 0 rgba(255, 255, 255, 0.4)`) and subtle dark ambient occlusion beneath (`inset 0 -1px 1px 0 rgba(0, 0, 0, 0.5)`).
- **Physical Depth & Specular Hotspot:** Soft, multi-layered diffuse drop shadows combined with radial specular hotspots that track cursor interaction.
- **Concentric Squircles (Doppelrand):** Mathematical squircle curvature (`border-radius: 28px` to `36px`) with nested sub-containers maintaining exact radius offset (`R_inner = R_outer - padding`).

---

## 2. Authentic Apple Liquid Glass CSS Formula

```css
/* Authentic Apple Liquid Glass Base Material */
.apple-liquid-glass {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.08) 0%,
    rgba(255, 255, 255, 0.02) 100%
  );
  backdrop-filter: blur(28px) saturate(190%) contrast(105%);
  -webkit-backdrop-filter: blur(28px) saturate(190%) contrast(105%);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-top: 1px solid rgba(255, 255, 255, 0.28);
  border-left: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 28px;
  box-shadow: 
    0 30px 60px -12px rgba(0, 0, 0, 0.55),
    0 18px 36px -18px rgba(0, 0, 0, 0.6),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.35),
    inset 0 -1px 1px 0 rgba(0, 0, 0, 0.4);
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Apple Liquid Specular Sheen (Moves with cursor) */
.apple-liquid-glass::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
    rgba(255, 255, 255, 0.18) 0%,
    rgba(255, 255, 255, 0.04) 35%,
    transparent 65%
  );
  pointer-events: none;
  border-radius: inherit;
  opacity: 0;
  transition: opacity 0.3s ease;
  mix-blend-mode: overlay;
  z-index: 1;
}

.apple-liquid-glass:hover::before {
  opacity: 1;
}

/* Concentric Inner Glass Pod */
.apple-glass-pod {
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: calc(28px - 8px);
  padding: 16px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.08);
}
```

---

## 3. MotionSites Apple Landing Page Architecture

### A. The Floating Frosted Glass Dock (Navbar)
Detached from viewport edges, centered with `margin: 20px auto`, pill-shaped (`rounded-full`), with frosted blur, micro-dividers, and fluid button capsules.

### B. Ambient Chromatic Fluid Orbs
Slowly oscillating radial gradient orbs behind the glass layer (deep imperial gold, titan cyan, midnight indigo) that provide rich refracted color through the frosted glass cards as the user scrolls.

### C. Apple Pro Typography & Eyebrows
- **Eyebrow:** Micro-pill with illuminated breathing status dot (`Apple Green` or `Aureus Gold`).
- **Headlines:** Large font weight with subtle gradient clipping (`linear-gradient(180deg, #FFFFFF 0%, rgba(255,255,255,0.72) 100%)`).
- **Specs Callouts:** Monospaced metric capsules with subtle glass enclosures.

### D. Kinetic Interactions (MotionSites Standard)
- Magnetic glass buttons that spring-scale on hover.
- Staggered scroll reveals using `IntersectionObserver` with custom cubic-bezier timing.
- Real-time mouse tilt with optical refraction angle adjustments.
