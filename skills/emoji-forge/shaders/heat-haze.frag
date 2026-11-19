vec4 effect(vec2 uv, vec4 art) {
    float width = 1.0 - smoothstep(.13,.46,abs(uv.x - anchor.x));
    float heat = width * forgePulse(phase,.15,.42,.91) * intensity;
    float waves = sin(uv.y * 36.0 - TAU * phase * 2.0);
    vec4 shifted = forgeSample(uv + vec2(waves,.16*cos(uv.x * 17.0))*.031*heat);
    float embers = forgeRing(uv - (anchor - vec2(0.0,.25)),.17 + .04 * waves,.025) * heat * .41;
    return over(vec4(shifted.rgb,shifted.a * edgeFade(uv)),vec4(1.08,.38,.08,clamp(embers * edgeFade(uv),0.0,1.0)));
}
