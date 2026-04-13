# Liquid Gradient Background

Smooth, organic blobs of color that shift and flow — inspired by lava lamps and liquid gradients. The most versatile background style.

## How it works

Multiple "color centers" orbit the screen on sinusoidal paths. The fragment shader blends colors based on inverse distance to each center, creating soft, blurred blobs. Layered with fbm noise to break up mathematical regularity.

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

  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
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
    float v = 0.0;
    float a = 0.5;
    for (int i = 0; i < 4; i++) {
      v += a * noise(p);
      p = p * 2.1 + vec2(1.7, 9.2);
      a *= 0.5;
    }
    return v;
  }

  vec3 palette(float t) {
    // Violet → Cyan → Magenta cycle
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(1.0, 1.0, 1.0);
    vec3 d = vec3(0.30, 0.10, 0.55);
    return a + b * cos(6.2832 * (c * t + d));
  }

  void main() {
    vec2 uv = vUv;
    float ar = uResolution.x / uResolution.y;
    uv.x *= ar;

    float t = uTime * 0.4;

    // Five animated color centers with different orbital speeds
    vec2 c1 = vec2(0.5 * ar + sin(t * 0.7) * 0.4 * ar, 0.5 + cos(t * 0.5) * 0.35);
    vec2 c2 = vec2(0.5 * ar + cos(t * 0.4 + 1.0) * 0.5 * ar, 0.5 + sin(t * 0.6 + 2.0) * 0.4);
    vec2 c3 = vec2(0.5 * ar + sin(t * 0.9 + 4.0) * 0.35 * ar, 0.5 + cos(t * 0.8 + 1.5) * 0.45);
    vec2 c4 = vec2(0.5 * ar + cos(t * 0.3 + 3.0) * 0.45 * ar, 0.5 + sin(t * 0.7 + 0.5) * 0.3);
    vec2 c5 = vec2(0.5 * ar + sin(t * 0.6 + 2.5) * 0.3 * ar, 0.5 + cos(t * 0.4 + 3.5) * 0.4);

    // Noise warp for organic feel
    vec2 warpedUv = uv + fbm(uv * 2.0 + t * 0.3) * 0.2;

    // Inverse distance weighting — closer centers contribute more color
    float w1 = 1.0 / (length(warpedUv - c1) + 0.001);
    float w2 = 1.0 / (length(warpedUv - c2) + 0.001);
    float w3 = 1.0 / (length(warpedUv - c3) + 0.001);
    float w4 = 1.0 / (length(warpedUv - c4) + 0.001);
    float w5 = 1.0 / (length(warpedUv - c5) + 0.001);
    float totalW = w1 + w2 + w3 + w4 + w5;

    // Blend time offsets for each center → different hues
    float colorT = (
      w1 * 0.0 +
      w2 * 0.2 +
      w3 * 0.45 +
      w4 * 0.65 +
      w5 * 0.85
    ) / totalW;

    colorT += fbm(uv * 3.0 + t * 0.2) * 0.15;

    vec3 color = palette(colorT);

    // Subtle vignette
    float vignette = 1.0 - smoothstep(0.4, 1.2, length(vUv - 0.5) * 1.8);
    color *= 0.7 + 0.3 * vignette;

    gl_FragColor = vec4(color, 1.0);
  }
`;

const LiquidMesh = ({ frame }: { frame: number }) => {
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

export const LiquidGradientBackground = () => {
  const { width, height } = useVideoConfig();
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill>
      <ThreeCanvas width={width} height={height} orthographic>
        <LiquidMesh frame={frame} />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
```

## Customization

**Change palette** — replace the `palette()` function's `d` vector. The four components control the color cycle offset:
```glsl
// Sunset (orange → pink → purple)
vec3 d = vec3(0.00, 0.33, 0.67);

// Ocean (blue → teal → cyan)
vec3 d = vec3(0.55, 0.65, 0.75);

// Fire (red → orange → yellow)
vec3 d = vec3(0.00, 0.10, 0.20);
```

**Slow down / speed up** — change `t = uTime * 0.4`. Lower = slower, higher = more energetic.

**More blobs** — add more `c6`, `c7` center points and include their weights.

**Sharper edges** — replace inverse-distance with gaussian: `exp(-dist * dist * 8.0)` for defined, bubblier blobs.
