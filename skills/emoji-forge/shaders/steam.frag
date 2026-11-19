vec4 effect(vec2 uv, vec4 art) {
    float plume = 0.0;
    for (int i = 0; i < 5; i++) {
        float age = fract(phase * 2.0 + float(i) / 5.0);
        vec2 center = anchor + vec2(.27 + .04 * sin(age * 8.0 + float(i)), -.23 + .57 * age);
        vec2 size = vec2(.021,.073) * (1.0 + age * .7);
        float life = smoothstep(0.0,.14,age) * (1.0 - smoothstep(.65,1.0,age));
        plume = max(plume,forgeFill(forgeEllipse(uv - center - vec2(.026*sin((uv.y-center.y)*22.0 + age*4.0),0.0),size),.013) * life);
    }
    vec3 color = mix(vec3(.38,.63,.82), vec3(.87,.97,1.23), plume);
    return over(art,vec4(color,clamp(plume * intensity * edgeFade(uv),0.0,1.0)));
}
