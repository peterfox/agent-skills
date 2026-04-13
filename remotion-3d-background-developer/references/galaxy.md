# Galaxy / Nebula / Space Background

A rotating galaxy arm with nebula clouds, star fields, and colorful dust. Stunning for cinematic intros, sci-fi content, or anything needing cosmic scale.

## How it works

Stars are placed using hash-based point distribution. Nebula clouds use layered fbm noise tinted with multiple colors. A galaxy spiral is simulated by rotating UV coordinates and applying polar-coordinate-based density falloff. Everything rotates slowly over time.

## Full Implementation

```tsx
import { useRef } from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
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

  #define PI 3.14159265359

  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
  }
  float hash1(float p) {
    return fract(sin(p * 127.1) * 43758.5453);
  }

  float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(
      mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
      mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x),
      f.y
    );
  }

  float fbm(vec2 p) {
    float v = 0.0; float a = 0.5;
    for (int i = 0; i < 5; i++) {
      v += a * noise(p);
      p = p * 2.0 + vec2(3.1, 7.4);
      a *= 0.5;
    }
    return v;
  }

  // Smooth star field — returns brightness for a star cluster grid
  float starField(vec2 uv, float density, float size) {
    vec2 cell = floor(uv / density);
    vec2 cellUv = fract(uv / density);
    
    float starX = hash(cell);
    float starY = hash(cell + vec2(17.3, 43.7));
    float starBrightness = hash(cell + vec2(89.1, 23.4));
    float starSize = hash(cell + vec2(5.1, 11.9)) * size;

    if (starBrightness < 0.85) return 0.0; // only 15% of cells have stars

    vec2 starPos = vec2(starX, starY);
    float d = length(cellUv - starPos);
    return smoothstep(starSize, 0.0, d) * (0.5 + starBrightness * 0.5);
  }

  vec2 rotate(vec2 uv, float angle) {
    float c = cos(angle); float s = sin(angle);
    return vec2(uv.x * c - uv.y * s, uv.x * s + uv.y * c);
  }

  void main() {
    vec2 uv = (vUv - 0.5) * 2.0;
    uv.x *= uResolution.x / uResolution.y;

    float t = uTime * 0.08; // very slow rotation

    // ---- Deep space background ----
    vec3 color = vec3(0.0, 0.0, 0.02);

    // ---- Nebula clouds ----
    // Layer 1: large blue-purple cloud
    vec2 nebUv1 = rotate(uv, t * 0.5) * 0.8 + vec2(0.1, 0.15);
    float neb1 = fbm(nebUv1 * 1.2 + 0.5);
    neb1 = smoothstep(0.35, 0.75, neb1);
    color += vec3(0.05, 0.10, 0.45) * neb1 * 0.7;

    // Layer 2: teal-cyan cloud
    vec2 nebUv2 = rotate(uv, -t * 0.3 + 1.2) * 1.1 + vec2(-0.2, 0.05);
    float neb2 = fbm(nebUv2 * 1.5 + 2.3);
    neb2 = smoothstep(0.40, 0.80, neb2);
    color += vec3(0.00, 0.35, 0.45) * neb2 * 0.5;

    // Layer 3: pink-magenta cloud (smaller)
    vec2 nebUv3 = rotate(uv + vec2(0.3, -0.2), t * 0.7) * 1.5;
    float neb3 = fbm(nebUv3 * 2.0 + 5.7);
    neb3 = smoothstep(0.45, 0.80, neb3);
    color += vec3(0.55, 0.05, 0.35) * neb3 * 0.6;

    // Layer 4: orange dust band
    vec2 nebUv4 = rotate(uv + vec2(-0.1, 0.3), -t * 0.4) * 0.9;
    float neb4 = fbm(nebUv4 * 1.8 + 3.1);
    neb4 = smoothstep(0.50, 0.82, neb4);
    color += vec3(0.50, 0.18, 0.02) * neb4 * 0.4;

    // ---- Galaxy spiral ----
    vec2 galUv = rotate(uv, t);
    float r = length(galUv);
    float angle = atan(galUv.y, galUv.x);

    // Spiral arms: brightness peaks where arm passes
    float spiralAngle = angle + r * 4.0; // spiral tightness
    float arm = abs(sin(spiralAngle * 1.0));
    arm = pow(1.0 - arm, 6.0); // thin arm falloff
    float galDensity = arm * exp(-r * 2.5); // fade with radius
    galDensity *= (0.7 + fbm(galUv * 4.0 + t * 0.5) * 0.3); // clump variation

    vec3 galColor = mix(
      vec3(0.90, 0.75, 0.40),  // warm core
      vec3(0.60, 0.70, 1.00),  // cool outer arms
      smoothstep(0.0, 0.6, r)
    );
    color += galColor * galDensity * 1.2;

    // Bright galactic core
    float core = exp(-r * r * 18.0);
    color += vec3(1.0, 0.92, 0.70) * core * 1.5;

    // ---- Star fields (multiple scales) ----
    vec2 rotUv = rotate(uv, t * 0.2); // stars rotate slowly
    float stars1 = starField(rotUv * 4.0, 1.0, 0.08);
    float stars2 = starField(rotUv * 7.0 + 2.3, 1.0, 0.06);
    float stars3 = starField(rotUv * 12.0 + 5.7, 1.0, 0.04);
    float allStars = stars1 * 0.9 + stars2 * 0.7 + stars3 * 0.5;
    color += vec3(0.85, 0.90, 1.00) * allStars;

    // Tone map and clamp
    color = color / (color + 0.5); // simple Reinhard
    color = clamp(color, 0.0, 1.0);

    gl_FragColor = vec4(color, 1.0);
  }
`;

const GalaxyMesh = ({ frame }: { frame: number }) => {
  const { width, height } = useVideoConfig();
  const uniforms = useRef({
    uTime: { value: 0 },
    uResolution: { value: new THREE.Vector2(width, height) },
  });

  uniforms.current.uTime.value = frame / 30;

  return (
    <mesh>
      <planeGeometry args={[2, 2]} />
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms.current}
      />
    </mesh>
  );
};

export const GalaxyBackground = () => {
  const { width, height } = useVideoConfig();
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill>
      <ThreeCanvas width={width} height={height} orthographic>
        <GalaxyMesh frame={frame} />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
```

## Customization

**Zoom into the core** — scale `uv` down: `uv *= 0.5` brings the galaxy center into view.

**More spiral arms** — change `sin(spiralAngle * 1.0)` to `sin(spiralAngle * 2.0)` (2 arms) or `3.0` (3 arms).

**Nebula colors** — swap the `vec3` color values for each nebula layer. Complement colors work well (e.g., teal+orange, purple+yellow).

**Star density** — lower the `0.85` threshold in `starField` for more stars, raise it for fewer.

**Rotation speed** — `uTime * 0.08` controls overall rotation. `0.0` = frozen galaxy.
