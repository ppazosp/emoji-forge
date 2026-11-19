// HSV uses normalized hue, saturation and value. Value may exceed one for emission.
vec3 forgeHSV(vec3 hsv) {
    vec3 wheel = abs(fract(hsv.x + vec3(0.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0);
    return hsv.z * mix(vec3(1.0), clamp(wheel - 1.0, 0.0, 1.0), hsv.y);
}

vec3 forgeRGBToHSV(vec3 rgb) {
    float peak = max(rgb.r, max(rgb.g, rgb.b));
    float trough = min(rgb.r, min(rgb.g, rgb.b));
    float range = peak - trough;
    if (range <= 1e-6) return vec3(0.0, 0.0, peak);
    float hue;
    if (peak == rgb.r) hue = (rgb.g - rgb.b) / range;
    else if (peak == rgb.g) hue = 2.0 + (rgb.b - rgb.r) / range;
    else hue = 4.0 + (rgb.r - rgb.g) / range;
    return vec3(fract(hue / 6.0), range / max(peak, 1e-6), peak);
}

vec3 forgeGradient(vec3 low, vec3 high, float t) {
    return mix(low, high, clamp(t, 0.0, 1.0));
}

// Reinhard compression for nonnegative HDR light when resolving a final pass.
vec3 forgeToneMap(vec3 rgb) {
    rgb = max(rgb, 0.0);
    return rgb / (1.0 + rgb);
}
