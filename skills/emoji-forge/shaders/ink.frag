vec4 effect(vec2 uv, vec4 art) {
    float grain = forgeLoopNoise(uv * 21.0,phase,1.05);
    float bleed = smoothstep(.24,.64,grain) * forgeOutline(uv,.028 + .022 * grain);
    float luma = dot(art.rgb,vec3(.27,.62,.11));
    float wash = clamp(luma * .81 + grain * .28,0.0,1.0);
    vec3 inkColor = mix(vec3(.09,.135,.28),vec3(.79,.90,.99),wash);
    vec4 figure = vec4(mix(art.rgb,inkColor,clamp(intensity,0.0,1.0)),art.a);
    return over(figure,vec4(.14,.20,.37,clamp(bleed*intensity,0.0,1.0)));
}
