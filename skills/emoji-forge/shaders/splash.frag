vec4 effect(vec2 uv, vec4 art) {
    vec2 origin = anchor + vec2(.03,-.26);
    float localTime = max(0.0, phase - .18);
    float wave = forgeEllipse(uv - origin, vec2(.05,.02) + vec2(.52,.14) * localTime);
    float liquid = halo(wave,.013) * forgePulse(phase,.16,.29,.76);
    for (int i = 0; i < 12; i++) {
        vec2 seed = forgeHash2(vec2(float(i), 71.0));
        vec2 flight = vec2((seed.x - .5) * 1.52, .55 + .68 * seed.y);
        vec2 p = forgeBallistic(origin,flight,localTime,2.80);
        vec2 tail = forgeBallistic(origin,flight,max(0.0,localTime - .052),2.80);
        float streak = halo(sdSegment(uv,p,tail),.011 + .009 * seed.x);
        liquid = max(liquid, streak * forgePulse(phase,.17,.36,.68));
    }
    return over(vec4(.39,.87,1.36,clamp(liquid * intensity * edgeFade(uv),0.0,1.0)),art);
}
