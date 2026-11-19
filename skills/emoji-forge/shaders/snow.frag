vec4 effect(vec2 uv, vec4 art) {
    float snow = 0.0;
    for (int i = 0; i < 14; i++) {
        vec2 seed = forgeHash2(vec2(float(i), 82.0));
        float fall = fract(seed.y + phase);
        vec2 center = vec2(seed.x + .045 * sin(TAU * (fall + seed.x)),1.0 - fall);
        vec2 p = uv - center;
        float width = .013 + .014 * seed.y;
        float arms = forgeGlint(forgeRotate(p,TAU * (phase + seed.x)),width,.006);
        float core = forgeFill(sdCircle(p,width * .54),.004);
        snow = max(snow,max(core,arms) * (.55 + .45 * seed.y));
    }
    return over(vec4(mix(vec3(.39,.67,.94),vec3(.90,.96,1.24),snow*snow),clamp(snow * intensity * edgeFade(uv),0.0,1.0)),art);
}
