# Shader motion review

The gallery uses the same Tavvik cel to make changes in motion and visibility easy to compare. Each sequence starts from 512 px renders and is fitted to the Slack preset. Follow the [individual GIFs](README.md) for timing and use the [dark](dark-32.png) and [light](light-32.png) sheets to compare five frames at 32 px.

## First pass and fixes

- **Hologram.** The saturated cyan hid Tavvik’s face. Lowered the tint in the shadows and kept more of the original value range. The revised frame retains a face beneath the scanlines.
- **Fire.** The first flame was mostly behind Tavvik. Moved the effect beside the cel and used the bloom resolve to fade the plume before the canvas edge. Rechecked all exported frames for opaque borders.
- **God-rays and shockwave.** Thin lines were hard to read in the small review. Widened the rays and increased the ring intensity in the gallery. Both have a shape that can be followed through the sequence.
- **Low-amplitude treatments.** Heat haze, pixel sort and ordered dithering are easiest to see at 128 px. At 32 px, try shaping the next pass around the action so the effect can carry more of the frame.

## Technical pass

All 40 files are 128×128 looping GIFs, between 21,545 and 91,476 bytes. The GIFs retain 1.6-second timelines with 4 to 16 encoded frames. The gallery builder also checks every frame for opaque pixels along the border. The test suite renders each fragment in ModernGL and headless WebGL 2.

Regenerate the gallery from the checkout root with `uv run --project skills/emoji-forge --locked --extra gpu python tools/build_shader_gallery.py`.

## Motion designer hand-off

Check the impact and recovery of the rings, beams, and particles. Look for lost silhouettes under light effects, discontinuities in the repeating motion, and unreadable effects at the target size. Note the shader, timestamp, background and desired change in the review. The library is staged for this review before release.
