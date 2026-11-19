vec4 effect(vec2 uv, vec4 art) {
    float light = smoothstep(.58, .73, time) * (1.0 - smoothstep(1.17, 1.49, time));
    vec2 p = uv - anchor;
    float bulb = length(p - vec2(0., .018)) - .049;
    float neck = max(abs(p.x) - .020, abs(p.y + .041) - .018);
    float opaque = (1.0 - smoothstep(0., .007, min(bulb, neck))) * light;
    vec3 ink = mix(vec3(.34, .20, .09), vec3(1.34, 1.07, .42), 1.0 - smoothstep(-.012, -.005, bulb));
    vec2 top = p - vec2(0., .018);
    float filament = min(sdSegment(top, vec2(-.015, .010), vec2(0., -.009)),
                         sdSegment(top, vec2(.015, .010), vec2(0., -.009)));
    filament = min(filament, sdSegment(top, vec2(0., -.009), vec2(0., -.033)));
    ink = mix(ink, vec3(.54, .27, .075), (1.0 - smoothstep(.002, .005, filament)));
    float ray = 0.0;
    for (int i = 0; i < 5; ++i) {
        float angle = .15 + float(i) * .70;
        vec2 direction = vec2(cos(angle), sin(angle));
        ray = max(ray, 1.0 - smoothstep(.003, .007, sdSegment(top, direction * .065, direction * .084)));
    }
    float halo_alpha = halo(length(p), .096) * .31 * light;
    vec4 icon = over(vec4(ink, opaque), vec4(1.16, .64, .15, halo_alpha));
    icon = over(icon, vec4(1.34, .89, .26, ray * light * .78));
    return over(vec4(icon.rgb, icon.a * edgeFade(uv)), art);
}
