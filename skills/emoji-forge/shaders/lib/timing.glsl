// Normalized easing. Compose with forgeRange to place a movement on the timeline.
float forgeRange(float t, float start, float end) {
    return clamp((t - start) / max(end - start, 1e-5), 0.0, 1.0);
}

float forgeEaseIn(float t) {
    t = clamp(t, 0.0, 1.0);
    return t * t * t;
}

float forgeEaseOut(float t) {
    return 1.0 - forgeEaseIn(1.0 - t);
}

float forgeSineEase(float t) {
    return 0.5 - 0.5 * cos(0.5 * TAU * clamp(t, 0.0, 1.0));
}

// Repeating fractional age with an offset per particle or layer.
float forgeLoopAge(float t, float cycles, float offset) {
    return fract(t * cycles + offset);
}
