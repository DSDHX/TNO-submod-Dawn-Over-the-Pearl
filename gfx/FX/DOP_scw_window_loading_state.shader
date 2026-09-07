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
		float WindowBox(float2 p, float2 center, float2 halfSize)
		{
			float2 q = abs(p - center) - halfSize;
			return 1.0f - smoothstep(-0.45f, 0.65f, max(q.x, q.y));
		}

		float4 main(VS_OUTPUT v) : PDX_COLOR
		{
			// Regular sprites supply the last state-change timestamp in AnimationTime.
			// No terminal frame or retained frame-player completion flag is involved.
			float age = max(0.0f, Time - AnimationTime);
			float phase = saturate(age / 2.6f);
			if (phase >= 0.999f)
				return float4(0.0f, 0.0f, 0.0f, 0.0f);

			// Derivative ratio handles both frame-local and atlas-width U conventions.
			float uScale = (636.0f / 1056.0f) * abs(ddy(v.vTexCoord.y))
				/ max(abs(ddx(v.vTexCoord.x)), 0.0000001f);
			float2 uv = float2(frac(v.vTexCoord.x * uScale), v.vTexCoord.y);
			float2 px = uv * float2(1056.0f, 636.0f);
			float progress = smoothstep(0.02f, 0.40f, phase);
			float curtain = 1.0f - smoothstep(0.44f, 0.54f, phase);
			float barLife = 1.0f - smoothstep(0.42f, 0.47f, phase);
			float3 ink = float3(0.50f, 0.82f, 0.85f);
			float3 surface = float3(0.044f, 0.068f, 0.088f);
			float3 color = surface;
			float alpha = curtain;

			// One centred progress bar on an opaque screen, with small end caps.
			float track = WindowBox(px, float2(528.0f, 318.0f), float2(270.0f, 10.0f));
			float hollow = WindowBox(px, float2(528.0f, 318.0f), float2(267.0f, 7.0f));
			float outline = saturate(track - hollow);
			float cells = 0.0f;
			float cellIndex = floor((px.x - 261.33333f) / 13.333333f);
			if (cellIndex >= 0.0f && cellIndex < 40.0f)
			{
				float n = cellIndex;
				float lit = saturate(progress * 40.0f - n);
				float cell = WindowBox(px, float2(268.0f + n * 13.333333f, 318.0f),
					float2(4.45f, 3.5f));
				cells = max(cells, cell * (0.09f + lit * 0.78f));
			}
			float endCaps = max(
				WindowBox(px, float2(246.0f, 318.0f), float2(0.65f, 15.0f)),
				WindowBox(px, float2(810.0f, 318.0f), float2(0.65f, 15.0f))
			);
			color += ink * (outline * 0.38f + cells + endCaps * 0.38f) * barLife;
			float carrierAlpha = tex2D(MapTexture, float2(0.5f, 0.5f)).a;
			return float4(saturate(color), saturate(alpha * carrierAlpha)) * Color;
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
