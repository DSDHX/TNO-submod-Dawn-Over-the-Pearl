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
 float2 p=v.vTexCoord*float2(420,16);
 float y=8.0f+3.0f*sin(p.x*0.052f)+1.0f*sin(p.x*0.141f);
 float trace=1.0f-smoothstep(0.50f,1.20f,abs(p.y-y));
 float head=frac(Time/4.2f)*420.0f;
 float behind=head-p.x;
 float tail=saturate(1.0f-behind/100.0f)*step(0.0f,behind);
 float dotMask=1.0f-smoothstep(1.3f,3.0f,length(float2(p.x-head,p.y-y)));
 float glow=max(trace*(0.20f+tail*0.70f),dotMask);
 float3 color=lerp(float3(0.025f,0.043f,0.062f),float3(0.64f,0.89f,0.92f),glow);
 return float4(color,0.87f*tex2D(MapTexture,float2(.5f,.5f)).a)*Color;
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

