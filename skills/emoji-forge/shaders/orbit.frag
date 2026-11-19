vec4 effect(vec2 uv, vec4 art) {
    vec4 behind = vec4(0.0), ahead = vec4(0.0);
    for (int i = 0; i < 7; i++) {
        float progressAlongOrbit = phase + float(i) / 7.0;
        float angle = forgeLoopAngle(1.0,progressAlongOrbit);
        float depth = .5 + .5 * sin(angle);
        vec2 center = anchor + forgeRotate(vec2(cos(angle)*.35,sin(angle)*.18),-.33);
        vec2 p = uv - center;
        float radius = mix(.017,.031,depth);
        float core = forgeFill(sdCircle(p,radius),.007);
        float trail = forgeGlint(p,radius * 1.45,.006) * .55;
        vec3 color = mix(vec3(.27,.61,1.29),vec3(1.15,.78,.40),depth);
        vec4 mote = vec4(color,clamp(max(core,trail) * edgeFade(uv) * intensity,0.0,1.0));
        if (depth > .5) ahead = over(mote,ahead);
        else behind = over(mote,behind);
    }
    return over(ahead,over(art,behind));
}
