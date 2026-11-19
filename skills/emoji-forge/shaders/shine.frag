vec4 effect(vec2 uv, vec4 art) {
    float center = mix(-.7, 1.8, forgeEase(phase));
    float distanceToBand = uv.x + uv.y * .48 - center;
    float band = halo(distanceToBand,.14);
    float trail = halo(distanceToBand + .18,.037) * .47;
    return vec4(art.rgb + vec3(.80,.69,.45) * max(band,trail) * intensity, art.a);
}
