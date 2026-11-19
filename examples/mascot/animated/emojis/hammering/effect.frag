// Burst at the anvil face. Streaks diverge in the upper half of the burst.
vec4 effect(vec2 uv, vec4 art) {
    float burst = 1.0 - smoothstep(.20, .36, abs(progress - .535));
    burst *= step(.46, progress) * (1.0 - smoothstep(.57, .78, progress));
    float trail = 0.0;
    for (int i = 0; i < 8; ++i) {
        float index = float(i);
        float angle = .18 + .39 * index;
        vec2 ray = vec2(cos(angle), sin(angle));
        vec2 local = uv - anchor;
        float along = dot(local, ray);
        float across = abs(dot(local, vec2(-ray.y, ray.x)));
        float start = .027 + .024 * hash(vec2(index, 1.0));
        float end = start + .035 + .047 * hash(vec2(index, 2.0));
        float streak = smoothstep(start - .008, start, along) *
                       (1.0 - smoothstep(end, end + .008, along)) *
                       (1.0 - smoothstep(.003, .010, across));
        trail = max(trail, streak);
    }
    float flash = 1.0 - smoothstep(.013, .034, length(uv - anchor));
    return over(vec4(1.85, .91, .16, max(trail, flash) * burst * edgeFade(uv)), art);
}
