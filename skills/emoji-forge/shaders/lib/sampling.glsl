// Sample an offset cel in straight alpha, optionally confining it to a mask or rim.
vec4 forgeMaskedCel(sampler2D mask, vec2 uv, vec2 offset) {
    vec4 paint = forgeSample(uv + offset);
    paint.a *= texture(mask, uv).a;
    return paint;
}

float forgeRim(vec2 uv, vec2 lightDirection, float width) {
    return max(cel(uv).a - forgeSample(uv - lightDirection * width).a, 0.0);
}
