vec4 effect(vec2 uv, vec4 art) {
    vec2 p = uv - anchor - vec2(.06,.045);
    float travel = forgePulse(phase,.15,.42,.77);
    vec2 axis = normalize(vec2(.96,-.34));
    float along = dot(p,axis);
    float transverse = abs(dot(p,vec2(-axis.y,axis.x)));
    float spread = .012 + max(along,0.0) * (.17 + .38 * travel);
    float cone = (1.0 - smoothstep(spread * .30,spread,transverse))
                 * smoothstep(-.018,.026,along) * (1.0 - smoothstep(.37,.55,along));
    float rings = pow(.52 + .48 * cos((along + .029)*65.0 - TAU*phase*3.0),5.0);
    float light = cone * (.44 + .56 * rings) * travel * edgeFade(uv);
    return over(vec4(.54,1.17,1.50,clamp(light * intensity,0.0,1.0)),art);
}
