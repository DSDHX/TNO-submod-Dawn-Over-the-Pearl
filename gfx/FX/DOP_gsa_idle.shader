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

float4 main(VS_OUTPUT v):PDX_COLOR{
 float2 p=v.vTexCoord*float2(420,168);
 float2 q=p-float2(73,80);
 float ellipse=0.0f;
 for(int i=0;i<3;++i){
  float a=float(i)*1.04719755f;float ca=cos(a);float sa=sin(a);
  float2 z=float2(q.x*ca-q.y*sa,q.x*sa+q.y*ca)/float2(37,14);
  ellipse=max(ellipse,1.0f-smoothstep(0.045f,0.10f,abs(length(z)-1.0f)));
 }
 float nucleus=(1.0f-smoothstep(3.0f,4.2f,length(q)))*(0.55f+0.07f*sin(Time*1.1f));
 float grid=(1.0f-smoothstep(0.0f,0.8f,min(abs(frac(p.x/24)*24-12),abs(frac(p.y/24)*24-12))))*0.018f;
 float3 rgb=float3(0.032f,0.057f,0.079f)+grid;
 rgb=lerp(rgb,float3(0.53f,0.73f,0.77f),max(ellipse*0.56f,nucleus));
 return float4(rgb,tex2D(MapTexture,float2(.5f,.5f)).a)*Color;
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

