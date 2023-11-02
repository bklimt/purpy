#version 130

uniform float iTime;
uniform vec2 iResolution;
uniform vec2 iOffset;
uniform sampler2D u_texture;
uniform sampler2D iStatic;

uniform bool iSpotlightEnabled;
uniform vec2 iSpotlightPosition;
uniform float iSpotlightRadius;

vec2 tube_warp(vec2 coord, vec2 offset) {
    coord = (coord * 2.0) - 1.0;
    coord *= 0.5;

    coord.x *= (1.0 + pow(coord.y / 2.5, 2.0));
    coord.y *= (1.0 + pow(coord.x / 2.5, 2.0));

    coord += offset;
    coord += 0.5;
    return coord;
}

vec4 scanline(float y) {
    y *= iResolution.y;
    y += (iTime * 5.0);
    y /= 1.2;
    float scanline_mag = sin(y);
    vec3 scanline_color = vec3(scanline_mag, scanline_mag, scanline_mag);
    return vec4(scanline_color, 1.0);
}

vec4 spotlight(vec2 position) {
    if (!iSpotlightEnabled) {
        return vec4(1.0, 1.0, 1.0, 0.0);
    }
    position.y = 1.0 - position.y;
    position *= textureSize(u_texture, 0);
    float d = distance(iSpotlightPosition, position);
    // float a = 1.0 - clamp(d / iSpotlightRadius, 0.0, 1.0);
    float a = smoothstep(0.0, 1.0, d / iSpotlightRadius) * 0.85;
    return vec4(0.0, 0.0, 0.0, a);
}

void main() {
    vec2 uv = ((gl_FragCoord.xy - iOffset) / iResolution);
    vec2 uv1 = tube_warp(uv, vec2(0.0, 0.0));
    vec2 uv2 = tube_warp(uv, vec2(0.002, 0.0));
    vec2 uv3 = tube_warp(uv, vec2(-0.002, 0.0));

    if (uv1.x < 0.0 || uv1.y < 0.0 || uv1.x > 1.0 || uv1.y > 1.0) {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    vec4 scan = scanline(uv1.y);

    vec2 random_pos = uv1;
    random_pos.y += iTime * 10.0;
    vec4 random = texture2D(iStatic, random_pos);

    vec4 color;
    color.r = texture2D(u_texture, uv2).r;
    color.g = texture2D(u_texture, uv1).g;
    color.b = texture2D(u_texture, uv3).b;
    color.a = 1.0;

    vec4 spot = spotlight(uv1);
    color = vec4(mix(color.rgb, spot.rgb, spot.a), 1.0);

    color = mix(mix(color, random, 0.04), scan, 0.01);

    gl_FragColor = color;
}
