# Render a shader you write

Forge runs local fragment shaders on ModernGL or headless WebGL 2. It supplies timed cels, a clock and optional image inputs. Start with the action and what the effect should make visible. Design a shader for that moment, using your own uniforms, textures and passes. Borrow individual techniques when they fit, or start with a blank fragment and leave the helpers out.

## Write an effect

Save this as `wash.frag`. Declare your own uniform names and read them in your fragment code.

```glsl
uniform vec3 washColor;
uniform float washAmount;

vec4 effect(vec2 uv, vec4 art) {
    float traveling = 0.5 + 0.5 * sin(time * 4.0 + uv.y * 8.0);
    return vec4(mix(art.rgb, washColor, washAmount * traveling), art.a);
}
```

Save a local `uniforms.json` and pass it with `--params`.

```json
{
  "washColor": "#70c6ff",
  "washAmount": {"keyframes": [
    {"at": 0.0, "value": 0.0, "ease": "ease-in-out"},
    {"at": 0.5, "value": 0.8},
    {"at": 1.0, "value": 0.0}
  ]}
}
```

```sh
uv run --extra gpu forge render cels/ wash.frag out/wash --params uniforms.json
uv run forge fit out/wash/timing.json out/wash.gif --preset slack
```

For an explicit pass chain, use a JSON file in place of `wash.frag`. In a pack entry you can also put that JSON structure directly under `effect`. Paths are relative to the config that declares them.

```json
{
  "passes": [
    {"name": "emit", "shader": "./custom-emit.frag", "params": {"ink": "#ffac41"},
     "inputs": {"grain": "./grain.png"}},
    "bloom",
    {"shader": "./custom-composite.frag", "inputs": {"unblurred": "emit"}}
  ],
  "params": {"palette": ["#e73f76", "#91dcea"]}
}
```

A pass reads the previous result as `source`. It can also read the original cel through `original`, or a named earlier pass using `inputs`. In `params` you can use `{"image": "grain.png"}` for a texture or `{"pass": "emit"}` to bind an earlier result. Multiple samplers and sampler arrays are supported. Intermediate passes retain high dynamic range. The example `bloom` step extracts and blurs bright pixels then composites them. Omit it to use your own passes throughout. A single-fragment shorthand carries the original optional bloom pass. Use `"bloom": false` or an explicit one-pass chain to render only that shader.

## Uniform contract

| GLSL name | Meaning |
| --- | --- |
| `time` | Seconds from the start of the current sequence to this exposure. |
| `progress` | That same value normalized from 0 to 1. |
| `resolution` | Render width and height in pixels, as a `vec2`. |
| `source`, `original` | Straight-alpha RGBA `sampler2D` textures. Read with `uv` from the bottom left. |
| `anchor`, `intensity`, `phase`, `seconds` | Convenience uniforms used by older examples. `phase` mirrors progress and `seconds` can be scaled with a `speed` parameter. |

In the `effect(vec2 uv, vec4 art)` form, Forge declares the uniforms in the table and adds its helper library. Write only the extra declarations you need. A complete fragment file can instead define `void main()`, read `in vec2 uv`, and use one `out vec4` color. In that form declare the inputs and uniforms you use. Forge supplies the runtime GLSL version for its fullscreen vertex shader. For a file that runs on both backends, use the shared desktop GLSL 330 and ES 300 syntax.

Uniform names and types come from the compiled shader. Pass numbers, booleans, vectors, column-major matrices, arrays, CSS colors for `vec3` or `vec4`, or image bindings. With a uniform array, use one JSON entry per element, such as `[[0.1, 0.2], [0.3, 0.4]]` for a `vec2[2]`. A curve can use normalized `at`, absolute `ms` or zero-based `frame` keys. Easing supports `linear`, `ease-in`, `ease-out`, `ease-in-out` and `hold`. For booleans or textures, use hold interpolation. Frame-level values can override global parameters. Pass-specific values apply to their pass. Unused uniforms may be optimized away by the shader compiler.

