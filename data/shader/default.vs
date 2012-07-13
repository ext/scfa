#version 330
#include "common.glsl"

layout (location=0) in vec4 in_pos;
layout (location=1) in vec2 in_uv;

out vec2 uv;

void main(){
	uv = in_uv;
	vec4 w_pos = modelMatrix * in_pos;
	gl_Position = projectionViewMatrix *  w_pos;
}
