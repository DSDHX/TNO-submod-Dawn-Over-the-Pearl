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

float4 main(VS_OUTPUT v) : PDX_COLOR
{
	float4 base = tex2D(MapTexture, v.vTexCoord);
	float2 p = v.vTexCoord * 102.0f;
	float2 q = abs(p - 51.0f);
	// The logistics emblem occupies a smaller alpha-bounded square in its 102px canvas.
	float compact = 1.0f - step(0.5f, tex2D(MapTexture, float2(0.06f, 0.5f)).a);
	float halfSize = lerp(49.0f, 33.5f, compact);
	float edge = 1.0f - smoothstep(0.55f, 1.3f, abs(max(q.x, q.y) - halfSize));
	float corners = edge * smoothstep(halfSize - 14.0f, halfSize - 11.0f, min(q.x, q.y));
	float breathing = 0.68f + 0.12f * sin(Time * 1.9634954f);
	float marks = 0.0f;
	for (int i = 0; i < 3; ++i)
	{
		float n = float(i);
		float2 d = abs(p - float2(76.0f - compact * 15.0f + n * 6.0f, 95.0f - compact * 17.0f)) - float2(1.45f, 1.55f);
		float pip = 1.0f - smoothstep(-0.3f, 0.65f, max(d.x, d.y));
		float wave = 0.5f + 0.5f * sin(Time * 3.14159265f - n * 1.55f);
		marks = max(marks, pip * (0.34f + wave * 0.54f));
	}
	float light = max(corners * breathing, marks);
	// The photograph itself stays stable. Only inset corner marks and three tiny pips move.
	base.rgb = lerp(base.rgb, float3(0.72f, 0.92f, 0.94f), light);
	base.a = max(base.a, light);
	return base * Color;
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
