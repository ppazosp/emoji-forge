vec4 effect(vec2 uv, vec4 art) {
    float breath = .56 + .44 * sin(TAU * phase);
    float haloAlpha = (forgeOutline(uv, .04) * .70 + forgeOutline(uv, .075) * .24) * breath;
    vec3 light = mix(vec3(.41,.72,1.15), vec3(.83,.95,1.35), breath);
    vec4 subject = vec4(art.rgb + light * art.a * breath * .13 * intensity, art.a);
    return over(subject, vec4(light, clamp(haloAlpha * intensity, 0.0, 1.0)));
}
