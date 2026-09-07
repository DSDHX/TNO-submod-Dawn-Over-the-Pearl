Includes = { "buttonstate.fxh" }
PixelShader = {
	Samplers = {
		MapTexture = {
			Index = 0
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "None"
			AddressU = "Clamp"
			AddressV = "Clamp"
		}
	}
}
VertexStruct VS_OUTPUT
{
	float4 vPosition : PDX_POSITION;
	float2 vTexCoord : TEXCOORD0;
};
VertexShader = {
	MainCode VertexShader
	[[
		VS_OUTPUT main(const VS_INPUT v)
		{
			VS_OUTPUT Out;
			Out.vPosition = mul(WorldViewProjectionMatrix, float4(v.vPosition.xyz, 1));
			Out.vTexCoord = v.vTexCoord;
			return Out;
		}
	]]
}
PixelShader = {
	MainCode PixelShaderMonitor
	[[

float B(float2 p,float2 c,float2 h){float2 d=abs(p-c)-h;return 1.0f-smoothstep(-0.4f,0.6f,max(d.x,d.y));}
float4 main(VS_OUTPUT v):PDX_COLOR{
 float2 p=v.vTexCoord*float2(448.0f,504.0f);
 float3 color=float3(0.047f,0.078f,0.106f);
 float border=B(p,float2(224,252),float2(223.5f,251.5f))-B(p,float2(224,252),float2(222.4f,250.4f));
 float header=B(p,float2(224,26),float2(222,25));
 color+=float3(0.019f,0.026f,0.031f)*header;
 float rules=max(B(p,float2(224,52),float2(209,0.45f)),B(p,float2(224,360),float2(209,0.45f)));
 float photo=B(p,float2(224,153),float2(211,85))-B(p,float2(224,153),float2(210,84));
 float meter=B(p,float2(224,283),float2(211,8))-B(p,float2(224,283),float2(210,6));
 float dividers=max(B(p,float2(117,328),float2(0.4f,23)),max(B(p,float2(224,328),float2(0.4f,23)),B(p,float2(331,328),float2(0.4f,23))));
 float etching=max(max(border*0.60f,photo*0.40f),max(max(rules*0.28f,meter*0.35f),dividers*0.22f));
 color=lerp(color,float3(0.63f,0.78f,0.82f),etching);
 return float4(color,tex2D(MapTexture,float2(0.5f,0.5f)).a)*Color;
}
	]]
}
BlendState BlendState
{
	BlendEnable = yes
	SourceBlend = "SRC_ALPHA"
	DestBlend = "INV_SRC_ALPHA"
}
Effect Up
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderMonitor"
}
Effect Down
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderMonitor"
}
Effect Disable
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderMonitor"
}
Effect Over
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderMonitor"
}
