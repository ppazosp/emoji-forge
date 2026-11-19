vec4 effect(vec2 uv, vec4 art) {
    float angle = forgeLoopAngle(1.0,phase);
    vec2 shift = vec2(sin(angle),cos(angle)) * .045 * intensity;
    vec4 distant = forgeSample(uv + shift * 1.6);
    vec4 middle = forgeSample(uv + shift * .8);
    vec4 near = forgeSample(uv - shift * .7);
    vec4 layers = over(vec4(.19,.46,.88,distant.a * .49),vec4(0.0));
    layers = over(vec4(.64,.44,1.0,middle.a * .62),layers);
    return over(vec4(near.rgb,near.a * edgeFade(uv)),vec4(layers.rgb,layers.a * edgeFade(uv)));
}
