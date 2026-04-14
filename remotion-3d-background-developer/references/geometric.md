# Geometric / Low-Poly / Crystalline Background

Sharp-edged faceted planes, voronoi crystal patterns, and angular geometry with vivid color fills. Feels modern, tech, architectural. Great for corporate, design, or product videos.

## How it works

Two techniques covered here:

1. **Voronoi / Crystal cells** — divide space into cells based on nearest point, colorize by cell ID and distance to edge
2. **Animated polygon mesh** — a grid of vertices that oscillate, creating a shimmering low-poly surface

## Voronoi Crystal Implementation

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

  vec2 hash2(vec2 p) {
    p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
    return fract(sin(p) * 43758.5453);
  }

  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
  }

  // Voronoi: returns vec2(min dist to center, cell id hash)
  vec2 voronoi(vec2 p, float t) {
    vec2 ip = floor(p);
    vec2 fp = fract(p);

    float minDist = 8.0;
    float cellId = 0.0;

    for (int j = -1; j <= 1; j++) {
      for (int i = -1; i <= 1; i++) {
        vec2 neighbor = vec2(float(i), float(j));
        vec2 cellCenter = hash2(ip + neighbor);

        // Animate cell centers subtly
        cellCenter = 0.5 + 0.45 * sin(t * 0.4 + 6.2832 * cellCenter);

        vec2 diff = neighbor + cellCenter - fp;
        float dist = length(diff);

        if (dist < minDist) {
          minDist = dist;
          cellId = hash(ip + neighbor);
        }
      }
    }
    return vec2(minDist, cellId);
  }

  vec3 palette(float t) {
    // Cool blue-purple-teal geometric palette
    vec3 a = vec3(0.4, 0.4, 0.5);
    vec3 b = vec3(0.3, 0.3, 0.4);
    vec3 c = vec3(1.0, 1.0, 1.0);
    vec3 d = vec3(0.00, 0.15, 0.50);
    return a + b * cos(6.2832 * (c * t + d));
  }

  void main() {
    vec2 uv = vUv;
    float ar = uResolution.x / uResolution.y;
    uv.x *= ar;

    float t = uTime * 0.3;

    // Scale controls cell size — smaller = more cells
    float scale = 6.0;
    vec2 vor = voronoi(uv * scale, t);
    float minDist = vor.x;
    float cellId = vor.y;

    // Cell fill color — map cell ID to palette
    vec3 cellColor = palette(cellId + t * 0.05);

    // Cell edge — sharp dark border
    float edge = 1.0 - smoothstep(0.02, 0.08, minDist);
    vec3 edgeColor = vec3(0.0, 0.02, 0.05);

    vec3 color = mix(cellColor, edgeColor, edge);

    // Subtle highlight at cell centers (minDist very small = center glow)
    float centerGlow = exp(-minDist * minDist * 40.0) * 0.3;
    color += vec3(1.0) * centerGlow;

    // Overall luminosity variation by position
    float vignette = 1.0 - smoothstep(0.3, 1.0, length(vUv - 0.5));
    color *= 0.6 + 0.4 * vignette;

    gl_FragColor = vec4(color, 1.0);
  }
`;

const GeometricMesh = ({ frame }: { frame: number }) => {
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

export const GeometricBackground = () => {
  const { width, height } = useVideoConfig();
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill>
      <ThreeCanvas width={width} height={height} orthographic>
        <GeometricMesh frame={frame} />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
```

## Customization

**Cell count** — `scale = 6.0` gives ~36 visible cells. Double to 12 for small crystals, halve to 3 for large dramatic facets.

**Sharper edges** — tighten the edge smoothstep: `smoothstep(0.01, 0.04, minDist)`

**Flat color per cell** (no palette cycling) — use the `cellId` directly to index a fixed palette array:
```glsl
vec3[5] colors = vec3[5](
  vec3(0.95, 0.20, 0.40),
  vec3(0.10, 0.60, 0.95),
  vec3(0.10, 0.90, 0.60),
  vec3(0.95, 0.75, 0.10),
  vec3(0.65, 0.10, 0.95)
);
vec3 cellColor = colors[int(cellId * 5.0)];
```

**Dark/corporate look** — pull colors toward dark:
```glsl
color = mix(vec3(0.05, 0.05, 0.08), color, 0.4);
```

**No animation (static)** — pass `t = 0.0` regardless of time. Cells stay fixed, only the palette shifts.
