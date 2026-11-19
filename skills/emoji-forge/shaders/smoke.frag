vec4 effect(vec2 uv, vec4 art) {
    vec2 p = uv - anchor - vec2(.25, -.20);
    float wind = .055 * sin(p.y * 12.0 + TAU * phase);
    vec2 advect = vec2(p.x - wind, p.y);
    float density = forgeLoopNoise(advect * vec2(11.0,5.0),phase,1.7);
    float cone = forgeFill(forgeEllipse(advect - vec2(0.0,.20),vec2(.18,.37)),.055);
    float shadow = smoothstep(.34,.64,density) * cone;
    vec3 color = mix(vec3(.32,.32,.44),vec3(.76,.78,.87),density);
    return over(art,vec4(color,clamp(shadow * intensity * edgeFade(uv),0.0,1.0)));
}
