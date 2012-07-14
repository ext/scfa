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

	float d2 = length(w_pos.xy - house_pos);
	float l2 = clamp(1.0f-d2/12.0f, 0.0f, 1.0f);

	float d3 = length(w_pos.xy - vec2(354,-18));
	float l3 = clamp(1.0f-d3/12.0f, 0.0f, 1.0f);

	float d4 = length(w_pos.xy - vec2(200,-48));
	float l4 = clamp(1.0f-d4/20.0f, 0.0f, 1.0f) * clamp((sin(time*3.2) + 1.3)*0.5, 0.5, 1.2);

	float d5 = length(w_pos.xy - vec2(384,-87));
	float l5 = clamp(1.0f-d5/20.0f, 0.0f, 1.0f);

	float m = mix(dark, light, hp);
	vec4 texel = texture2D(texture0, uv);
	ocolor =  vec4(texel.rgb * m +
	               vec3(texel.r*l2, texel.gb*l2*0.7) +
	               vec3(texel.r*l3, texel.g*l3*0.6, texel.b*l3*0.4) +
	               vec3(texel.r*l4*1.6, texel.g*l4*0.4, texel.b*l4*0.3) +
	               vec3(texel.r*l5*1.6, texel.g*l5*0.4, texel.b*l5*0.3)
	               , texel.a);
}
