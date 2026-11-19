float bolt(vec2 uv, vec2 end, float seed, float width) {
    float h = clamp((uv.y - end.y) / max(.13, .94 - end.y), 0.0, 1.0);
    float wander = (noise(vec2(h * 13.0, seed)) - .5) * .16 * sin(3.14159 * h);
    float x = mix(end.x, end.x + .18, h) + wander;
    float span = smoothstep(end.y - .015, end.y + .02, uv.y) * (1.0 - smoothstep(.89, .96, uv.y));
    return halo(uv.x - x, width) * span;
}

vec4 effect(vec2 uv, vec4 art) {
    float flash = forgePulse(phase, .16, .32, .65);
    float seed = floor(phase * 8.0);
    vec2 foot = anchor + vec2(.15, -.12);
    float core = bolt(uv, foot, seed, .018);
    float branch = bolt(uv, foot + vec2(-.21, .20), seed + 5.0, .011);
    float light = clamp(max(core, branch) * flash * intensity * edgeFade(uv), 0.0, 1.0);
    return over(art, vec4(mix(vec3(.26,.56,1.52), vec3(1.52,1.56,1.66), core), light));
}
