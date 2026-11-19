# Review tools and tips

Start with the target checks for file dimensions, bytes and format limits. Machine checks can also measure decoded edges and seams, and optionally body-mask drift and face containment. An intentional matte may occupy the edge. Use the actual export for visual review.

- `forge strips` shows each frame with a timestamp. Try the intended display size, the native canvas and a 4× view on light and dark backgrounds. The zoom can expose clipping, palette artefacts and stray pixels.
- Use a body mask that excludes props and free limbs. Check scale and anchor against the model throughout the loop. Annotate small intentional squash around the hit and confirm it returns to baseline without a jump.
- Step through held props at full resolution. Follow the same fist, grip and wrist pivot from frame to frame. Check that the handle crosses the palm, that the prop follows the hand, and that any change of angle comes from the action. A flip or separate spin reads as a broken grip. Use the [per-frame prop strip](production-pipeline.md#cross-pack-reviews) to spot discontinuities.
- Play the animation at normal speed to see if it achieves the intended effect. Watch the seam, timing, attachments, contrast or expression when those details matter to the idea.
- `forge snapshot` can save a baseline before a revision. `forge compare` presents versions side by side on the same clock. A comparison helps when you change an art technique or effect.
- For a detailed handoff, record what you observed, the version and the frame numbers or timestamps for any changes you suggest. After a revision, check the affected export again.

An example observation might be “Frames 5–6 at 1.10–1.38 s. The raised hand is readable on light but blends with the outline on dark at 22 px.” Name the intended result and let that guide the fix.

## Review brief template

Use a short brief and the stage ZIP from `forge review-pack` for each hand-off. In one-shot mode, run these as internal motion-design reviews. Share stage materials with the user when they request a checkpoint.

- **Bible** • Check the proposed reference views, construction, palette, and whether the name or silhouette resembles an existing character.
- **Storyboard** • Check the panels, intended reaction and animatic timing.
- **Keys** • Compare the poses to the model and expression sheets at display size.
- **In-betweens** • Check anticipation, spacing, easing, readable holds, scale, anchor and the loop seam. Play the rhythm as well as stepping through individual frames.
- **Effects** • Compare clean and treated cels. For a hit, look for a flash at the contact point, a readable outward burst, and a short decay that leaves the pose clear.
- **Final** • Check the platform file limits and inspect the overview, exported cels and strips.

Return a verdict, the affected frame or panel IDs, an observation against the bible or storyboard, and the smallest adjustment worth trying. Record the review and snapshot before the next revision. [Production pipeline and hand-offs](production-pipeline.md)

## Asset, integration and consistency briefs

- **Asset** • Compare each prop, character feature or effect sheet against the bible. Check that its views describe a single construction, palette and intended size. Record the exact view or state that needs revision.
- **Integration** • Compare grips, worn parts, contact and overlaps across the integration sheet and its sequences. Watch the attachment through anticipation, contact and release. Include affected exposure numbers in the verdict.
- **Consistency** • Read the lineup across all columns. Compare repeated features and props in the final exports, including stills. Confirm that the reference body mask passes the scale and anchor tolerance across the animated pack. Re-open any matching asset or integration review when a mismatch turns up.

Bundle each level with `forge review-pack`. Save the verdict and the relevant lineup rows or measured outliers with the version before fixing them.
