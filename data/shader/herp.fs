#version 330
#include "common.glsl"

in vec2 uv;
out vec4 ocolor;

float rand(vec2 co){
	return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

void main(){
	vec3 texel = texture2D(texture0, uv).rgb;

	int x = int(uv.x * 300);
	float r = min(min(rand(vec2(float(x)/300, time)), 0.03) * 32 + 0.7, 1.0);

	float noise = 1.0f - clamp(rand(uv + vec2(time, time*2)) * 0.4, 0.0, 0.7);

	ocolor.rgb = texel * r * noise * fade;
	ocolor.a = 1.0f;
}
