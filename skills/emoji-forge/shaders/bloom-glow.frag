vec4 effect(vec2 uv, vec4 art) {
    float breath = .56 + .44 * sin(TAU * phase);
    float haloAlpha = forgeOutline(uv, .014 + .026 * breath) * .85;
    float skirt = forgeOutline(uv, .024 + .052 * breath) * .38;
    haloAlpha = max(haloAlpha, skirt) * (.75 + .25 * breath);
    vec3 light = mix(vec3(.22,.55,.89), vec3(.83,.95,1.35), breath);
    vec4 subject = vec4(art.rgb + light * art.a * breath * .13 * intensity, art.a);
    return over(subject, vec4(light, clamp(haloAlpha * intensity, 0.0, 1.0)));
}
