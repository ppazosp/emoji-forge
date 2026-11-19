vec4 effect(vec2 uv, vec4 art) {
    vec2 p = uv - anchor;
    float distanceToCenter = length(p);
    float pull = forgePulse(phase,.05,.39,.93) * intensity;
    float well = exp(-distanceToCenter * 4.3) * pull;
    vec2 spiraled = forgeRotate(p,well * 5.4) * (1.0 + 1.9 * well);
    vec4 warped = forgeSample(anchor + spiraled);
    float rim = forgeRing(p,.19 + .075 * pull,.018) * pull;
    float tail = forgeRing(p,.27 + .092 * pull,.024) * pull * .37;
    return over(vec4(warped.rgb,warped.a * edgeFade(uv)),vec4(1.27,.47,.80,clamp((rim + tail)*edgeFade(uv),0.0,1.0)));
}
