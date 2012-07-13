#version 330
//#include "common.glsl"

layout (location=0) in vec4 in_pos;
//layout (location=1) in vec2 in_uv;

uniform mat4 m;
uniform mat4 pv;

//out vec2 uv;

void main(){
	vec4 w_pos = m * in_pos;
	gl_Position = pv *  w_pos;
}
