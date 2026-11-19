vec4 effect(vec2 uv, vec4 art) {
    float falloff = forgePulse(phase,.06,.48,.93) * clamp(intensity,0.0,1.0);
    float erosion = fbm(uv * vec2(12.0,17.0)) * .59 + uv.y * .41;
    float threshold = mix(-.12,.72,falloff);
    float keep = smoothstep(threshold - .012,threshold + .016,erosion);
    float edge = halo(erosion - threshold,.078) * keep;
    vec3 hot = forgePalette(edge,vec3(.86,.30,.08),vec3(1.46,.70,.18),vec3(1.62,1.32,.64));
    return vec4(mix(art.rgb,hot,edge),art.a * keep);
}
