---
name: emoji-forge
description: Make or revise custom emojis, stickers, reactions, and animated GIF emoji from character or style references. Use for solo artwork or a named pack of static PNGs and drawn loops, including optional GLSL effects and target-specific exports.
---

# Emoji Forge

1. Set the brief. Get the references, reactions, format and smallest display size. Use `forge new`, then fill in the [pack manifest](references/workflow.md). Load the [Slack reference](references/slack.md) only for Slack.
2. Lock the style before drawing. Write a style sheet from real reference images. Match body colour, texture, line weight, face, hands, legs and feet. With no supplied reference, draw an original turnaround or neutral pose and use it as the reference. Variants change posture and attitude while keeping the same character design.
3. Storyboard one unmistakable action per animated emoji. Draw the anticipation, action and follow-through. Build [expressions](references/expressions.md) around the recognisable resting face. Give each static emoji a single readable gesture or expressive pose.
4. Generate each key pose with image generation using the locked reference. Register the cels against the body-mask centroid and scale. Preserve deliberate moves as explicit offsets. Keep feet and limbs planted or deliberately moving, use outlined hands with open or neutral interiors, keep the face centred, and leave canvas clearance. Draw or edit in-betweens or hold a clean cel. Never use optical flow, blended frames, or a cut-out rig in place of approved drawings.
5. Time the drawings for readability. Start around 3–5 seconds with a readable peak hold, a living 150–250 ms end rest and a continuous seam. Read [animation timing](references/animation-timing.md). When effects help tell the action, follow the [GPU cookbook](references/shaders.md) and check the result at target size.
6. Run `forge all` to render and check the encoded files and annotated cels. For stills, check dimensions, bytes and border. Export static art as PNG, with SVG optional when appropriate. Before **every review or fix pass**, run `forge snapshot` to preserve the version. Have a motion designer inspect every frame at native size, 4× and smallest display size on light and dark. Record a pass or fail per emoji with frame numbers, fix in a fresh snapshot and repeat. Show side-by-side proof before switching art technique. Use the [review rubric](references/review-checklist.md) and [failure patterns](references/lessons.md).
7. Put short names under every emoji in one flat preview grid. Deliver the animated grid, still PNG, timestamped strips, individual named files, ordered `NAMES.md` and ZIP. Keep the stronger animated version of duplicate reactions and let the user prune weak entries.
