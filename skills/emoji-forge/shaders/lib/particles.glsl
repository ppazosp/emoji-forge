// Velocity is in position units per second. Age is in seconds when using seconds-based velocity.
vec2 forgeBallistic(vec2 origin, vec2 velocity, float age, float gravity) {
    return origin + velocity * age - vec2(0.0, 0.5 * gravity * age * age);
}

// Integer hash for stable variation from a particle index and a seed.
uint forgeHashUint(uint value) {
    value ^= value >> 16u;
    value *= 0x7feb352du;
    value ^= value >> 15u;
    value *= 0x846ca68bu;
    return value ^ (value >> 16u);
}

float forgeParticleRandom(uint index, uint seed) {
    return float(forgeHashUint(index ^ forgeHashUint(seed)) >> 8u) / 16777216.0;
}

vec2 forgeParticleVelocity(uint index, uint seed, vec2 speedRange) {
    float angle = TAU * forgeParticleRandom(index, seed);
    float speed = mix(speedRange.x, speedRange.y, forgeParticleRandom(index, seed + 1u));
    return forgeCartesian(vec2(speed, angle));
}
