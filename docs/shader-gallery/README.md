# Shader gallery

Forty GPU effects on Tavvik, the hammer-wielding anvil. Each GIF comes from 512 px frames fitted to the Slack 128 px preset. The overview shows all effects on the same 1.6-second clock.

![Animated overview of all 40 shaders](overview.gif)

[32 px on dark](dark-32.png) · [32 px on light](light-32.png) · [Original test cel](fixture.png) · [Write your own shader](../../skills/emoji-forge/references/shaders.md) · [Motion review](REVIEW.md)

Click a name to open the GLSL. Rebuild the gallery from the checkout root with `uv run --project skills/emoji-forge --locked --extra gpu python tools/build_shader_gallery.py`.

## Fire and energy

| [fire](../../skills/emoji-forge/shaders/fire.frag) | [plasma](../../skills/emoji-forge/shaders/plasma.frag) | [lightning](../../skills/emoji-forge/shaders/lightning.frag) |
| --- | --- | --- |
| ![Turbulent flames](fire.gif) | ![Looping plasma filaments](plasma.gif) | ![Forked arcs](lightning.gif) |

| [aura](../../skills/emoji-forge/shaders/aura.frag) | [portal](../../skills/emoji-forge/shaders/portal.frag) |
| --- | --- |
| ![Shifting energy around a silhouette](aura.gif) | ![A swirling rim and inner field](portal.gif) |

## Lighting

| [bloom-glow](../../skills/emoji-forge/shaders/bloom-glow.frag) | [god-rays](../../skills/emoji-forge/shaders/god-rays.frag) | [lens-flare](../../skills/emoji-forge/shaders/lens-flare.frag) |
| --- | --- | --- |
| ![HDR emission for the bloom pass](bloom-glow.gif) | ![Fanning light shafts](god-rays.gif) | ![Flare with optical ghosts](lens-flare.gif) |

| [neon-rim](../../skills/emoji-forge/shaders/neon-rim.frag) | [shine](../../skills/emoji-forge/shaders/shine.frag) | [sparkle](../../skills/emoji-forge/shaders/sparkle.frag) |
| --- | --- | --- |
| ![Colored light around the silhouette](neon-rim.gif) | ![A traveling band of light](shine.gif) | ![Glints and stars](sparkle.gif) |

## Impact and movement

| [shockwave](../../skills/emoji-forge/shaders/shockwave.frag) | [speed-lines](../../skills/emoji-forge/shaders/speed-lines.frag) | [motion-smear](../../skills/emoji-forge/shaders/motion-smear.frag) |
| --- | --- | --- |
| ![Traveling pressure ring](shockwave.gif) | ![Directional streaks](speed-lines.gif) | ![A trailing smear behind the cel](motion-smear.gif) |

| [camera-shake](../../skills/emoji-forge/shaders/camera-shake.frag) | [dust](../../skills/emoji-forge/shaders/dust.frag) | [confetti](../../skills/emoji-forge/shaders/confetti.frag) |
| --- | --- | --- |
| ![A brief shake that settles](camera-shake.gif) | ![Ground-level puffs and particles](dust.gif) | ![Tumbling strips](confetti.gif) |

## Weather and liquids

| [splash](../../skills/emoji-forge/shaders/splash.frag) | [steam](../../skills/emoji-forge/shaders/steam.frag) | [smoke](../../skills/emoji-forge/shaders/smoke.frag) |
| --- | --- | --- |
| ![Ballistic droplets](splash.gif) | ![Translucent rising wisps](steam.gif) | ![A spreading plume](smoke.gif) |

| [snow](../../skills/emoji-forge/shaders/snow.frag) | [rain](../../skills/emoji-forge/shaders/rain.frag) | [bubbles](../../skills/emoji-forge/shaders/bubbles.frag) |
| --- | --- | --- |
| ![Drifting flakes](snow.gif) | ![Slanted raindrops](rain.gif) | ![Rising soap rings](bubbles.gif) |

## Distortion and display

| [heat-haze](../../skills/emoji-forge/shaders/heat-haze.frag) | [glitch](../../skills/emoji-forge/shaders/glitch.frag) | [pixel-sort](../../skills/emoji-forge/shaders/pixel-sort.frag) |
| --- | --- | --- |
| ![Refracted art](heat-haze.gif) | ![Displaced and split colors](glitch.gif) | ![Bands of rearranged pixels](pixel-sort.gif) |

| [crt](../../skills/emoji-forge/shaders/crt.frag) | [black-hole](../../skills/emoji-forge/shaders/black-hole.frag) | [hologram](../../skills/emoji-forge/shaders/hologram.frag) |
| --- | --- | --- |
| ![Scanlines and curved-glass sampling](crt.gif) | ![A gravitational lens and accretion ring](black-hole.gif) | ![Flickering lines and cyan light](hologram.gif) |

## Transitions

| [dissolve](../../skills/emoji-forge/shaders/dissolve.frag) | [shatter](../../skills/emoji-forge/shaders/shatter.frag) | [iris](../../skills/emoji-forge/shaders/iris.frag) |
| --- | --- | --- |
| ![Erosion with an emissive edge](dissolve.gif) | ![Displaced tiles of the cel](shatter.gif) | ![A circular aperture and rim](iris.gif) |

## Depth and perspective

| [beam-burn](../../skills/emoji-forge/shaders/beam-burn.frag) | [beam-perspective](../../skills/emoji-forge/shaders/beam-perspective.frag) | [parallax](../../skills/emoji-forge/shaders/parallax.frag) |
| --- | --- | --- |
| ![A beam and ember trail](beam-burn.gif) | ![A widening beam foreshortened toward the viewer](beam-perspective.gif) | ![Separately moving depth layers](parallax.gif) |

| [orbit](../../skills/emoji-forge/shaders/orbit.frag) |
| --- |
| ![Particles that pass behind and in front of the cel](orbit.gif) |

## Graphic treatments

| [halftone](../../skills/emoji-forge/shaders/halftone.frag) | [toon-outline](../../skills/emoji-forge/shaders/toon-outline.frag) | [ink](../../skills/emoji-forge/shaders/ink.frag) |
| --- | --- | --- |
| ![Printed dots](halftone.gif) | ![A heavier silhouette and simplified tones](toon-outline.gif) | ![Ragged ink edges](ink.gif) |

| [dither](../../skills/emoji-forge/shaders/dither.frag) |
| --- |
| ![Ordered pixel dithering](dither.gif) |
