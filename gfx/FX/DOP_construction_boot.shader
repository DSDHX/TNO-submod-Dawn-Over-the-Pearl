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
 float4 now=tex2D(MapTexture,Offset+float2(.015625f,.5f));
 if(now.r>=.999f)return float4(0,0,0,0);
 float4 next=tex2D(MapTexture,NextOffset+float2(.015625f,.5f));
 float phase=saturate(lerp(now.r,next.r,saturate(AnimationTime)));
 if(phase>=.999f)return float4(0,0,0,0);
 float uScale=(636.0f/1056.0f)*abs(ddy(v.vTexCoord.y))/max(abs(ddx(v.vTexCoord.x)),.0000001f);
 float2 p=float2(frac(v.vTexCoord.x*uScale),v.vTexCoord.y)*float2(1056,636);
 float3 surface=float3(.041f,.067f,.090f);
 float3 color=surface;

 float progress=smoothstep(.02f,.82f,phase);
 float curtain=1.0f-smoothstep(.85f,.995f,phase);
 float track=B(p,float2(528,318),float2(270,4.5f))-B(p,float2(528,318),float2(268,2.5f));
 float fill=B(p,float2(258+270*progress,318),float2(270*progress,1.6f))*step(.0001f,progress);
 float caps=max(B(p,float2(252,318),float2(.7f,8)),B(p,float2(804,318),float2(.7f,8)));
 color+=float3(.69f,.75f,.79f)*(track*.32f+fill*.8f+caps*.3f);
 float alpha=curtain;

 return float4(saturate(color),saturate(alpha))*Color;
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

