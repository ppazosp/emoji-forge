vec4 effect(vec2 uv, vec4 art) {
    float burst = clamp(forgePulse(phase, .14, .40, .86) * intensity, 0.0, 1.0);
    if (burst <= .001) return art;
    vec2 grid = uv * 9.0;
    vec2 cell = floor(grid);
    vec4 pieces = vec4(0.0);
    for (int y = -1; y <= 1; ++y) {
        for (int x = -1; x <= 1; ++x) {
            vec2 tile = cell + vec2(float(x), float(y));
            vec2 center = tile + .5;
            vec2 seed = forgeHash2(tile + vec2(10.5, 19.4));
            vec2 radial = center - 9.0 * anchor;
            vec2 travel = radial / max(length(radial), .5) * (.22 + .42 * seed.x);
            vec2 local = forgeRotate(grid - center - travel * burst, (seed.y - .5) * burst);
            float edge = forgeBox(local, vec2(.5 - .10 * burst));
            float coverage = forgeFill(edge, .009);
            vec4 shard = forgeSample((center + local) / 9.0);
            pieces = over(vec4(shard.rgb, shard.a * coverage), pieces);
        }
    }
    return vec4(pieces.rgb, pieces.a * edgeFade(uv));
}
