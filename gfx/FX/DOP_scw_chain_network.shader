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
float4 main(VS_OUTPUT v) : PDX_COLOR
{
	float2 p = v.vTexCoord * 450.0f;
	// Continuous decorative time: deliberately independent of opening or game-date ticks.
	float cycle = frac(Time / 6.4f) * 6.4f;
	float alpha = 0.0f;
	float hot = 0.0f;
	for (int i = 0; i < 5; ++i)
	{
		float2 a = ChainStart(i);
		float2 b = ChainEnd(i);
		float2 d = b - a;
		float span = length(d);
		float along = dot(p - a, d / span);
		// Each station traces its frame first, then hands the packet to its outgoing link.
		float age = cycle - float(i) * 1.28f - 0.78f;
		float head = lerp(-12.0f, span + 24.0f, saturate(age / 0.40f));
		float tail = head - along;
		float packet = saturate(1.0f - tail / 34.0f)
			* smoothstep(-0.8f, 0.8f, tail)
			* smoothstep(0.0f, 0.03f, age) * (1.0f - smoothstep(0.40f, 0.47f, age));
		float track = ChainLine(p, a, b, 1.55f);
		float halo = ChainLine(p, a, b, 4.0f);
		float port = 1.0f - smoothstep(1.35f, 2.30f, min(length(p - a), length(p - b)));
		float ack = smoothstep(0.30f, 0.34f, age) * (1.0f - smoothstep(0.37f, 0.46f, age));
		float receive = (1.0f - smoothstep(1.2f, 3.6f, length(p - b))) * ack;
		float2 u = d / span;
		float2 side = float2(-u.y, u.x);
		float2 tip = lerp(a, b, 0.60f);
		float chevron = max(ChainLine(p, tip - u * 4.5f + side * 3.0f, tip, 0.65f),
			ChainLine(p, tip - u * 4.5f - side * 3.0f, tip, 0.65f));
		float signal = max(track * packet, receive);
		float part = max(track * (0.42f + packet * 0.54f) + halo * packet * 0.09f,
			max(chevron * 0.52f, max(port * 0.42f, receive * 0.95f)));
		alpha = max(alpha, part);
		hot = max(hot, signal);
	}
	float3 ink = lerp(float3(0.39f, 0.69f, 0.74f), float3(0.86f, 0.96f, 0.97f), saturate(hot));
	return float4(ink, saturate(alpha) * tex2D(MapTexture, float2(0.5f, 0.5f)).a) * Color;
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
