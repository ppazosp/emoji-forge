vec4 effect(vec2 uv, vec4 art) {
    float drops = 0.0;
    for (int i = 0; i < 14; i++) {
        vec2 seed = forgeHash2(vec2(float(i), 65.0));
        float fall = fract(seed.y + phase * (1.0 + floor(seed.x * 2.0)));
        vec2 head = vec2(seed.x + (fall - .5) * .15, 1.0 - fall);
        vec2 tail = head + vec2(-.017,.072 + seed.y * .089);
        drops = max(drops, halo(sdSegment(uv,head,tail),.012 + .005 * seed.x));
    }
    float alpha = clamp(drops * .76 * intensity * edgeFade(uv),0.0,1.0);
    return over(art,vec4(.33,.73,1.22,alpha));
}
