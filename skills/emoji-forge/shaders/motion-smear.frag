vec4 effect(vec2 uv, vec4 art) {
    float sweep = forgePulse(phase,.15,.40,.71);
    vec2 direction = normalize(vec2(.92,.37));
    float trace = 0.0;
    for (int i = 1; i <= 7; i++) {
        float u = float(i) / 7.0;
        trace = max(trace, forgeSample(uv + direction * (.25 * sweep * u)).a * (1.0 - .8 * u));
    }
    trace *= sweep * edgeFade(uv);
    vec3 ink = mix(vec3(.28,.46,1.02), vec3(.73,1.09,1.29), trace);
    return over(art,vec4(ink,clamp(trace * intensity,0.0,1.0)));
}
