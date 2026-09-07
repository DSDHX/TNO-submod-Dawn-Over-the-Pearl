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

 float progress=smoothstep(.02f,.40f,phase);
 float curtain=1.0f-smoothstep(.44f,.56f,phase);
 float life=1.0f-smoothstep(.40f,.47f,phase);
 float track=B(p,float2(528,318),float2(270,9))-B(p,float2(528,318),float2(268,7));
 float cells=0.0f;
 for(int i=0;i<8;++i){float n=float(i);float c=B(p,float2(318+n*60,318),float2(26,3.5f));cells=max(cells,c*(.08f+saturate(progress*8-n)*.75f));}
 float checks=0.0f;
 for(int j=0;j<3;++j){float n=float(j);checks=max(checks,B(p,float2(512+n*16,295),float2(4,1.0f))*smoothstep(n*.09f,n*.09f+.07f,phase));}
 color+=float3(.59f,.80f,.88f)*(track*.4f+cells+checks*.45f)*life;
 float reveal=smoothstep(.62f,.97f,phase);
 float photo=B(p,float2(255,241),float2(210,84));
 float scan=p.y-157.0f-reveal*168.0f;
 float cover=photo*(reveal<.0001f?1.0f:smoothstep(-.7f,.7f,scan));
 if(reveal>=.9999f)cover=0;
 float sweep=photo*(1.0f-smoothstep(.3f,1.5f,abs(scan)))*step(.001f,reveal)*(1-step(.999f,reveal));
 color=lerp(color,surface,cover*(1-curtain));
 color=lerp(color,float3(.70f,.89f,.93f),sweep*(1-curtain)*.6f);
 float alpha=max(curtain,max(cover,sweep*.6f));

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

