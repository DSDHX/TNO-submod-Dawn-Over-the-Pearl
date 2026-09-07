Includes = {
	"buttonstate.fxh"
}

PixelShader =
{
	Samplers =
	{
		MapTexture =
		{
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

VertexShader =
{
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

PixelShader =
{
	MainCode PixelShaderMonitor
	[[
		float DOP_SCW_PanelGrid(float coordinate, float frequency, float width)
		{
			float cell = frac(coordinate * frequency);
			float distanceToEdge = min(cell, 1.0f - cell);
			return 1.0f - smoothstep(0.0f, width, distanceToEdge);
		}

		float4 main(VS_OUTPUT v) : PDX_COLOR
		{
			float2 uv = v.vTexCoord;
			float textureMask = tex2D(MapTexture, uv).a;
			float edgeDistance = min(min(uv.x, 1.0f - uv.x), min(uv.y, 1.0f - uv.y));
			float border = 1.0f - smoothstep(0.0f, 0.008f, edgeDistance);

			float gridX = DOP_SCW_PanelGrid(uv.x, 20.0f, 0.018f);
			float gridY = DOP_SCW_PanelGrid(uv.y, 15.0f, 0.018f);
			float grid = max(gridX, gridY);

			float scanX = frac(Time * 0.060f);
			float scanDistance = abs(uv.x - scanX);
			scanDistance = min(scanDistance, 1.0f - scanDistance);
			float scanBeam = exp(-scanDistance * 72.0f);

			// A short acquisition line may play when the empty-state panel is shown.
			float sinceShow = max(0.0f, Time - AnimationTime);
			float bootPosition = saturate(sinceShow / 0.65f);
			float bootLife = 1.0f - smoothstep(0.55f, 0.85f, sinceShow);
			float bootLine = exp(-abs(uv.y - bootPosition) * 82.0f) * bootLife;

			float scanline = 0.5f + 0.5f * sin((uv.y * 480.0f + Time * 2.5f) * 3.14159265f);
			float alpha = border * 0.055f
				+ grid * 0.012f
				+ scanBeam * 0.050f
				+ bootLine * 0.14f
				+ scanline * 0.008f;
			alpha *= textureMask;

			float3 color = lerp(float3(0.12f, 0.58f, 0.56f), float3(0.45f, 0.95f, 0.78f), scanBeam);
			float4 OutColor = float4(color, saturate(alpha));
			OutColor *= Color;
			return OutColor;
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
