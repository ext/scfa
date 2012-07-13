#version 330
#include "common.glsl"

in vec2 uv;
out vec4 ocolor;

void main(){
	//ocolor = texture2D(texture0, uv);
  ocolor = vec4(uv,0,1);
}

