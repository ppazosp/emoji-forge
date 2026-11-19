# Shader motion review

All 40 effects earned a place in the gallery. The judgments below use the exported GIFs on charcoal and warm white. I stepped through each decoded exposure at 128 px and 32 px and used nearest-neighbour 4× views to inspect moving edges, transparent holes and palette transitions. Repeated drawings share a GIF exposure. Every loop measured 1,600 ms. The gallery builder checks the canvas border on every decoded frame. [Gallery](README.md) · [Dark sheet](dark-32.png) · [Light sheet](light-32.png)

| Effect | Verdict from the exported animation |
| --- | --- |
| Aura | **Revised.** The charge originally appeared as isolated specks. A wider, denser band around the silhouette carries the blue-to-gold change through the hold. |
| Beam burn | **Revised.** The hole expanded until the character abruptly filled back in. Its radius now contracts during recovery, giving the ember edge a path home. |
| Beam perspective | **Revised.** Three floating cyan ticks looked disconnected from the source. Blue between the bright crests joins them into a widening cone at the peak. |
| Black hole | **Keep.** The horn and goggles spiral inward first. The pink rim holds their location during the strongest squeeze, and the opening pose returns smoothly. Works as a transition. |
| Bloom glow | **Revised.** The old half-cycle crossed the GIF transparency threshold and the halo switched off. Its radius now breathes while a blue inner edge stays visible. |
| Bubbles | **Revised.** Fine pastel rims vanished on white. Thicker violet and blue rims carry the highlights upward without filling the bubbles or covering the face. |
| Camera shake | **Keep.** A single short jolt has a clear rest on either side. The silhouette stays within the frame. The shake helper now also accepts an independently timed strength. |
| Confetti | **Keep.** Wide paper faces and narrow turned edges alternate as pieces fall. The gaps let the character read through the busy peak. |
| CRT | **Keep.** The traveling band and green cast read as a display at 32 px. The fine scanlines are clearer at native size and stay inside the cel. |
| Dissolve | **Keep.** The bright perforations grow into a deliberate disappearance. The same islands return in reverse order, so the midpoint hold has a purpose. |
| Dither | **Revised.** Fine checks averaged into a tint. A coarser ordered grid gives the four stepped phases a visible texture at emoji size. |
| Dust | **Revised.** The tan puffs had perfectly oval edges. Small variations break up the contours as they spread from behind the feet. A quiet accent for a landing. |
| Fire | **Revised.** The plume resembled a yellow wedge. Tapered, moving tongues and a cooler red tip separate the flame shapes beside the hammer. |
| Glitch | **Keep.** Two short interruptions split the silhouette into colored strips, with a readable rest between them. The face recovers cleanly. |
| God rays | **Revised.** Pale yellow shafts washed out on white. Distance-dependent amber gives the fan a readable edge on both backgrounds. |
| Halftone | **Keep.** Dot sizes modulate within the anvil while the outer contour holds still. At 32 px it works as a print texture under another action. |
| Heat haze | **Revised.** The displacement was lost on reduction. Fewer, wider bends now move the silhouette above a narrow orange heat source. |
| Hologram | **Keep.** The moving breaks in the cyan outline identify the projection. Enough dark detail survives inside the face to keep the expression. |
| Ink | **Keep.** The navy bleed pools around the horn and boots, particularly clearly on white. The lighter interior wash keeps the figure legible on charcoal. |
| Iris | **Keep.** The circular crop closes around the face and reverses. The rim is fine on white, but the changing circular silhouette carries the transition. |
| Lens flare | **Keep.** The moving cross reads on the goggles at 32 px. The secondary optical ghost is a quieter detail at native size. |
| Lightning | **Revised.** Thin white strokes vanished against white. Wider branches with a blue edge and a narrow white core retain a short, sharp strike. |
| Motion smear | **Keep.** The cyan trail separates from the leading contour and collapses behind it. The eyes stay sharp throughout. |
| Neon rim | **Keep.** Color travels around a continuous outline with enough width to survive reduction. The original surface colors remain visible inside it. |
| Orbit | **Keep.** Warm near dots pass in front while cooler far dots disappear behind the head. That occlusion carries the sense of depth even at 32 px. |
| Parallax | **Revised.** The far copy broke into peppered pixels at the GIF alpha threshold. A stronger blue far layer separates the three moving planes. |
| Pixel sort | **Revised.** Random row offsets disagreed between sample and destination, producing dark blocks. Both now use the same origin. Longer runs pull recognizable bands from the source, and transparent samples retain the underlying color. |
| Plasma | **Revised.** One purple circle read like a second portal. Two strands now cross and separate around the silhouette throughout the loop. |
| Portal | **Keep.** The flattened magenta ellipse opens behind the waist and closes to rest. The character conceals its middle, placing the opening behind the figure. |
| Rain | **Revised.** Hairline drops broke up at 32 px. Slightly wider slanted strokes keep their direction across both themes and fall behind the face. |
| Shatter | **Revised.** Fixed square windows made the face look like a checkerboard. The pieces now carry their own source pixels outward, rotate separately, and fit back together. |
| Shine | **Revised.** The broad white highlight erased the eye at mid-sweep. Lower peak brightness retains shading beneath the diagonal band. |
| Shockwave | **Keep.** The ring expands beyond the horn, thins and disappears. Its rest frames give enough separation for another impact on the loop. |
| Smoke | **Keep.** Broad curls separate into small wisps on the open side. The lavender-gray value survives either matte without obscuring the character. |
| Snow | **Revised.** Near-white flecks disappeared on the light matte. Blue shading gives the falling flakes a second value against white. |
| Sparkle | **Keep.** The glints appear in sequence beside the face and shrink back into points. The largest four-point star carries the read on white. |
| Speed lines | **Keep.** An uneven ring of radial strokes directs attention inward. Their open center leaves room for a face or an action pose. |
| Splash | **Keep.** The low crown and rising droplets precede a widening, flattened ripple. The feet anchor the water to a surface. |
| Steam | **Revised.** Separate oval puffs looked like bubbles. Taller, bent wisps overlap as they rise and disperse beside the character. |
| Toon outline | **Keep.** The dark contour thickens and relaxes around the figure. The stroke is clearest on white, while the brighter cel carries the silhouette on charcoal. |

The transparent GIFs give soft light a harder outer edge than a continuous-alpha render. In the revised bloom, fire and aura, changes in shape or color carry the motion through that threshold. For new effects, place the source against the specific pose and try different timings on the same drawing. The shared compositor bounds opacity while retaining overbright color, and the shake offset can follow the timing of any contact.

Rebuild the checked-in gallery with `uv run --project skills/emoji-forge --locked --extra gpu python tools/build_shader_gallery.py`. The rendering tests exercise every shader in ModernGL and Chromium WebGL 2.
