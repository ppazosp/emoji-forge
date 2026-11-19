# GPU effects cookbook

Start from approved cels. For each effect, identify the purpose, emitter (wrist, prop or feet), active phase and layer order. Render at **512 px or above**, keep a lossless sequence, and downsample once with Lanczos. Review at the native canvas and smallest target size. Keep facial ink and silhouette readable even on the strongest frame. Match matte and transparent variants to their backgrounds.

```sh
uv run --with pillow --with moderngl --with glcontext --with playwright \
  python scripts/render_shader.py work/registered/timing.json shaders/sparkle.frag work/fx
uv run --with pillow python scripts/assemble_gif.py work/fx/timing.json exports/sparkle.gif \
  --size 128 --max-bytes 128000 --matte '#20252f'
```

ModernGL tries native standalone OpenGL and EGL. In auto mode, context unavailability falls back to headless Chromium WebGL 2. Install a Playwright browser with `uv run --with playwright playwright install chromium`, or pass `--channel chrome` to use an installed Chrome. To diagnose a backend, pass `--backend moderngl` or `--backend webgl`. WebGL requires floating-point render targets and can use Chromium's software compositor on hosts without a supported GPU. Both paths run the same GLSL effect and five passes. A shader compile failure is reported on the selected backend.

## Shader contract

A shader file defines `vec4 effect(vec2 uv, vec4 art)`. UV is normalized from the bottom left. `art` and `cel(uv)` are straight-alpha source samples. Uniforms include `anchor` (per-exposure UV), `phase` (normalized loop time at that exposure's start), `seconds` and `resolution`. To animate a shader during a held drawing, repeat the source cel in the timing file with separate exposure delays. Use only local, trusted shader files.

The first pass composites artwork and effects into a half-float target. `brightPass` extracts emissive values above 1.0. Horizontal and vertical Gaussian blur passes spread the light, and a final pass adds bloom and fades to transparent before the border. Render transparent masters first. For GIF with soft fire or smoke, try an opaque dark matte then use opacity thresholding only for the transparent export. Inspect dithering at the target size. Diffusion can restore gradients at the cost of larger files and some temporal noise. Keep a simple palette for the character.

### Domain-warped fire and heat haze

```glsl
vec2 p = (uv - anchor) * vec2(12.0, 5.0) - vec2(0.0, seconds * 2.8);
float turbulence = fbm(p + vec2(fbm(p + 4.0), 0.0) * 2.0);
vec2 offset = vec2(turbulence - 0.5, 0.0) * 0.01 * (1.0 - art.a);
vec4 displaced = cel(uv + offset);
```

### Distance fields, perspective and impact

```glsl
float radius = 0.025 / mix(1.0, 0.27, travel); // Perspective growth as depth closes.
float core = halo(sdSegment(uv, anchor, tip), radius);
float hardRing = halo(sdCircle(uv - anchor, ringRadius), 0.018);
```

Use a converging segment and an expanding near-camera cross-section for a head-on beam. Key a distinct charge, contact, recoil and smoke release. Use camera movement only if the storyboard calls for it. Carry it through impact and burn, then damp it before the seam. A dissolve can subtract a warped distance mask and use the boundary as its emissive edge.

```glsl
float edge = length(uv - anchor) - radius + 0.08 * (fbm(uv * 32.0) - 0.5);
float survivingAlpha = art.a * smoothstep(-0.006, 0.008, edge);
vec3 color = mix(art.rgb, vec3(2.2, 0.7, 0.12), halo(edge, 0.014));
```

| Example | What to adapt |
| --- | --- |
| [Fire](../shaders/fire.frag) | Layer warped flames behind art, then confine heat haze to the plume. |
| [Sparkle](../shaders/sparkle.frag) | Seed particles deterministically with staggered birth, travel and decay. |
| [Shockwave](../shaders/shockwave.frag) | Expand an SDF ring on contact and refract lightly near the ring. |
| [Beam and burn](../shaders/beam-burn.frag) | Grow a perspective beam into a flare, then spread a hot-edged hole. |
| [Glitch](../shaders/glitch.frag) | Briefly displace rows and split colour channels before recovering the drawing. |
| [Portal](../shaders/portal.frag) | Animate radius and polar noise around a vortex. Attach it to a floor or exit point. |
| [Aura](../shaders/aura.frag) | Pulse outer noise and angular lightning around the silhouette. Time the colour change to the pose. |

Use branch-shaped lightning or staggered flashes sparingly. After effects, inspect the eyes, prop anchors and border on every encoded frame. If an effect is lost at small size, enlarge a few defining shapes before increasing overall brightness.
