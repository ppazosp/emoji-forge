vec4 effect(vec2 uv, vec4 art) {
    float burst = forgePulse(phase,.14,.40,.86) * intensity;
    if (burst <= .001) return art;
    vec2 grid = uv * 9.0;
    vec2 cell = floor(grid);
    vec2 local = fract(grid) - .5;
    vec2 direction = (forgeHash2(cell + vec2(10.5,19.4)) - .5) * vec2(.22,.17);
    vec2 uvShift = uv - direction * burst;
    vec4 shard = forgeSample(uvShift);
    float gap = 1.0 - smoothstep(.45 - .16 * burst,.51 - .12 * burst,max(abs(local.x),abs(local.y)));
    return vec4(shard.rgb + vec3(.12,.23,.48) * (1.0 - gap) * burst,shard.a * gap * edgeFade(uv));
}
