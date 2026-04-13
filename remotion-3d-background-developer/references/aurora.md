# Aurora Borealis Background

Flowing bands of green, teal, and purple light shimmering against a dark sky — ethereal and serene. Perfect for nature documentaries, meditative content, or anything needing otherworldly calm.

## How it works

Layered fbm noise forms horizontal bands across the screen. The bands shift vertically over time with a sine wave envelope to create the ribbon-like aurora shape. Color transitions from teal/green at the base through purple/violet at the top.

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
    for (int i = 0; i < 6; i++) {
      v += a * noise(p);
      p = p * 2.0 + vec2(5.7, 3.2);
      a *= 0.48;
    }
    return v;
  }

  vec3 auroraColor(float t) {
    // t=0: deep teal/green, t=0.5: cyan-white, t=1: violet/purple
    vec3 teal    = vec3(0.00, 0.85, 0.65);
    vec3 green   = vec3(0.10, 0.95, 0.40);
    vec3 cyan    = vec3(0.40, 1.00, 0.90);
    vec3 purple  = vec3(0.55, 0.10, 0.85);
    vec3 violet  = vec3(0.75, 0.20, 0.95);

    if (t < 0.25) return mix(green, teal, t / 0.25);
    if (t < 0.5)  return mix(teal, cyan, (t - 0.25) / 0.25);
    if (t < 0.75) return mix(cyan, purple, (t - 0.5) / 0.25);
    return mix(purple, violet, (t - 0.75) / 0.25);
  }

  void main() {
    vec2 uv = vUv;
    float t = uTime * 0.25;

    // Sky gradient: dark navy → near-black
    vec3 sky = mix(vec3(0.01, 0.02, 0.08), vec3(0.0, 0.01, 0.04), uv.y);

    // Aurora is centered in the upper-middle third of the screen
    float bandCenter = 0.62 + sin(t * 0.3) * 0.06;
    float bandWidth = 0.22;

    // Horizontal flow: warp x with slow fbm
    float warpX = fbm(vec2(uv.x * 1.5 + t * 0.4, uv.y * 0.5 + t * 0.15)) * 0.3;
    float warpY = fbm(vec2(uv.x * 2.0 - t * 0.2, uv.y * 1.5 + t * 0.1)) * 0.15;

    vec2 warpedUv = uv + vec2(warpX, warpY);

    // Vertical band envelope: gaussian falloff from band center
    float dist = abs(warpedUv.y - bandCenter);
    float band = exp(-dist * dist / (bandWidth * bandWidth * 0.5));

    // Inner shimmer — faster noise for the glowing core
    float shimmer = fbm(vec2(uv.x * 3.0 + t * 1.2, uv.y * 4.0 - t * 0.8));
    float glow = band * (0.7 + shimmer * 0.3);

    // Color: vary hue across x and slightly by y height within band
    float hueT = fbm(vec2(uv.x * 1.2 + t * 0.3, t * 0.2)) * 0.8
               + (warpedUv.y - bandCenter + bandWidth) / (bandWidth * 2.0) * 0.2;
    hueT = clamp(hueT, 0.0, 1.0);

    vec3 auroraCol = auroraColor(hueT);

    // Subtle stars in sky
    float starNoise = hash(floor(uv * 200.0));
    float star = step(0.997, starNoise) * (0.4 + 0.6 * hash(uv * 300.0));
    sky += star * vec3(0.8, 0.9, 1.0) * (1.0 - glow);

    // Compose: sky + aurora glow + bright core
    vec3 color = sky;
    color += auroraCol * glow * 0.9;
    color += auroraCol * pow(band, 3.0) * 0.5; // bright core streak

    // Subtle second aurora band
    float bandCenter2 = 0.52 + cos(t * 0.4 + 1.5) * 0.04;
    float dist2 = abs(warpedUv.y - bandCenter2);
    float band2 = exp(-dist2 * dist2 / (0.06 * 0.06)) * 0.35;
    vec3 aurora2Col = auroraColor(fract(hueT + 0.4));
    color += aurora2Col * band2;

    color = clamp(color, 0.0, 1.0);
    gl_FragColor = vec4(color, 1.0);
  }
`;

const AuroraMesh = ({ frame }: { frame: number }) => {
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

export const AuroraBackground = () => {
  const { width, height } = useVideoConfig();
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill>
      <ThreeCanvas width={width} height={height} orthographic>
        <AuroraMesh frame={frame} />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
```

## Customization

**Move band position** — adjust `bandCenter` (0=bottom, 1=top of screen).

**Wider/narrower ribbons** — adjust `bandWidth` (0.1 = thin ribbon, 0.4 = fills half screen).

**Color variation**:
- Replace `auroraColor()` hues for pink/coral aurora (rare natural phenomenon):
  ```glsl
  vec3 pink = vec3(0.95, 0.30, 0.55);
  vec3 red  = vec3(0.90, 0.10, 0.15);
  ```
- For a more synthetic neon look, increase saturation:
  ```glsl
  color = mix(vec3(dot(color, vec3(0.299, 0.587, 0.114))), color, 1.5);
  ```

**Denser stars** — lower the `step(0.997, ...)` threshold toward `0.990`.
