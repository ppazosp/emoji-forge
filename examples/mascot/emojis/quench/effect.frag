vec4 effect(vec2 uv, vec4 art) {
    float age = time - .63;
    if (age < 0.0 || age > .69) return art;
    vec2 p = uv - anchor;
    float life = 1.0 - smoothstep(.25, .68, age);
    p.x += sin(p.y * 29.0 + time * 8.0) * .021;
    p.y -= age * .11;
    float plume = min(length(p - vec2(0., .035)) - .029,
                      length(p - vec2(.024, .079)) - .036);
    plume = min(plume, length(p - vec2(-.013, .121)) - .037);
    float opacity = (1.0 - smoothstep(.003, .012, plume)) * life;
    vec3 steam = mix(vec3(.36, .59, .73), vec3(.85, .97, 1.0), 1.0 - smoothstep(-.012, -.003, plume));
    return over(vec4(steam, opacity * edgeFade(uv)), art);
}
