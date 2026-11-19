vec4 effect(vec2 uv, vec4 art) {
    vec2 center = anchor + vec2(.24 * sin(TAU * phase), .14);
    vec2 p = uv - center;
    float glint = forgeGlint(p, .18, .018);
    float streak = halo(p.y,.018) * (1.0 - smoothstep(.07,.44,abs(p.x))) * .72;
    float ghost = forgeRing(p + vec2(.18,.095), .055, .015) * .52;
    vec3 color = mix(vec3(.62,.41,1.16), vec3(1.49,1.32,.92), glint);
    return over(vec4(color, clamp(max(max(glint, streak), ghost) * edgeFade(uv) * intensity,0.0,1.0)), art);
}
