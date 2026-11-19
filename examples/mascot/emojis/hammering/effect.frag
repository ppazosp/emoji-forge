// The two strikes use the same contact time inside each 1.8 s action.
vec4 effect(vec2 uv, vec4 art) {
    float age = mod(time, 1.8) - .81;
    if (age < -.015 || age > .44) return art;
    float t = max(age, 0.0);
    vec2 p = uv - anchor;
    float flash = exp(-t * 36.0) * (1.0 - smoothstep(.008, .036, length(p)));
    vec2 glint = abs(p);
    float rays = exp(-t * 26.0) * exp(-min(glint.x + glint.y * .12, glint.y + glint.x * .12) * 170.0)
                 * (1.0 - smoothstep(.026, .103, length(p)));

    vec2 plane = vec2(p.x, p.y * 2.3);
    float expanding = .012 + t * .84;
    float ring = halo(sdCircle(plane, expanding), .016)
                 * (1.0 - smoothstep(.01, .17, t)) * .88;

    float sparks = 0.0;
    for (int i = 0; i < 11; ++i) {
        float n = float(i);
        float speed = mix(.32, .97, hash(vec2(n, 4.0)));
        float angle = mix(.26, 2.94, hash(vec2(n, 8.0)));
        vec2 velocity = vec2(cos(angle), sin(angle)) * speed;
        vec2 tip = velocity * (t + .031) - vec2(0., 1.08 * t * t);
        float previous = max(t - .046, 0.0);
        vec2 tail = velocity * previous - vec2(0., 1.08 * previous * previous);
        float distance = sdSegment(p, tail, tip);
        float width = mix(.008, .0034, min(t * 2.35, 1.0));
        float life = 1.0 - smoothstep(.14, .40, t + .06 * hash(vec2(n, 7.)));
        sparks = max(sparks, (1.0 - smoothstep(width * .36, width, distance)) * life);
    }
    vec3 gold = mix(vec3(1.6, 1.28, .62), vec3(1.10, .34, .08), smoothstep(.035, .34, t));
    vec4 burst = over(vec4(gold, sparks), vec4(1., .74, .32, ring));
    burst = over(vec4(2.3, 2.06, 1.48, max(flash, rays)), burst);
    burst.a *= edgeFade(uv);
    return over(burst, art);
}
