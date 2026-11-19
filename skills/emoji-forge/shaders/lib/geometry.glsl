// Signed distances are negative inside. Keep primitive inputs in the same units.
float forgeRoundedBox(vec2 p, vec2 halfSize, float radius) {
    radius = clamp(radius, 0.0, min(halfSize.x, halfSize.y));
    return forgeBox(p, halfSize - radius) - radius;
}

float forgeCapsule(vec2 p, vec2 start, vec2 end, float radius) {
    return sdSegment(p, start, end) - radius;
}

float forgeUnion(float a, float b) { return min(a, b); }
float forgeIntersection(float a, float b) { return max(a, b); }
float forgeDifference(float a, float b) { return max(a, -b); }

float forgeSmoothUnion(float a, float b, float softness) {
    float radius = max(softness, 1e-5);
    float mixFactor = clamp(0.5 + 0.5 * (b - a) / radius, 0.0, 1.0);
    return mix(b, a, mixFactor) - radius * mixFactor * (1.0 - mixFactor);
}

// Polar vectors use (radius, angle in radians).
vec2 forgePolar(vec2 p) {
    return vec2(length(p), dot(p, p) > 0.0 ? atan(p.y, p.x) : 0.0);
}

vec2 forgeCartesian(vec2 polar) {
    return polar.x * vec2(cos(polar.y), sin(polar.y));
}

// The shorter canvas side is one unit, so circles stay round at any aspect ratio.
vec2 forgeAspectUV(vec2 uv, vec2 center, vec2 dimensions) {
    return (uv - center) * dimensions / max(1.0, min(dimensions.x, dimensions.y));
}
