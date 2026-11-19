vec4 effect(vec2 uv, vec4 art) {
    float phaseLine = fract(uv.y * 19.0 + phase * 2.0);
    float scan = smoothstep(.07,.24,phaseLine) * (1.0 - smoothstep(.52,.86,phaseLine));
    float sweep = halo(uv.y - fract(phase + .13),.11);
    float luminance = dot(art.rgb,vec3(.26,.59,.15));
    vec3 tint = mix(vec3(.07,.17,.27),vec3(.52,1.06,1.24),luminance);
    vec4 emission = vec4(mix(art.rgb,tint,clamp(intensity * .71,0.0,1.0))
        + vec3(.08,.18,.21) * sweep,art.a * (.74 + scan * .18 + sweep * .08));
    return over(emission,vec4(.23,.94,1.30,forgeOutline(uv,.034) * (.36 + .54 * scan)));
}
