vec4 effect(vec2 uv, vec4 art) {
    vec2 p = uv - anchor;
    float turbulence = forgeLoopNoise(p * 7.0, phase, 1.1);
    float wave = .31 + .085 * (turbulence - .5) + .025 * sin(TAU * phase);
    float angle = atan(p.y, p.x);
    float strand = .035 * sin(angle * 4.0 - TAU * phase + turbulence * 5.0);
    float field = max(forgeRing(p, wave + strand, .028), .80 * forgeRing(p, wave - strand, .022));
    vec3 color = forgePalette(turbulence, vec3(.38,.1,.92), vec3(.89,.24,1.11), vec3(.44,1.25,1.7));
    return over(art, vec4(color, clamp(field * edgeFade(uv) * intensity, 0.0, 1.0)));
}
