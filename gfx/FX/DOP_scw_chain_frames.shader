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

float2 FrameNode(int i)
{
	if (i == 0) return float2(221.0f, 63.0f);
	if (i == 1) return float2(71.0f, 213.0f);
	if (i == 2) return float2(220.0f, 363.0f);
	if (i == 3) return float2(371.0f, 213.0f);
	return float2(370.0f, 63.0f);
}
float FrameBox(float2 q, float2 center, float2 halfSize)
{
	float2 d = abs(q - center) - halfSize;
	return 1.0f - smoothstep(-0.35f, 0.65f, max(d.x, d.y));
}
float FrameArc(float2 q, float h)
{
	q = clamp(q, -h, h);
	if (abs(q.x) > abs(q.y))
	{
		if (q.x > 0.0f) return 0.25f + (q.y + h) / (8.0f * h);
		return 0.75f + (h - q.y) / (8.0f * h);
	}
	if (q.y < 0.0f) return (q.x + h) / (8.0f * h);
	return 0.50f + (h - q.x) / (8.0f * h);
}
float FrameIncoming(int i)
{
	if (i == 0) return 0.375f;
	if (i == 1) return 0.250f;
	if (i == 2) return 0.000f;
	if (i == 3) return 0.750f;
	return 0.625f;
}
float FrameOutgoing(int i)
{
	if (i == 0) return 0.750f;
	if (i == 1) return 0.500f;
	if (i == 2) return 0.250f;
	if (i == 3) return 0.125f;
	return 0.875f;
}
float4 main(VS_OUTPUT v) : PDX_COLOR
{
	float2 p = v.vTexCoord * 450.0f;
	float4 state = tex2D(MapTexture, float2(0.5f, 0.5f));
	// A static 90px data carrier selects the emphasized station; Time is never reset.
	float selectedId = floor(state.r * 255.0f + 0.5f);
	float cycle = frac(Time / 6.4f) * 6.4f;
	float alpha = 0.0f;
	float heat = 0.0f;
	for (int i = 0; i < 5; ++i)
	{
		float n = float(i);
		float chosen = 1.0f - step(0.5f, abs(selectedId - n - 1.0f));
		float2 q = p - FrameNode(i);
		float h = i == 4 ? 38.0f : 55.0f;
		float photoHalf = i == 4 ? 35.5f : 52.0f;
		float maxQ = max(abs(q.x), abs(q.y));
		float rimDistance = abs(maxQ - h);
		float rim = 1.0f - smoothstep(0.8f, 1.9f, rimDistance);
		float softRim = 1.0f - smoothstep(1.8f, 3.4f, rimDistance);
		float segments = 1.0f - smoothstep(h - 20.0f, h - 17.0f, min(abs(q.x), abs(q.y)));
		float age = cycle - n * 1.28f;
		float receive = smoothstep(0.0f, 0.04f, age) * (1.0f - smoothstep(0.74f, 0.78f, age));
		float arc = FrameArc(q, h);
		float entry = FrameIncoming(i);
		float distanceAround = 1.0f + frac(FrameOutgoing(i) - entry);
		float routeHead = frac(entry + distanceAround * saturate(age / 0.78f));
		float routeTail = frac(routeHead - arc);
		float transfer = saturate(1.0f - routeTail / 0.24f) * receive;
		// Only the production-chain transfer travels around the perimeter.
		float movingLight = transfer;
		float part = rim * (0.14f + segments * (0.28f + chosen * 0.10f));
		part = max(part, rim * movingLight * 0.96f + softRim * movingLight * 0.12f);
		float brackets = 0.0f;
		// One actuator per frame: all four jaws share exactly the same travel.
		// Stations retain their phase offset; corners within a station do not.
		float clampPhase = frac(Time / 3.6f - n * 0.13f);
		float closed = smoothstep(0.10f, 0.30f, clampPhase)
			* (1.0f - smoothstep(0.66f, 0.84f, clampPhase));
		float travel = (1.0f - closed) * lerp(3.5f, 6.0f, chosen);
		float reach = h + travel;
		for (int k = 0; k < 4; ++k)
		{
			float2 s = float2(1.0f, 1.0f);
			if (k == 0) s = float2(-1.0f, -1.0f);
			if (k == 1) s = float2(1.0f, -1.0f);
			if (k == 3) s = float2(-1.0f, 1.0f);
			float2 corner = s * reach;
			float horizontal = FrameBox(q, corner - float2(s.x * 7.0f, 0.0f), float2(7.0f, 1.05f));
			float vertical = FrameBox(q, corner - float2(0.0f, s.y * 7.0f), float2(1.05f, 7.0f));
			brackets = max(brackets, max(horizontal, vertical));
			// A shorter inner jaw makes selection legible without a second light orbit.
			float2 innerCorner = s * (reach - 3.0f);
			float innerHorizontal = FrameBox(q, innerCorner - float2(s.x * 5.0f, 0.0f), float2(5.0f, 0.80f));
			float innerVertical = FrameBox(q, innerCorner - float2(0.0f, s.y * 5.0f), float2(0.80f, 5.0f));
			brackets = max(brackets, max(innerHorizontal, innerVertical) * chosen * 0.90f);
		}
		part = max(part, brackets * (0.69f + chosen * 0.21f + receive * 0.08f));
		// Clip every decorative pixel outside the image itself; photographs never wobble.
		float outsidePhoto = step(photoHalf, maxQ);
		part *= outsidePhoto;
		alpha = max(alpha, part);
		heat = max(heat, max(movingLight * rim, brackets * (0.45f + chosen * 0.35f)) * outsidePhoto);
	}
	float3 ink = lerp(float3(0.48f, 0.73f, 0.77f), float3(0.91f, 0.97f, 0.98f), saturate(heat));
	return float4(ink, saturate(alpha) * state.a) * Color;
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
