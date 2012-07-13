#version 120
#extension GL_ARB_explicit_attrib_location : enable

//#include "common.glsl"

in vec4 in_pos;
//layout (location=1) in vec2 in_uv;

//out vec2 uv;

uniform mat4 pv;

void main(){
     gl_Position = pv * in_pos;
//	uv = in_uv;
//	vec4 w_pos = modelMatrix * in_pos;
//	gl_Position = projectionViewMatrix *  w_pos;
}
