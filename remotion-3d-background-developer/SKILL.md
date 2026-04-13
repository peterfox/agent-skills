---
name: remotion-3d-background-developer
description: >
  Generate visually stunning, colorful, procedural 3D backgrounds for Remotion videos using react-three-fiber and GLSL shaders.
  Use this skill whenever a user asks for: animated backgrounds, 3D backgrounds, shader backgrounds, liquid gradients, plasma effects,
  aurora effects, galaxy/nebula backgrounds, noise-based patterns, or any kind of procedurally generated visual backdrop for Remotion.
  Also trigger when the user wants to make a Remotion video "look more interesting", "add a background", or "make it pop visually".
  All backgrounds are deterministic — driven by useCurrentFrame() — so they render frame-perfectly in Remotion.
---

# Remotion 3D Background Developer

You generate beautiful, procedural, frame-perfectly rendered backgrounds for Remotion using `@remotion/three` (ThreeCanvas + react-three-fiber) and custom GLSL fragment shaders.

## Critical Remotion 3D Rules

Before writing any code, internalize these constraints — violating them causes rendering artifacts:

1. **Never use `useFrame()`** from `@react-three/fiber`. It animates independently of Remotion's timeline and causes flickering.
2. **Always use `useCurrentFrame()`** from Remotion to drive all animation. Pass `frame` as a shader uniform.
3. **Wrap everything in `<ThreeCanvas width={width} height={height}>`** from `@remotion/three`. Get dimensions from `useVideoConfig()`.
4. **`<Sequence>` inside ThreeCanvas** must have `layout="none"`.

```tsx
import { ThreeCanvas } from "@remotion/three";
import { useCurrentFrame, useVideoConfig } from "remotion";

export const MyBackground = () => {
  const { width, height } = useVideoConfig();
  const frame = useCurrentFrame();
  // frame is the only source of time — pass it to shaders as a uniform
};
```

## Setup

Install the required package:
```bash
npx remotion add @remotion/three
```

react-three-fiber (`@react-three/fiber`) is included as a peer dependency of `@remotion/three`.

## Background Types

Choose the right reference file based on what the user wants:

| Style | File | Keywords |
|-------|------|----------|
| Liquid gradient / blob / lava lamp | [references/liquid-gradient.md](references/liquid-gradient.md) | fluid, organic, smooth, colorful blobs |
| Plasma / electric / neon | [references/plasma.md](references/plasma.md) | electric, neon, psychedelic, acid, vibrant |
| Aurora borealis / northern lights | [references/aurora.md](references/aurora.md) | aurora, northern lights, ethereal, waves |
| Galaxy / nebula / stars | [references/galaxy.md](references/galaxy.md) | space, stars, cosmos, nebula, galaxy |
| Geometric / low-poly / crystalline | [references/geometric.md](references/geometric.md) | geometric, angular, faceted, crystal, prism |

If the user is vague ("make it stunning", "colorful background"), default to **liquid-gradient** — it's the most universally appealing.

## Core Shader Pattern

Every background follows this structure. The fragment shader does the heavy lifting:

```tsx
import { useRef } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";

const vertexShader = `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const fragmentShader = `
  uniform float uTime;
  uniform vec2 uResolution;
  varying vec2 vUv;

  // ... your procedural magic here
  
  void main() {
    vec2 uv = vUv;
    // compute color from uv and uTime
    gl_FragColor = vec4(color, 1.0);
  }
`;

const BackgroundMesh = ({ frame }: { frame: number }) => {
  const { width, height } = useVideoConfig();
  const meshRef = useRef<THREE.Mesh>(null);
  
  const uniforms = useRef({
    uTime: { value: frame / 30 },       // convert frames to seconds (adjust for FPS)
    uResolution: { value: new THREE.Vector2(width, height) },
  });

  // Update uniforms every render — this is the key pattern
  uniforms.current.uTime.value = frame / 30;

  return (
    <mesh ref={meshRef}>
      <planeGeometry args={[2, 2]} />   {/* Full-screen quad */}
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms.current}
      />
    </mesh>
  );
};

export const Background3D = () => {
  const { width, height } = useVideoConfig();
  const frame = useCurrentFrame();

  return (
    <ThreeCanvas width={width} height={height} orthographic>
      <BackgroundMesh frame={frame} />
    </ThreeCanvas>
  );
};
```

**Key details:**
- Use `orthographic` on ThreeCanvas for 2D full-screen backgrounds (no perspective distortion)
- `planeGeometry args={[2, 2]}` fills the orthographic view exactly — no camera positioning needed
- Store uniforms in a `useRef` — recreating them each frame creates GC pressure
- Update uniform values directly: `uniforms.current.uTime.value = frame / 30`

## Color Palettes

Rich color palettes are essential. Use these high-impact combinations in shaders as `vec3` (normalized 0–1 RGB):

```glsl
// Electric violet + hot pink
vec3 colorA = vec3(0.42, 0.05, 0.85);   // deep violet
vec3 colorB = vec3(0.95, 0.10, 0.55);   // hot magenta

// Ocean + lime
vec3 colorA = vec3(0.02, 0.15, 0.60);   // deep ocean blue
vec3 colorB = vec3(0.10, 0.95, 0.45);   // electric lime

// Sunset (fire)
vec3 colorA = vec3(0.95, 0.35, 0.13);   // orange-red
vec3 colorB = vec3(0.95, 0.75, 0.10);   // golden yellow

// Aurora
vec3 colorA = vec3(0.0, 0.85, 0.65);    // teal
vec3 colorB = vec3(0.35, 0.10, 0.90);   // purple
```

## Essential GLSL Utilities

Include these in your fragment shaders as needed:

```glsl
// Smooth noise (value noise)
float hash(vec2 p) {
  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  f = f * f * (3.0 - 2.0 * f); // smoothstep
  return mix(
    mix(hash(i), hash(i + vec2(1, 0)), f.x),
    mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x),
    f.y
  );
}

// Fractal Brownian Motion — layered noise for organic feel
float fbm(vec2 p) {
  float v = 0.0;
  float a = 0.5;
  for (int i = 0; i < 5; i++) {
    v += a * noise(p);
    p *= 2.0;
    a *= 0.5;
  }
  return v;
}

// Color mix with smooth curve
vec3 palette(float t, vec3 a, vec3 b, vec3 c, vec3 d) {
  return a + b * cos(6.2832 * (c * t + d));
}
```

## Composition with Remotion

Place the background behind other content using absolute positioning:

```tsx
export const MyComposition = () => {
  return (
    <AbsoluteFill>
      {/* Background fills the entire frame */}
      <Background3D />
      
      {/* Content layers above */}
      <AbsoluteFill style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
        <h1 style={{ color: "white", fontSize: 80, zIndex: 10 }}>Title</h1>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
```

## Animating Colors Over Time

To transition between color palettes across the video duration:

```tsx
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

const frame = useCurrentFrame();
const { durationInFrames } = useVideoConfig();
const progress = frame / durationInFrames; // 0 → 1 over video duration

// Use in shader uniform as uProgress, then mix palettes in GLSL:
// vec3 color = mix(paletteA(t), paletteB(t), uProgress);
```
