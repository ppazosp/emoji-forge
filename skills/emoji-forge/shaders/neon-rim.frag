vec4 effect(vec2 uv, vec4 art) {
    float rim = forgeOutline(uv, .030);
    float glow = forgeOutline(uv, .060) * .24;
    float hue = .5 + .5 * sin(TAU * (phase + uv.y * .54));
    vec3 light = mix(vec3(.20,.96,1.30), vec3(1.16,.23,.83), hue);
    return over(art, vec4(light, clamp((rim + glow) * intensity,0.0,1.0)));
}
