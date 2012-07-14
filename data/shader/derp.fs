#version 330
#include "common.glsl"

in vec2 uv;
in vec4 w_pos;
out vec4 ocolor;

void main(){
	float distance = length(w_pos.xy - player_pos);

	float light = clamp(1.0f-distance/10.0f, 0.0f, 1.0f);
	float dark = light * (hp*1.7) *
		(1.0-clamp(sin(time*25.0f), 0.1, 0.6)) *
		clamp(((sin(time*2.5f + time*6.5f) + 1.0) * 0.5), 0.2, 0.6);

	float m = mix(dark, light, hp);
	vec4 texel = texture2D(texture0, uv);
	ocolor =  vec4(texel.rgb * m, texel.a);
}
