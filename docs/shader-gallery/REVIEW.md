# Shader motion review

All 40 effects pass. Comparing `458bfc7` with `b12c38e` showed that the 40 fragment files stayed identical. The shared library gained helpers and moved into seven files. Rendering the approved Tavvik cel through the regrouped library reproduced all 40 approved GIFs byte for byte, including the frame delays, palette, loop seam and file size.

The neutral cel changed the appearance of every effect. Its flat face made the beam burn hole and heat haze easy to see, but hid much of the portal behind its body and gave pixel sort fewer colors to pull into streaks. At 32 px, the portal had nine distinct drawings on the neutral face and thirteen on Tavvik. I kept Tavvik for the gallery because the goggles, hammer and gaps in the silhouette show which parts an effect displaces, lights or passes behind.

I compared each export at all sixteen 100 ms positions, including the step from the last exposure back to the first, at 128 px and 32 px on charcoal and warm white. Every final GIF measures 128 × 128 px, loops in 1,600 ms and leaves a transparent border on every frame. The files range from 21,061 bytes (dither) to 93,085 bytes (plasma). [Gallery](README.md) · [Dark sheet](dark-32.png) · [Light sheet](light-32.png)

¹ Counts include each visibly different decoded image once on the 32 px charcoal matte. A held pose can span several exposures.

