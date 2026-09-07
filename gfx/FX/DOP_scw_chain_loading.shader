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


float2 ChainNode(int i)
{
	if (i == 0) return float2(221.0f, 63.0f);
	if (i == 1) return float2(71.0f, 213.0f);
	if (i == 2) return float2(220.0f, 363.0f);
	if (i == 3) return float2(371.0f, 213.0f);
	return float2(370.0f, 63.0f);
}
float2 ChainStart(int i)
{
	if (i == 0) return float2(166.0f, 118.0f);
	if (i == 1) return float2(126.0f, 268.0f);
	if (i == 2) return float2(275.0f, 308.0f);
	if (i == 3) return float2(371.0f, 158.0f);
	return float2(333.0f, 63.0f);
}
float2 ChainEnd(int i)
{
	if (i == 0) return float2(126.0f, 158.0f);
	if (i == 1) return float2(165.0f, 308.0f);
	if (i == 2) return float2(316.0f, 268.0f);
	if (i == 3) return float2(370.0f, 100.0f);
	return float2(276.0f, 63.0f);
}
float ChainLine(float2 p, float2 a, float2 b, float width)
{
	float t = saturate(dot(p - a, b - a) / max(dot(b - a, b - a), 0.001f));
	return 1.0f - smoothstep(width - 0.45f, width + 0.55f, length(p - lerp(a, b, t)));
}
float2 ChainBoot(float2 p, float phase)
{
	float mask = 0.0f;
	float light = 0.0f;
	for (int i = 0; i < 5; ++i)
	{
		float n = float(i);
		float2 center = ChainNode(i);
		// Include the independent moving brackets, not only the 102px photograph.
		float node = WindowBox(p, center, float2(64.5f, 64.5f));
		float reveal = smoothstep(0.545f + n * 0.075f, 0.645f + n * 0.075f, phase);
		float scan = p.y - center.y + 64.5f - reveal * 129.0f;
		float hidden = reveal < 0.0001f ? 1.0f : smoothstep(-0.75f, 0.75f, scan);
		if (reveal >= 0.9999f) hidden = 0.0f;
		mask = max(mask, node * hidden);
		if (reveal > 0.001f && reveal < 0.999f)
			light = max(light, node * (1.0f - smoothstep(0.3f, 1.5f, abs(scan))) * 0.65f);
		float2 a = ChainStart(i);
		float2 b = ChainEnd(i);
		float along = saturate(dot(p - a, b - a) / dot(b - a, b - a));
		float linkReveal = smoothstep(0.605f + n * 0.073f, 0.685f + n * 0.073f, phase);
		float linkHidden = linkReveal < 0.0001f ? 1.0f : smoothstep(-0.025f, 0.025f, along - linkReveal);
		if (linkReveal >= 0.9999f) linkHidden = 0.0f;
		mask = max(mask, ChainLine(p, a, b, 5.5f) * linkHidden);
	}
	return float2(mask, light);
}

		float4 main(VS_OUTPUT v) : PDX_COLOR
		{
			// Read each frame at its centre: R is playback phase, G selects the page.
			// Native non-looping playback is used only for the first-show sequence.
			// Reopening the native parent is not a supported replay trigger here.
			float4 now = tex2D(MapTexture, Offset + float2(0.015625f, 0.5f));
			// Remain invisible even if the engine leaves NextOffset wrapped at the final frame.
			if (now.r >= 0.999f)
				return float4(0.0f, 0.0f, 0.0f, 0.0f);
			float4 next = tex2D(MapTexture, NextOffset + float2(0.015625f, 0.5f));
			float4 clock = lerp(now, next, saturate(AnimationTime));
			float phase = saturate(clock.r);
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
			// The chain boot uses the same native frame clock as the curtain, never a show timestamp.
			// Native BoP (25,19) + network (30,150) - curtain (18,22) = (37,147).
			float2 boot = ChainBoot(px - float2(37.0f, 147.0f), phase);
			color = lerp(color, surface, boot.x * (1.0f - curtain));
			color = lerp(color, float3(0.76f, 0.92f, 0.94f), boot.y * (1.0f - curtain));
			alpha = max(alpha, max(boot.x, boot.y));
			return float4(saturate(color), saturate(alpha)) * Color;
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
