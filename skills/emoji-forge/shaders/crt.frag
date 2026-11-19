vec4 effect(vec2 uv, vec4 art) {
    vec2 p = uv - anchor;
    vec2 warped = anchor + p * (1.0 + dot(p,p) * .21);
    vec4 frame = forgeSample(warped);
    float scan = .76 + .24 * cos(uv.y * TAU * 24.0 - TAU * phase * 2.0);
    float snaking = forgeRing(vec2(0.0,uv.y - fract(phase + .2)),.0,.10) * .31;
    vec3 shifted = frame.rgb * vec3(.79,1.16,1.04) * scan + vec3(.12,.36,.26) * snaking;
    return vec4(mix(art.rgb,shifted,clamp(intensity,0.0,1.0)),frame.a * edgeFade(uv));
}
