vec4 effect(vec2 uv, vec4 art) {
    vec2 p = uv - (anchor + vec2(-.22,.41));
    float angle = atan(p.y, p.x);
    float beams = pow(.5 + .5 * cos(angle * 17.0 + .8 * sin(TAU * phase)), 2.6);
    float reach = exp(-length(p) * 2.3);
    float wash = (.12 + .88 * beams) * reach * smoothstep(.03,.17,-p.y);
    return over(art, vec4(1.27, 1.03, .61, clamp(wash * 1.15 * intensity * edgeFade(uv),0.0,1.0)));
}
