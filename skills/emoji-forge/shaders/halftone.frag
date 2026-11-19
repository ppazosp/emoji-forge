vec4 effect(vec2 uv, vec4 art) {
    vec2 screen = forgeRotate(uv - anchor,.26) * 22.0;
    vec2 local = fract(screen) - .5;
    float brightness = dot(art.rgb,vec3(.30,.59,.11));
    float setting = clamp(intensity,0.0,1.0);
    float pulse = .75 + .25 * sin(TAU * phase);
    float dotSize = mix(.47,.11,brightness) * pulse;
    float dotInk = forgeFill(sdCircle(local,dotSize),.075);
    vec3 color = mix(art.rgb,vec3(.075,.12,.23),dotInk * setting * .83);
    return vec4(color,art.a);
}
