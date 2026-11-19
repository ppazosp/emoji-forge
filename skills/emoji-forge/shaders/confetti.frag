vec4 effect(vec2 uv, vec4 art) {
    vec4 paper = vec4(0.0);
    for (int i = 0; i < 13; i++) {
        vec2 seed = forgeHash2(vec2(float(i), 37.0));
        float fall = fract(phase + seed.y);
        vec2 center = vec2(seed.x + .063 * sin(TAU * (fall + seed.x)),1.0 - fall);
        vec2 p = forgeRotate(uv - center,TAU * (fall + seed.x));
        float width = .012 + .010 * abs(cos(TAU * fall));
        float alpha = forgeFill(forgeBox(p,vec2(width,.031)),.004) * edgeFade(uv);
        vec3 color = forgePalette(seed.x,vec3(.99,.30,.69),vec3(1.14,.77,.22),vec3(.21,.93,1.22));
        paper = over(vec4(color,clamp(alpha * intensity,0.0,1.0)),paper);
    }
    return over(art,paper);
}
