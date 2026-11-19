// A readable luminous pictogram, with a lofted point of light around it.
vec4 effect(vec2 uv, vec4 art) {
    float lit = smoothstep(.37, .405, progress) *
                (1.0 - smoothstep(.77, .99, progress));
    vec2 p = uv - anchor;
    float glass = length(p - vec2(0., .020)) - .048;
    float base = max(abs(p.x) - .021, abs(p.y + .041) - .018);
    float shape = min(glass, base);
    float bulb = (1.0 - smoothstep(0., .009, shape)) * lit;
    float fill = 1.0 - smoothstep(-.012, -.005, glass);
    vec3 color = mix(vec3(.39, .18, .037), vec3(1.55, 1.2, .35), fill);
    if (base < 0. && glass > 0.) {
        color = vec3(.52, .32, .12);
    }
    float halo = (1.0 - smoothstep(.037, .115, length(p))) * lit * .37;
    vec4 focused = over(vec4(color, bulb), vec4(1.3, .64, .10, halo));
    return over(vec4(focused.rgb, focused.a * edgeFade(uv)), art);
}
