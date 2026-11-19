// Transform UVs before sampling a layer or the whole scene.
vec2 forgeView(vec2 uv, vec2 center, vec2 translation, float zoom) {
    return center + (uv - center - translation) / max(0.1, zoom);
}

vec2 forgeShakeOffset(float framePhase, float strength) {
    return vec2(sin(framePhase * 79.0), cos(framePhase * 116.0)) * strength;
}

vec2 forgeShake(float framePhase, float amplitude) {
    return forgeShakeOffset(framePhase, forgePulse(framePhase, 0.19, 0.36, 0.67) * amplitude);
}