| Effect | Distinct frames at 32 px, neutral → final¹ | Final review |
| --- | --- | --- |
| Aura | 15 → 15 | **Pass.** The charge originally appeared as isolated specks. A wider, denser band around the silhouette carries the blue-to-gold change through the hold. |
| Beam burn | 12 → 12 | **Pass.** The hole expanded until the character abruptly filled back in. Its radius now contracts during recovery, giving the ember edge a path home. |
| Beam perspective | 11 → 11 | **Pass.** Three floating cyan ticks looked disconnected from the source. Blue between the bright crests joins them into a widening cone at the peak. |
| Black hole | 15 → 15 | **Pass.** The horn and goggles spiral inward first. The pink rim holds their location during the strongest squeeze, and the opening pose returns smoothly. Works as a transition. |
| Bloom glow | 9 → 9 | **Pass.** The old half-cycle crossed the GIF transparency threshold and the halo switched off. Its radius now breathes while a blue inner edge stays visible. |
| Bubbles | 16 → 16 | **Pass.** Fine pastel rims vanished on white. Thicker violet and blue rims carry the highlights upward without filling the bubbles or covering the face. |
| Camera shake | 8 → 8 | **Pass.** A single short jolt has a clear rest on either side. The silhouette stays within the frame. The shake helper now also accepts an independently timed strength. |
| Confetti | 16 → 16 | **Pass.** Wide paper faces and narrow turned edges alternate as pieces fall. The gaps let the character read through the busy peak. |
| CRT | 16 → 16 | **Pass.** The traveling band and green cast read as a display at 32 px. The fine scanlines are clearer at native size and stay inside the cel. |
| Dissolve | 10 → 10 | **Pass.** The bright perforations grow into a deliberate disappearance. The same islands return in reverse order, so the midpoint hold has a purpose. |
| Dither | 4 → 4 | **Pass.** Fine checks averaged into a tint. A coarser ordered grid gives the four stepped phases a visible texture at emoji size. |
| Dust | 13 → 13 | **Pass.** The tan puffs had perfectly oval edges. Small variations break up the contours as they spread from behind the feet. A quiet accent for a landing. |
| Fire | 14 → 14 | **Pass.** The plume resembled a yellow wedge. Tapered, moving tongues and a cooler red tip separate the flame shapes beside the hammer. |
| Glitch | 5 → 6 | **Pass.** Two short interruptions split the silhouette into colored strips, with a readable rest between them. The face recovers cleanly. |
| God rays | 10 → 9 | **Pass.** Pale yellow shafts washed out on white. Distance-dependent amber gives the fan a readable edge on both backgrounds. |
| Halftone | 9 → 9 | **Pass.** Dot sizes modulate within the anvil while the outer contour holds still. At 32 px it works as a print texture under another action. |
| Heat haze | 12 → 13 | **Pass.** The displacement was lost on reduction. Fewer, wider bends now move the silhouette above a narrow orange heat source. |
| Hologram | 16 → 16 | **Pass.** The moving breaks in the cyan outline identify the projection. Enough dark detail survives inside the face to keep the expression. |
| Ink | 16 → 16 | **Pass.** The navy bleed pools around the horn and boots, particularly clearly on white. The lighter interior wash keeps the figure legible on charcoal. |
| Iris | 7 → 7 | **Pass.** The circular crop closes around the face and reverses. The rim is fine on white, but the changing circular silhouette carries the transition. |
| Lens flare | 11 → 10 | **Pass.** The moving cross reads on the goggles at 32 px. The secondary optical ghost is a quieter detail at native size. |
| Lightning | 9 → 9 | **Pass.** Thin white strokes vanished against white. Wider branches with a blue edge and a narrow white core retain a short, sharp strike. |
| Motion smear | 10 → 10 | **Pass.** The cyan trail separates from the leading contour and collapses behind it. The eyes stay sharp throughout. |
| Neon rim | 16 → 16 | **Pass.** Color travels around a continuous outline with enough width to survive reduction. The original surface colors remain visible inside it. |
| Orbit | 16 → 16 | **Pass.** Warm near dots pass in front while cooler far dots disappear behind the head. That occlusion carries the sense of depth even at 32 px. |
| Parallax | 16 → 16 | **Pass.** The far copy broke into peppered pixels at the GIF alpha threshold. A stronger blue far layer separates the three moving planes. |
| Pixel sort | 7 → 8 | **Pass.** Random row offsets disagreed between sample and destination, producing dark blocks. Both now use the same origin. Longer runs pull recognizable bands from the source, and transparent samples retain the underlying color. |
| Plasma | 16 → 16 | **Pass.** One purple circle read like a second portal. Two strands now cross and separate around the silhouette throughout the loop. |
| Portal | 9 → 13 | **Pass.** The flattened magenta ellipse opens behind the waist and closes to rest. The character conceals its middle, placing the opening behind the figure. |
| Rain | 16 → 16 | **Pass.** Hairline drops broke up at 32 px. Slightly wider slanted strokes keep their direction across both themes and fall behind the face. |
| Shatter | 12 → 12 | **Pass.** Fixed square windows made the face look like a checkerboard. The pieces now carry their own source pixels outward, rotate separately, and fit back together. |
| Shine | 6 → 5 | **Pass.** The broad white highlight erased the eye at mid-sweep. Lower peak brightness retains shading beneath the diagonal band. |
| Shockwave | 7 → 9 | **Pass.** The ring expands beyond the horn, thins and disappears. Its rest frames give enough separation for another impact on the loop. |
| Smoke | 16 → 16 | **Pass.** Broad curls separate into small wisps on the open side. The lavender-gray value survives either matte without obscuring the character. |
| Snow | 16 → 16 | **Pass.** Near-white flecks disappeared on the light matte. Blue shading gives the falling flakes a second value against white. |
| Sparkle | 10 → 11 | **Pass.** The glints appear in sequence beside the face and shrink back into points. The largest four-point star carries the read on white. |
| Speed lines | 12 → 12 | **Pass.** An uneven ring of radial strokes directs attention inward. Their open center leaves room for a face or an action pose. |
| Splash | 10 → 10 | **Pass.** The low crown and rising droplets precede a widening, flattened ripple. The feet anchor the water to a surface. |
| Steam | 10 → 11 | **Pass.** Separate oval puffs looked like bubbles. Taller, bent wisps overlap as they rise and disperse beside the character. |
| Toon outline | 9 → 9 | **Pass.** The dark contour thickens and relaxes around the figure. The stroke is clearest on white, while the brighter cel carries the silhouette on charcoal. |

The transparent GIFs give soft light a harder outer edge than a continuous-alpha render. In the revised bloom, fire and aura, changes in shape or color carry the motion through that threshold. For new effects, place the source against the specific pose and try different timings on the same drawing. The shared compositor bounds opacity while retaining overbright color, and the shake offset can follow the timing of any contact.
