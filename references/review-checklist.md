# Motion review

Work as an expert motion designer. Before **each review or fix pass**, snapshot the current art, timeline, exports and report to a new version folder. Keep approved revisions intact. For a change of technique, put old and new art side by side on the same timing, scale and backgrounds before selecting one.

1. Open the final encoded GIFs. Watch successive loops at normal speed. Check that each tells one clear action, holds its expression, recovers and crosses the seam smoothly.
2. Step through **every decoded frame** at canvas size, 4× nearest-neighbour zoom and the smallest display size. Inspect light and dark backgrounds at all three sizes. Use `make_strips.py` with the relevant sizes, then check playback again for spacing and holds.
3. At 4×, inspect texture, stroke width, mask edges, palette bands, halos and stray pixels. At native size, check body registration, joined wrists and ankles, stable feet and centred face. At the smallest size, judge silhouette, expression, contrast and action. Check the end rest has life without drawing attention.
4. Check that props have believable contact and that shaders align to contact or release. A soft glow can use a dark matte if it preserves the effect. Check both themes and make sure the matte has a clean boundary.
5. Write one result per emoji with verdict, version, exposure or decoded frame numbers, timestamps and a brief reason for any failed frame. Include export bytes, duration and frame count from the checks. For a static emoji, review its defining pose and expression at the same sizes.
6. Fix only in a fresh snapshot. Rerun machine checks, regenerate strips and review the affected emoji from start to seam, including previously passing frames.

| Emoji | Verdict | Frames / time | Observation |
| --- | --- | --- | --- |
| wave | Fail | 5–6 / 1.10–1.38 s | The wrist jumps on reversal and the hand overlaps the cheek at 22 px. |
| wave (next version) | Pass | 1–14 / whole loop | The new wrist pose keeps the hand clear and the half-blink carries through the seam. |
