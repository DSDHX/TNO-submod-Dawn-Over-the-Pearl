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
			// The same regular-sprite state clock as the full loading curtain.
			float age = max(0.0f, Time - AnimationTime);
			float phase = saturate(age / 2.6f);
			if (phase >= 0.97f)
				return float4(0.0f, 0.0f, 0.0f, 0.0f);

			// Square, pie-local coordinates. No whole-window position is used here.
			float uScale = abs(ddy(v.vTexCoord.y))
				/ max(abs(ddx(v.vTexCoord.x)), 0.0000001f);
			float2 uv = float2(frac(v.vTexCoord.x * uScale), v.vTexCoord.y);
			float2 pie = (uv - float2(0.5f, 0.5f)) * 360.0f;
			float radius = length(pie);
			float disc = 1.0f - smoothstep(178.0f, 180.0f, radius);
			// Curtain has fully disappeared at phase .54; fan starts at .59.
			float fan = smoothstep(0.59f, 0.97f, phase);
			float hidden = 1.0f;
			if (fan > 0.0001f)
			{
				float angle = atan2(pie.x, -pie.y);
				if (angle < 0.0f)
					angle += 6.28318531f;
				float aa = 0.8f / max(radius, 1.0f);
				hidden = smoothstep(fan * 6.28318531f - aa, fan * 6.28318531f + aa, angle);
			}
			return float4(0.067f, 0.102f, 0.133f, disc * hidden * tex2D(MapTexture, float2(0.5f, 0.5f)).a) * Color;
		}
	]]
}
BlendState BlendState
{
	BlendEnable = yes
	SourceBlend = "SRC_ALPHA"
	DestBlend = "INV_SRC_ALPHA"
}
Effect Up { VertexShader = "VertexShader" PixelShader = "PixelShaderMonitor" }
Effect Down { VertexShader = "VertexShader" PixelShader = "PixelShaderMonitor" }
Effect Disable { VertexShader = "VertexShader" PixelShader = "PixelShaderMonitor" }
Effect Over { VertexShader = "VertexShader" PixelShader = "PixelShaderMonitor" }
