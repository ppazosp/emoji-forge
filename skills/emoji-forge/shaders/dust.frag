vec4 effect(vec2 uv, vec4 art) {
    float puff = 0.0;
    for (int i = 0; i < 11; i++) {
        vec2 seed = forgeHash2(vec2(float(i), 61.0));
        float age = max(0.0, phase - .16 - seed.y * .13);
        vec2 velocity = vec2((seed.x - .5) * 1.28, .31 + seed.y * .14);
        vec2 center = forgeBallistic(anchor + vec2(0.0,-.28), velocity,age,.42);
        float life = smoothstep(0.0,.11,age) * (1.0 - smoothstep(.31,.64,age));
        vec2 radius = vec2(.037,.023) * (1.0 + age + seed.x);
        puff = max(puff,forgeFill(forgeEllipse(uv - center,radius) + .016*(noise(uv*54.0 + seed)-.5),.010) * life);
    }
    return over(art,vec4(.93,.73,.50,clamp(puff * intensity * edgeFade(uv),0.0,1.0)));
}
