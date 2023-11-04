#version 120

// Screen Info
uniform float iTime;
uniform vec2 iResolution;
uniform vec2 iOffset;
uniform vec2 iTextureSize;

// Textures
uniform sampler2D iStaticTexture;
uniform sampler2D iPlayerTexture;
uniform sampler2D iHudTexture;

// Lighting
uniform int iSpotlightCount;
uniform vec2 iSpotlightPosition[20];
uniform float iSpotlightRadius[20];

// This is like, halfway between GL_LINEAR and GL_NEAREST.
// It requires the texture be sampled with GL_LINEAR.
vec2 fuzz_sample_uv(vec2 coord) {
    coord *= iTextureSize;
    coord += 0.5;

    vec2 coordFloor = floor(coord) + 0.5;
    vec2 coordFract = fract(coord);

    coordFract = smoothstep(-0.5, 0.5, coordFract - 0.5);
    // coordFract = vec2(0.0, 0.0);

    coord = coordFloor + coordFract;
    coord /= iTextureSize;
    return coord;
}

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
    y /= 1.5;
    float scanline_mag = sin(y);
    vec3 scanline_color = vec3(scanline_mag, scanline_mag, scanline_mag);
    return vec4(scanline_color, 1.0);
}

vec4 spotlight(vec2 position) {
    if (iSpotlightCount == 0) {
        return vec4(1.0, 1.0, 1.0, 0.0);
    }
    position.y = 1.0 - position.y;
    position *= iTextureSize;

    float alpha = 1.0;
    int i;
    for (i = 0; i < iSpotlightCount; ++i) {
        float d = distance(iSpotlightPosition[i], position);
        float a = smoothstep(0.0, 1.0, d / iSpotlightRadius[i]) * 0.85;
        alpha = min(alpha, a);
    }

    return vec4(0.0, 0.0, 0.0, alpha);
}

// Like texture2D, but fuzzes partway between linear and nearest.
vec4 sample_texture(sampler2D texture, vec2 uv) {
    return texture2D(texture, fuzz_sample_uv(uv));
}

vec4 get_scene_pixel(vec2 uv) {
    vec4 spot = spotlight(uv);

    vec4 player_color = sample_texture(iPlayerTexture, uv);
    player_color = vec4(mix(player_color.rgb, spot.rgb, spot.a), 1.0);

    vec4 hud_color = sample_texture(iHudTexture, uv);
    vec4 color = vec4(mix(hud_color.rgb, player_color.rgb, 1.0 - hud_color.a), 1.0);

    return color;
}

vec4 frame(vec2 uv) {
    uv -= 0.5;

    // Make a squircle glossy screen.
    float sqr = pow(uv.x, 4.0) + pow(uv.y, 4.0);
    if (sqr < 0.02) {
        vec3 white = vec3(1.0, 1.0, 1.0);
        vec3 beige = vec3(0.99, 0.85, 0.70);
        float sqr2 = pow(uv.x, 4.0) + pow((uv.y - 0.5), 4.0);
        if (sqr2 < 0.09) {
            return vec4(mix(beige, white, sqr2*2.0), 0.1);
        } else {
            return vec4(beige, 0.1);
        }
    } else {
        // Make a frame.
        float corner = smoothstep(0.7, 1.0, 0.85 - abs(abs(uv.x)-abs(uv.y)));
        corner = corner * corner;

        vec3 shiny = vec3(1.0, 1.0, 1.0);
        // vec3 color = vec3(0.23, 0.28, 0.23);
        vec3 color = vec3(0.12, 0.14, 0.12);
        vec3 result = mix(color, shiny, corner);

        return vec4(result, 1.0);
    }
}

vec4 gamescreen(vec2 uv) {
    // Shrink the screen slightly.
    uv *= 1.05;
    uv -= 0.025;

    vec2 uv1 = tube_warp(uv, vec2(0.0, 0.0));
    vec2 uv2 = tube_warp(uv, vec2(0.002, 0.0));
    vec2 uv3 = tube_warp(uv, vec2(-0.002, 0.0));

    // Fade in the very edges.
    float min_edge = min(uv1.x, min(uv1.y, min(1.0 - uv1.x, 1.0 - uv1.y)));
    if (min_edge < 0.0) {
        return vec4(0.0, 0.0, 0.0, 0.0);
    }
    float alpha = smoothstep(0.0, 1.0, min_edge * 150.0);

    vec4 scan = scanline(uv1.y);

    vec2 random_pos = uv1;
    random_pos.y += iTime * 10.0;
    vec4 random = texture2D(iStaticTexture, random_pos);

    vec4 color1 = get_scene_pixel(uv1);
    vec4 color2 = get_scene_pixel(uv2);
    vec4 color3 = get_scene_pixel(uv3);
    vec4 color = vec4(color2.r, color1.g, color3.b, 1.0);

    return vec4(mix(mix(color, random, 0.04), scan, 0.015).rgb, alpha);
}

void main() {
    vec2 uv = ((gl_FragCoord.xy - iOffset) / iResolution);

    vec4 frame_color = frame(uv);
    vec4 game_color = gamescreen(uv);

    gl_FragColor = vec4(mix(frame_color.rgb, game_color.rgb, game_color.a), 1.0);
}
