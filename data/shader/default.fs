#version 330
#include "common.glsl"

in vec2 uv;
out vec4 ocolor;

void main(){
	ocolor = texture2D(texture0, uv);
	ocolor.a = 1.0f;
}
