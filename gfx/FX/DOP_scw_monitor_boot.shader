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
	float2 vTexCoordNext : TEXCOORD1;
};
VertexShader = {
	MainCode VertexShader
	[[
		VS_OUTPUT main(const VS_INPUT v)
		{
			VS_OUTPUT Out;
			Out.vPosition = mul(WorldViewProjectionMatrix, float4(v.vPosition.xyz, 1));
			// Same Offset / NextOffset mechanism as buttonstate_blendframes.
			Out.vTexCoord = v.vTexCoord + Offset;
			Out.vTexCoordNext = v.vTexCoord + NextOffset;
			return Out;
		}
	]]
}
PixelShader = {
	MainCode PixelShaderMonitor
	[[
		float4 main(VS_OUTPUT v) : PDX_COLOR
		{
			return lerp(tex2D(MapTexture, v.vTexCoord),
				tex2D(MapTexture, v.vTexCoordNext), saturate(AnimationTime)) * Color;
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
