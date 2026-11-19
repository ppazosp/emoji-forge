// Shared straight-alpha compositing and procedural primitives.
const float TAU = 6.28318530718;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1, 0)), u.x),
               mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), u.x), u.y);
}

float fbm(vec2 p) {
    float accum = 0.0, gain = 0.5;
    for (int i = 0; i < 5; i++) {
        accum += gain * noise(p);
        p = mat2(1.6, 1.2, -1.2, 1.6) * p + 5.0;
        gain *= 0.5;
    }
    return accum;
}

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

float envelope(float start, float peak, float release, float end) {
    return intensity * smoothstep(start, peak, phase) * (1.0 - smoothstep(release, end, phase));
}

float edgeFade(vec2 p) {
    vec2 margin = min(p, 1.0 - p);
    return smoothstep(0.008, 0.07, min(margin.x, margin.y));
}

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

// Looping time, geometry and layered effects. All distances use normalized UVs.
float forgeEase(float t) {
    t = clamp(t, 0.0, 1.0);
    return t * t * (3.0 - 2.0 * t);
}

float forgeLoopAngle(float cycles, float framePhase) {
    return TAU * cycles * framePhase;
}

vec2 forgeRotate(vec2 p, float angle) {
    float c = cos(angle), s = sin(angle);
    return vec2(c * p.x - s * p.y, s * p.x + c * p.y);
}

vec2 forgeHash2(vec2 seed) {
    return vec2(hash(seed), hash(seed + vec2(17.3, 8.7)));
}

float forgeLoopNoise(vec2 p, float framePhase, float travel) {
    float angle = forgeLoopAngle(1.0, framePhase);
    return fbm(p + travel * vec2(cos(angle), sin(angle)));
}

float forgePulse(float framePhase, float start, float peak, float end) {
    return smoothstep(start, peak, framePhase) * (1.0 - smoothstep(peak, end, framePhase));
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

vec3 forgePalette(float amount, vec3 low, vec3 middle, vec3 high) {
    return mix(mix(low, middle, smoothstep(0.0, 0.55, amount)), high,
               smoothstep(0.55, 1.0, amount));
}

vec2 forgeBallistic(vec2 origin, vec2 velocity, float age, float gravity) {
    return origin + velocity * age - vec2(0.0, 0.5 * gravity * age * age);
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

vec2 forgeView(vec2 uv, vec2 center, vec2 translation, float zoom) {
    return center + (uv - center - translation) / max(0.1, zoom);
}

vec2 forgeShakeOffset(float framePhase, float strength) {
    return vec2(sin(framePhase * 79.0), cos(framePhase * 116.0)) * strength;
}

vec2 forgeShake(float framePhase, float amplitude) {
    return forgeShakeOffset(framePhase, forgePulse(framePhase, 0.19, 0.36, 0.67) * amplitude);
}
