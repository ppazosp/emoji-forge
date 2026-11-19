vec4 effect(vec2 uv, vec4 art) {
    vec2 movement = forgeShake(phase,.064 * intensity);
    float zoom = 1.0 + .065 * forgePulse(phase,.16,.39,.71) * intensity;
    vec4 frame = forgeSample(forgeView(uv, anchor, movement, zoom));
    return vec4(frame.rgb, frame.a * edgeFade(uv));
}
