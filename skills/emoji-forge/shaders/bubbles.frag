vec4 effect(vec2 uv, vec4 art) {
    vec4 bubbles = vec4(0.0);
    for (int i = 0; i < 7; i++) {
        vec2 seed = forgeHash2(vec2(float(i), 91.0));
        float rise = fract(phase + seed.y);
        vec2 center = vec2(anchor.x + (seed.x - .5) * .88 + .044 * sin(rise * TAU),rise);
        vec2 p = uv - center;
        float radius = .029 + .035 * seed.y;
        float rim = forgeRing(p,radius,.015);
        float glint = forgeFill(sdCircle(p - vec2(-.016,.018),.011),.005);
        vec3 color = mix(vec3(.15,.63,1.16),vec3(.93,.55,1.10),seed.x);
        float alpha = max(rim * .78,glint) * edgeFade(uv) * intensity;
        bubbles = over(vec4(color,clamp(alpha,0.0,1.0)),bubbles);
    }
    return over(bubbles,art);
}
