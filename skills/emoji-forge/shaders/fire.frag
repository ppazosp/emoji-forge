vec4 effect(vec2 uv, vec4 art) {
    vec2 p = uv - anchor;
    float strength = envelope(.05, .3, .62, .94);
    vec2 flow = p * vec2(12.0, 5.0) - vec2(0.0, seconds * 2.8);
    float plume = fbm(flow + vec2(fbm(flow + 4.0), 0.0) * 2.0);
    float tongue = .5 + .5 * sin(p.x * 57.0 + 8.0 * plume);
    float taper = 1.0 - smoothstep(.01, .25, abs(p.x));
    float height = (.035 + taper * (.09 + .15 * tongue + .12 * plume)) * strength;
    float flame = smoothstep(-.025, .025, height - p.y - abs(p.x) * .85)
        * smoothstep(-.02, .03, p.y) * strength;
    vec3 color = mix(vec3(1.38, 1.06, .32), vec3(.89, .16, .04), smoothstep(.02, .86, p.y / max(.02, height)));
    vec4 warm = cel(uv + vec2((plume - .5) * .018 * flame, 0));
    return over(warm, vec4(color, flame));
}
