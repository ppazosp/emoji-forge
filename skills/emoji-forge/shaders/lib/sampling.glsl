// Texture helpers use bottom-left UV and straight alpha.
vec4 cel(vec2 p) {
    return texture(source, p);
}

vec4 over(vec4 front, vec4 back) {
    // Keep HDR radiance, but layer coverage is always a fraction.
    front.a = clamp(front.a, 0.0, 1.0);
    back.a = clamp(back.a, 0.0, 1.0);
    float a = front.a + back.a * (1.0 - front.a);
    vec3 premult = front.rgb * front.a + back.rgb * back.a * (1.0 - front.a);
    return vec4(premult / max(a, 1e-5), a);
}

vec3 brightPass(vec4 color) {
    return max(color.rgb - 1.0, vec3(0.0)) * color.a;
}

vec4 blurPass(sampler2D tex, vec2 p, vec2 stepUV) {
    vec4 blur = texture(tex, p) * 0.227027;
    blur += (texture(tex, p + stepUV) + texture(tex, p - stepUV)) * 0.194595;
    blur += (texture(tex, p + 2.0 * stepUV) + texture(tex, p - 2.0 * stepUV)) * 0.121622;
    blur += (texture(tex, p + 3.0 * stepUV) + texture(tex, p - 3.0 * stepUV)) * 0.054054;
    blur += (texture(tex, p + 4.0 * stepUV) + texture(tex, p - 4.0 * stepUV)) * 0.016216;
    return blur;
}

vec4 forgeSample(vec2 p) {
    vec2 within = step(vec2(0.0), p) * step(p, vec2(1.0));
    return cel(clamp(p, 0.0, 1.0)) * within.x * within.y;
}

float forgeDilateAlpha(vec2 uv, float radius) {
    float alpha = cel(uv).a;
    for (int i = 0; i < 8; i++) {
        float angle = TAU * float(i) / 8.0;
        alpha = max(alpha, forgeSample(uv + vec2(cos(angle), sin(angle)) * radius).a);
    }
    return alpha;
}

float forgeOutline(vec2 uv, float radius) {
    return max(forgeDilateAlpha(uv, radius) - cel(uv).a, 0.0) * edgeFade(uv);
}

// Sample an offset cel in straight alpha, optionally confining it to a mask or rim.
vec4 forgeMaskedCel(sampler2D mask, vec2 uv, vec2 offset) {
    vec4 paint = forgeSample(uv + offset);
    paint.a *= texture(mask, uv).a;
    return paint;
}

float forgeRim(vec2 uv, vec2 lightDirection, float width) {
    return max(cel(uv).a - forgeSample(uv - lightDirection * width).a, 0.0);
}
