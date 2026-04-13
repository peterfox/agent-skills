# Plasma / Electric / Neon Background

High-energy, psychedelic patterns using classic plasma shader math — sine wave interference patterns that produce vibrant, shifting colors. Great for music videos, tech intros, or anything needing intensity.

## How it works

Combine multiple sine waves with different frequencies and phases across both UV axes. The interference pattern creates complex, organic-looking shapes without any noise functions. Apply a color palette function to map the scalar field to vivid RGB.

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
  #define TAU 6.28318530718

  vec3 palette(float t) {
    // Electric neon: cyan → magenta → yellow → white
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(1.0, 1.0, 0.5);
    vec3 d = vec3(0.80, 0.90, 0.30);
    return a + b * cos(TAU * (c * t + d));
  }

  float plasma(vec2 uv, float t) {
    float v = 0.0;
    
    // Classic plasma: layered sine interference
    v += sin(uv.x * 5.0 + t);
    v += sin(uv.y * 4.0 + t * 1.1);
    v += sin((uv.x + uv.y) * 3.5 + t * 0.9);
    v += sin(sqrt(uv.x * uv.x + uv.y * uv.y) * 6.0 - t * 1.3);
    
    // Additional layers for complexity
    v += sin(uv.x * 8.0 - uv.y * 3.0 + t * 0.7) * 0.5;
    v += sin(length(uv - vec2(sin(t * 0.3), cos(t * 0.4))) * 7.0) * 0.6;
    
    return v / 4.0; // normalize roughly to [-1, 1]
  }

  void main() {
    // Center and aspect-correct UV
    vec2 uv = (vUv - 0.5) * 2.0;
    uv.x *= uResolution.x / uResolution.y;

    float t = uTime * 0.5;

    float p = plasma(uv, t);

    // Map scalar field to color via palette
    float colorT = p * 0.5 + 0.5; // remap to [0, 1]
    vec3 color = palette(colorT);

    // Add a secondary palette layer for more richness
    float p2 = plasma(uv * 1.5 + 0.3, t * 0.8 + 1.0);
    float colorT2 = p2 * 0.5 + 0.5;
    vec3 color2 = palette(colorT2 + 0.3);

    color = mix(color, color2, 0.35);

    // Boost saturation slightly
    float luma = dot(color, vec3(0.299, 0.587, 0.114));
    color = mix(vec3(luma), color, 1.3);
    color = clamp(color, 0.0, 1.0);

    gl_FragColor = vec4(color, 1.0);
  }
`;

const PlasmaMesh = ({ frame }: { frame: number }) => {
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

export const PlasmaBackground = () => {
  const { width, height } = useVideoConfig();
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill>
      <ThreeCanvas width={width} height={height} orthographic>
        <PlasmaMesh frame={frame} />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
```

## Customization

**Dark/moody** — add a dark base mix:
```glsl
color = mix(vec3(0.02, 0.0, 0.08), color, 0.85);
```

**Glowing neon lines** — threshold the plasma field:
```glsl
float edge = abs(sin(p * PI * 3.0));
edge = pow(edge, 4.0);  // sharpen
color = mix(color, vec3(1.0), edge * 0.6);
```

**Palette variants**:
```glsl
// Deep space purple
vec3 d = vec3(0.25, 0.45, 0.75);

// Toxic green + yellow
vec3 d = vec3(0.10, 0.30, 0.45);

// Hot pink + orange
vec3 d = vec3(0.0, 0.20, 0.40);
```

**Speed control** — `t = uTime * 0.5`. Increase to ~1.5 for frenetic energy, decrease to ~0.2 for meditative feel.
