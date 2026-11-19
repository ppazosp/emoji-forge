float orderedPattern(vec2 p) {
    vec2 q = mod(p,4.0);
    vec2 low = mod(q,2.0);
    vec2 high = floor(q/2.0);
    float coarse = 2.0 * mod(low.x + low.y,2.0) + low.y;
    float detail = 2.0 * mod(high.x + high.y,2.0) + high.y;
    return (coarse * 4.0 + detail + .5) / 16.0;
}

vec4 effect(vec2 uv, vec4 art) {
    vec2 grid = floor(uv * 42.0 + vec2(floor(phase*4.0),0.0));
    float threshold = orderedPattern(grid);
    vec3 graded = clamp(art.rgb * 1.09 + vec3(.026,-.009,.048),0.0,1.0);
    vec3 swatches = clamp(floor(graded * 3.0 + threshold) / 3.0,0.0,1.0);
    return vec4(mix(art.rgb,swatches,clamp(intensity,0.0,1.0)),art.a);
}
