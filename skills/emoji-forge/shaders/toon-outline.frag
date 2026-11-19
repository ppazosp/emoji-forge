vec4 effect(vec2 uv, vec4 art) {
    float emphasis = .5 + .5 * sin(TAU * phase);
    float thickness = (.022 + .013 * emphasis) * max(.15,intensity);
    float stroke = forgeOutline(uv,thickness);
    vec3 bands = floor(clamp(art.rgb,0.0,.999) * 4.0 + .27 * emphasis) / 3.7;
    return over(vec4(mix(art.rgb,bands,.52),art.a),vec4(.11,.16,.28,stroke));
}
