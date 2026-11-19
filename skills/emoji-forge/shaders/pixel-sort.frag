float bandLuma(vec4 pixel) {
    return dot(pixel.rgb,vec3(.299,.587,.114)) * pixel.a;
}

vec4 effect(vec2 uv, vec4 art) {
    float row = floor(uv.y * 27.0);
    float sortWindow = forgePulse(phase,.13,.38,.78) * intensity;
    if (hash(vec2(row, 31.0)) > sortWindow * .80 || art.a < .25) return art;
    float offset = hash(vec2(row, 21.0));
    float position = uv.x * 7.0 + offset;
    float block = floor(position) - offset;
    vec4 colors[5];
    for (int i = 0; i < 5; i++) {
        float x = (block + (float(i) + .5) / 5.0) / 7.0;
        colors[i] = forgeSample(vec2(x,uv.y));
    }
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            if (bandLuma(colors[j]) > bandLuma(colors[j + 1])) {
                vec4 prior = colors[j];
                colors[j] = colors[j + 1];
                colors[j + 1] = prior;
            }
        }
    }
    int index = int(floor(fract(position) * 5.0));
    return vec4(mix(art.rgb,colors[index].rgb,.90 * colors[index].a),art.a);
}
