#version 330
#include "common.glsl"

in vec2 uv;
in float distance;
out vec4 ocolor;

void main(){
	float light = clamp(1.0f-distance/10.0f, 0.0f, 1.0f) *
		(1.5-clamp(sin(time*25.0f), 0.6, 1.0)) *
		clamp(((sin(time*2.5f + time*6.5f) + 1.0) * 0.5), 0.7, 1.0);
	vec4 texel = texture2D(texture0, uv);
	ocolor =  vec4(texel.rgb * light, texel.a);
}