## Backend and export options

ModernGL tries native OpenGL and then EGL. On headless Ubuntu the EGL path needs `libegl1`, `libegl-mesa0`, `libgl1` and `libgl1-mesa-dri`. Auto mode can fall back to Playwright Chromium. Install it with `uv run --extra webgl playwright install chromium` or use `--channel chrome`. To choose the backend, pass `--backend moderngl` or `--backend webgl`. WebGL needs floating-point render targets and may use a software renderer.

A larger resolution can help with fine lines or soft lighting. Try the default full-size render and downsample, or use `--draft` to get quick feedback. For soft glows, compare a solid matte to GIF's single transparent palette index. Check both themes if the target uses them.

## Recipes and shared helpers

Use the [shader recipes](shader-recipes.md) as starting points for individual techniques. Design the effect for the emoji before choosing code. Use any technique, build from scratch when the action needs it, and skip helpers that get in the way. The [lantern example](../assets/lantern/README.md) shows fully custom shaders driven by a pack manifest.

Forge assembles [library.glsl](../shaders/library.glsl) when it loads a fragment that defines `effect`. The modules share normalized bottom-left UVs and straight alpha. The result of a pass can carry HDR color until the final output; use `forgeToneMap` or your own resolve to bring it into display range.

| Technique | Helpers |
| --- | --- |
| [Noise](../shaders/lib/noise.glsl) | Value `noise`, `fbm`, `forgeGradientNoise`, `forgeSimplexNoise`, `forgeWorley`, `forgeCurlNoise`, `forgeDomainWarp`, `forgeLoopNoise`. Gradient and simplex noise are signed. Worley returns the distances to the two nearest feature points. |
| [Shapes and transforms](../shaders/lib/geometry.glsl) | `sdCircle`, `forgeRoundedBox`, `forgeCapsule`, `forgeUnion`, `forgeIntersection`, `forgeDifference`, `forgeSmoothUnion`, `forgePolar`, `forgeCartesian`, `forgeAspectUV`, `forgeRotate`. Signed distance is negative inside. |
| [Timing](../shaders/lib/timing.glsl) | `forgeRange`, `forgeEase`, `forgeEaseIn`, `forgeEaseOut`, `forgeSineEase`, `forgePulse`, `forgeLoopAngle`, `forgeLoopAge`. Progress and age are normalized; angles are in radians. |
| [Color](../shaders/lib/color.glsl) | `forgePalette`, `forgeGradient`, `forgeHSV`, `forgeRGBToHSV`, `forgeToneMap`. The HSV hue wraps from 0 to 1. |
| [Particles](../shaders/lib/particles.glsl) | `forgeHashUint`, `forgeParticleRandom`, `forgeParticleVelocity`, `forgeBallistic`. Use integer seeds and indices for repeatable variation. |
| [Textures and light](../shaders/lib/sampling.glsl) | `forgeSample`, `forgeMaskedCel`, `forgeOutline`, `forgeRim`, `over`, `brightPass`, `blurPass`. A mask uses its alpha channel. |
| [Camera](../shaders/lib/camera.glsl) | `forgeView`, `forgeShake`, `forgeShakeOffset`. Apply these to a UV before sampling the source or a layer. |

For a repeating energy effect, feed `progress` into `forgeLoopNoise(uv * 8.0, progress, 1.2)` to return to the initial noise field. For a single hit, start particles where the objects meet, then animate `forgeBallistic` with each particle's local age. Use `forgePalette` to cool the particles as they move. Pass an envelope of your own to `forgeShakeOffset(phase, amount)` to place recoil on a particular exposure. A short `forgePulse` can drive both the contact flash and the shake so they land together.

Inspect the exported GIF at its real display size. Sample the setup, peak and recovery at 32 px on light and dark backgrounds. Larger shapes, brighter contrast and a clear contact point can help a short effect survive downsampling and GIF palette fitting.
