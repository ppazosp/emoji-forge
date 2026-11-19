vec4 effect(vec2 uv, vec4 art) {
    vec2 p = uv - anchor;
    float sweep = forgePulse(phase,.09,.46,.90) * clamp(intensity,0.0,1.0);
    float radius = mix(.82,.17,sweep);
    float inside = 1.0 - smoothstep(radius-.025,radius+.011,length(p));
    float line = forgeRing(p,radius,.017) * sweep * edgeFade(uv);
    return over(vec4(art.rgb,art.a * inside),vec4(.63,.94,1.24, line));
}
