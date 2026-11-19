// Value noise, domain warping and continuous-loop noise.
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

vec2 forgeHash2(vec2 seed) {
    return vec2(hash(seed), hash(seed + vec2(17.3, 8.7)));
}

float forgeLoopNoise(vec2 p, float framePhase, float travel) {
    float angle = forgeLoopAngle(1.0, framePhase);
    return fbm(p + travel * vec2(cos(angle), sin(angle)));
}

// Position uses noise-cell units. Gradient and simplex noise are signed.
vec2 forgeNoiseGradient(vec2 cell) {
    float angle = TAU * hash(cell);
    return vec2(cos(angle), sin(angle));
}

float forgeGradientNoise(vec2 p) {
    vec2 cell = floor(p);
    vec2 f = fract(p);
    vec2 blend = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
    float a = dot(forgeNoiseGradient(cell), f);
    float b = dot(forgeNoiseGradient(cell + vec2(1.0, 0.0)), f - vec2(1.0, 0.0));
    float c = dot(forgeNoiseGradient(cell + vec2(0.0, 1.0)), f - vec2(0.0, 1.0));
    float d = dot(forgeNoiseGradient(cell + 1.0), f - 1.0);
    return mix(mix(a, b, blend.x), mix(c, d, blend.x), blend.y);
}

float forgeSimplexCorner(vec2 cell, vec2 offset) {
    float influence = max(0.5 - dot(offset, offset), 0.0);
    influence *= influence;
    return influence * influence * dot(forgeNoiseGradient(cell), offset);
}

float forgeSimplexNoise(vec2 p) {
    const float skew = 0.3660254038;
    const float unskew = 0.2113248654;
    vec2 cell = floor(p + (p.x + p.y) * skew);
    vec2 first = p - cell + (cell.x + cell.y) * unskew;
    vec2 corner = first.x > first.y ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
    vec2 second = first - corner + unskew;
    vec2 third = first - 1.0 + 2.0 * unskew;
    return 70.0 * (forgeSimplexCorner(cell, first)
        + forgeSimplexCorner(cell + corner, second)
        + forgeSimplexCorner(cell + 1.0, third));
}

// Distances to the first and second nearest feature points.
vec2 forgeWorley(vec2 p) {
    vec2 cell = floor(p);
    vec2 nearest = vec2(1e6);
    for (int y = -2; y <= 2; y++) {
        for (int x = -2; x <= 2; x++) {
            vec2 neighbor = cell + vec2(float(x), float(y));
            vec2 offset = neighbor + forgeHash2(neighbor) - p;
            float squared = dot(offset, offset);
            nearest.y = min(nearest.y, max(nearest.x, squared));
            nearest.x = min(nearest.x, squared);
        }
    }
    return sqrt(nearest);
}

// Rotating the gradient of a scalar field produces flow without a source or sink.
vec2 forgeCurlNoise(vec2 p) {
    const float delta = 0.015;
    vec2 dx = vec2(delta, 0.0), dy = vec2(0.0, delta);
    float x = forgeSimplexNoise(p + dx) - forgeSimplexNoise(p - dx);
    float y = forgeSimplexNoise(p + dy) - forgeSimplexNoise(p - dy);
    return vec2(y, -x) / (2.0 * delta);
}

vec2 forgeDomainWarp(vec2 p, float strength) {
    vec2 offset = vec2(fbm(p), fbm(p + vec2(19.3, 42.7))) - 0.5;
    return p + strength * offset;
}
