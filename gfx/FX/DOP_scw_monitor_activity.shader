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
		float BoxMask(float2 p, float2 center, float2 halfSize)
		{
			float2 d = abs(p - center) - halfSize;
			return 1.0f - smoothstep(-0.40f, 0.65f, max(d.x, d.y));
		}
		float4 main(VS_OUTPUT v) : PDX_COLOR
		{
			// Only two small clusters at the ends of a 392 x 18 px footer animate.
			float2 px = v.vTexCoord * float2(392.0f, 18.0f);
			float carrier = tex2D(MapTexture, v.vTexCoord).a;
			float pulse = 0.5f + 0.5f * sin(Time * 2.6179939f);
			float ledDistance = length(px - float2(6.0f, 9.0f));
			float led = 1.0f - smoothstep(2.0f, 3.0f, ledDistance);
			float halo = (1.0f - smoothstep(3.0f, 5.0f, ledDistance)) * 0.08f;
			float signalAlpha = 0.0f;
			// Smooth interpolated bar heights, never random frame changes.
			for (int i = 0; i < 8; ++i)
			{
				float n = float(i);
				float wave = 0.5f + 0.5f * sin(Time * (2.1f + 0.13f * n) + n * 0.91f);
				float height = 3.0f + 10.0f * wave;
				float bar = BoxMask(px, float2(336.0f + n * 6.0f, 15.0f - height * 0.5f),
					float2(1.65f, height * 0.5f));
				signalAlpha = max(signalAlpha, bar * (0.54f + wave * 0.23f));
			}
			float baseline = BoxMask(px, float2(357.0f, 16.5f), float2(24.0f, 0.35f)) * 0.22f;
			float alpha = max(led * (0.40f + pulse * 0.40f) + halo, max(signalAlpha, baseline));
			float3 ink = float3(0.40f, 0.78f, 0.82f);
			// Straight-alpha RGB is deliberately not multiplied by alpha a second time.
			return float4(ink, saturate(alpha * carrier)) * Color;
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
