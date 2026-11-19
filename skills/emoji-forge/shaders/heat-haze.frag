vec4 effect(vec2 uv, vec4 art) {
    float width = 1.0 - smoothstep(.13,.46,abs(uv.x - anchor.x));
    float heat = width * forgePulse(phase,.15,.42,.91) * intensity;
    float waves = sin(uv.y * 28.0 - TAU * phase * 2.0);
    vec4 shifted = forgeSample(uv + vec2(waves,.16*cos(uv.x * 17.0))*.051*heat);
    vec2 sourceHeat = uv - (anchor - vec2(0.0, .24));
    float ember = forgeFill(forgeEllipse(sourceHeat, vec2(.12, .018)), .008) * heat;
    return over(shifted, vec4(.98, .41, .12, clamp(ember, 0.0, 1.0)));
}
