// Shape primitives and transforms in normalized UV space.
float sdCircle(vec2 p, float radius) {
    return length(p) - radius;
}

float sdSegment(vec2 p, vec2 a, vec2 b) {
    vec2 segment = b - a;
    float t = clamp(dot(p - a, segment) / max(dot(segment, segment), 1e-6), 0.0, 1.0);
    return length(p - a - t * segment);
}

float halo(float distanceToEdge, float width) {
    return 1.0 - smoothstep(0.0, width, abs(distanceToEdge));
}

float edgeFade(vec2 p) {
    vec2 margin = min(p, 1.0 - p);
    return smoothstep(0.008, 0.07, min(margin.x, margin.y));
}

vec2 forgeRotate(vec2 p, float angle) {
    float c = cos(angle), s = sin(angle);
    return vec2(c * p.x - s * p.y, s * p.x + c * p.y);
}

float forgeBox(vec2 p, vec2 halfSize) {
    vec2 q = abs(p) - halfSize;
    return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0);
}

float forgeEllipse(vec2 p, vec2 radii) {
    return (length(p / radii) - 1.0) * min(radii.x, radii.y);
}

float forgeFill(float distanceToShape, float softEdge) {
    return 1.0 - smoothstep(-softEdge, softEdge, distanceToShape);
}

float forgeRing(vec2 p, float radius, float width) {
    return halo(sdCircle(p, radius), width);
}

float forgeGlint(vec2 p, float span, float width) {
    float arms = min(sdSegment(p, vec2(-span, 0.0), vec2(span, 0.0)),
                     sdSegment(p, vec2(0.0, -span), vec2(0.0, span)));
    return halo(arms, width) * (1.0 - smoothstep(span * 0.35, span + width, length(p)));
}

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
