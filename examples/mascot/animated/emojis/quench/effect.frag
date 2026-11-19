// Rounded, lobed wisps with a thin dark-blue edge so they hold up on white.
float puff(vec2 point, float radius) {
    return length(point) - radius;
}

vec4 effect(vec2 uv, vec4 art) {
    float life = smoothstep(.43, .48, progress) *
                 (1.0 - smoothstep(.76, .97, progress));
    vec2 p = uv - anchor;
    p.x += sin(p.y * 27.0 + time * 5.0) * .023;
    float wisp = min(puff(p - vec2(-.017, .040), .035),
                     puff(p - vec2(.019, .086), .040));
    wisp = min(wisp, puff(p - vec2(-.011, .131), .046));
    float outer = (1.0 - smoothstep(.004, .012, wisp)) * life;
    float inner = 1.0 - smoothstep(-.012, -.003, wisp);
    vec3 shade = mix(vec3(.33, .52, .67), vec3(.81, .95, 1.0), inner);
    return over(vec4(shade, outer * edgeFade(uv)), art);
}
