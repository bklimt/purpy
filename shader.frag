
uniform vec2 iResolution;
uniform vec2 iOffset;
uniform sampler2D u_texture;

vec2 tube_warp(vec2 coord) {
    coord = (coord * 2.0) - 1.0;
    coord *= 0.5;

    coord.x *= (1.0 + pow(abs(coord.y) / 2.5, 2.0));
    coord.y *= (1.0 + pow(abs(coord.x) / 2.5, 2.0));

    coord += 0.5;
    return coord;
}

void main() {
    if (gl_FragCoord.x < iOffset.x || gl_FragCoord.y < iOffset.y) {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    vec2 uv = ((gl_FragCoord.xy - iOffset) / iResolution);
    uv = tube_warp(uv);

    if (uv.x < 0.0 || uv.y < 0.0 || uv.x > 1.0 || uv.y > 1.0) {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    vec4 color = texture2D(u_texture, uv);
    gl_FragColor = color;
}
