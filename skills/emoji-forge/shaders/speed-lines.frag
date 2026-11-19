vec4 effect(vec2 uv, vec4 art) {
    vec2 p = uv - anchor;
    float angle = atan(p.y, p.x) / TAU;
    float sector = floor(angle * 32.0);
    float width = halo(fract(angle * 32.0) - .5, .19);
    float start = .26 + .19 * hash(vec2(sector, 24.0));
    float energy = forgePulse(phase,.14,.40,.84) * intensity;
    float line = width * smoothstep(start, start + .05, length(p)) * energy * edgeFade(uv);
    return over(art, vec4(.72,1.04,1.30,clamp(line,0.0,1.0)));
}
