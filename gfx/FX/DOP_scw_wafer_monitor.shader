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
		float DOP_SCW_WaferHash(float seed)
		{
			return frac(sin(seed * 12.9898f) * 43758.5453f);
		}

		float DOP_SCW_WaferGridLine(float coordinate, float frequency, float width)
		{
			float cell = frac(coordinate * frequency);
			float distanceToEdge = min(cell, 1.0f - cell);
			return 1.0f - smoothstep(0.0f, width, distanceToEdge);
		}

		float DOP_SCW_WaferHairline(float distanceValue, float halfWidth)
		{
			return 1.0f - smoothstep(halfWidth, halfWidth + 0.0035f, abs(distanceValue));
		}

		float4 main(VS_OUTPUT v) : PDX_COLOR
		{
			static const float3 WAFER_DARK = float3(0.028f, 0.040f, 0.080f);
			static const float3 WAFER_LIGHT = float3(0.135f, 0.220f, 0.340f);
			static const float3 PHOSPHOR = float3(0.100f, 0.650f, 0.960f);
			static const float3 EXPOSURE = float3(0.760f, 0.940f, 1.000f);
			static const float3 ALIGNMENT = float3(0.940f, 0.220f, 0.680f);
			static const float3 SUBSTRATE = float3(0.012f, 0.022f, 0.052f);
			static const float3 SILVER = float3(0.590f, 0.680f, 0.800f);

			float2 uv = v.vTexCoord;
			float carrierAlpha = tex2D(MapTexture, uv).a;
			float2 p = uv - float2(0.5f, 0.5f);
			float radius = length(p);

			// Circular 300 mm wafer silhouette with the orientation notch at six o'clock.
			float outerCircle = 1.0f - smoothstep(0.432f, 0.444f, radius);
			float innerCircle = 1.0f - smoothstep(0.414f, 0.424f, radius);
			float notchDistance = length(p - float2(0.0f, 0.431f));
			float notchCut = 1.0f - smoothstep(0.020f, 0.027f, notchDistance);
			float wafer = outerCircle * (1.0f - notchCut);
			float waferInner = innerCircle * (1.0f - notchCut);
			float rim = saturate(wafer - waferInner);
			float notchRim = (1.0f - smoothstep(0.0020f, 0.0065f, abs(notchDistance - 0.0235f)))
				* smoothstep(0.392f, 0.412f, p.y)
				* outerCircle;

			// Fixed die lattice. Variation is spatial only, so no grain can flicker.
			float2 waferUV = p / 0.840f + float2(0.5f, 0.5f);
			float gridX = DOP_SCW_WaferGridLine(waferUV.x, 14.0f, 0.038f);
			float gridY = DOP_SCW_WaferGridLine(waferUV.y, 14.0f, 0.038f);
			float grid = max(gridX, gridY) * waferInner;
			float2 dieCell = floor(waferUV * 14.0f);
			float dieVariation = DOP_SCW_WaferHash(dieCell.x + dieCell.y * 19.0f);
			float2 dieLocal = frac(waferUV * 14.0f) - float2(0.5f, 0.5f);

			// One-way twelve-second cycle: load, scan down, hold, pick dies, reset off-screen.
			float exposureCycle = frac(Time * 0.08333333f);
			float loadEnvelope = smoothstep(0.000f, 0.060f, exposureCycle);
			float scanTravel = saturate((exposureCycle - 0.070f) / 0.570f);
			float scanY = -0.500f + scanTravel;
			float beamGate = smoothstep(0.055f, 0.080f, exposureCycle)
				* (1.0f - smoothstep(0.620f, 0.655f, exposureCycle));

			// Each die has a tiny fixed delay, producing a visible row-by-row cascade.
			float dieCenterY = ((dieCell.y + 0.5f) / 14.0f - 0.5f) * 0.840f;
			float dieProgress = saturate((dieCenterY + 0.420f) / 0.840f);
			float dieTrigger = clamp(dieProgress + (dieVariation - 0.5f) * 0.025f, 0.040f, 0.960f);
			float dieLatched = smoothstep(dieTrigger - 0.028f, dieTrigger + 0.028f, scanTravel);
			float activationBand = (1.0f - smoothstep(0.000f, 0.040f, abs(scanTravel - dieTrigger)))
				* beamGate;

			// Diagonal pick-up cascade. Each die rises inside its slot, shrinks, then vanishes.
			float removalTimeline = saturate((exposureCycle - 0.720f) / 0.220f);
			float removalOrder = saturate((dieCell.x + dieCell.y) / 26.0f);
			float removalTrigger = clamp(removalOrder * 0.820f + dieVariation * 0.100f, 0.060f, 0.920f);
			float dieRemoval = smoothstep(removalTrigger - 0.045f, removalTrigger + 0.070f, removalTimeline);
			float pickupScale = 1.0f - dieRemoval * 0.180f;
			float2 liftedLocal = float2(dieLocal.x, dieLocal.y + dieRemoval * 0.700f) / pickupScale;
			float liftedBoxDistance = max(abs(liftedLocal.x), abs(liftedLocal.y));
			float liftedDieBody = 1.0f - smoothstep(0.365f, 0.425f, liftedBoxDistance);
			float pickupFade = 1.0f - smoothstep(0.700f, 1.000f, dieRemoval);
			float dieVisible = liftedDieBody * pickupFade * loadEnvelope * waferInner;
			float pickupEdge = 1.0f - smoothstep(0.010f, 0.036f, abs(liftedBoxDistance - 0.395f));
			float pickupGlow = 4.0f * dieRemoval * (1.0f - dieRemoval);
			pickupEdge *= pickupFade * loadEnvelope * pickupGlow * waferInner;

			float incidence = saturate(0.58f + dot(p, float2(-0.58f, -0.72f)));
			float centerLift = 1.0f - saturate(radius / 0.445f);
			float baseLight = saturate(incidence * 0.620f + centerLift * 0.240f);
			float3 dieSurface = lerp(WAFER_DARK, WAFER_LIGHT, baseLight);
			dieSurface *= 0.900f + dieVariation * 0.140f;
			float activeDie = dieLatched * pickupFade;
			float3 color = SUBSTRATE * wafer * 0.700f;
			float silverBrush = 0.840f + 0.160f * sin((p.x * 0.38f + p.y) * 188.0f);
			float silverBase = wafer * (1.0f - dieVisible * 0.780f);
			color += SILVER * silverBase * silverBrush * 0.105f;
			color += dieSurface * dieVisible * (0.820f + activeDie * 0.260f);
			color += PHOSPHOR * activeDie * dieVisible * 0.215f;
			color += EXPOSURE * activationBand * dieVisible * 0.180f;
			color += PHOSPHOR * grid * (0.070f + activeDie * 0.160f);
			color += ALIGNMENT * pickupEdge * 0.520f;

			// Blue-silver thin-film interference replaces the previous dark-green cast.
			float interferencePhase = p.x * 13.0f - p.y * 9.0f + radius * 18.0f - Time * 0.290f;
			float3 interference = float3(
				0.5f + 0.5f * cos(interferencePhase),
				0.5f + 0.5f * cos(interferencePhase + 2.09439510f),
				0.5f + 0.5f * cos(interferencePhase + 4.18879020f)
			);
			float interferenceMask = dieVisible * (0.32f + centerLift * 0.68f);
			color += interference * interferenceMask * (0.050f + activeDie * 0.032f);

			// The stepper reticle breathes gently while the registration marks stay fixed.
			float reticleVertical = DOP_SCW_WaferHairline(abs(p.x) - 0.158f, 0.0014f)
				* (1.0f - smoothstep(0.116f, 0.124f, abs(p.y)));
			float reticleHorizontal = DOP_SCW_WaferHairline(abs(p.y) - 0.116f, 0.0014f)
				* (1.0f - smoothstep(0.158f, 0.166f, abs(p.x)));
			float reticle = max(reticleVertical, reticleHorizontal) * waferInner;

			float centerCrossV = DOP_SCW_WaferHairline(p.x, 0.0012f)
				* (1.0f - smoothstep(0.026f, 0.034f, abs(p.y)));
			float centerCrossH = DOP_SCW_WaferHairline(p.y, 0.0012f)
				* (1.0f - smoothstep(0.026f, 0.034f, abs(p.x)));
			float centerCross = max(centerCrossV, centerCrossH) * waferInner;

			float horizontalTicks = DOP_SCW_WaferHairline(p.y, 0.0013f)
				* smoothstep(0.344f, 0.360f, abs(p.x))
				* (1.0f - smoothstep(0.405f, 0.418f, abs(p.x)));
			float verticalTicks = DOP_SCW_WaferHairline(p.x, 0.0013f)
				* smoothstep(0.344f, 0.360f, abs(p.y))
				* (1.0f - smoothstep(0.405f, 0.418f, abs(p.y)));
			float fiducials = max(horizontalTicks, verticalTicks) * wafer;
			float reticlePulse = 0.76f + 0.24f * (0.5f + 0.5f * sin(Time * 0.920f));
			color += PHOSPHOR * (
				reticle * 0.225f * reticlePulse
				+ centerCross * 0.320f * reticlePulse
				+ fiducials * 0.390f
			);

			// A three-line exposure head travels only from top to bottom.
			float scanDistance = abs(p.y - scanY);
			float scanCore = exp(-scanDistance * 132.0f) * beamGate * waferInner;
			float scanHalo = exp(-scanDistance * 29.0f) * beamGate * waferInner;
			float scanUpper = exp(-abs(p.y - (scanY - 0.014f)) * 172.0f) * beamGate * waferInner;
			float scanLower = exp(-abs(p.y - (scanY + 0.014f)) * 172.0f) * beamGate * waferInner;
			color += EXPOSURE * (scanCore * 0.340f + scanHalo * 0.062f);
			color += ALIGNMENT * scanUpper * 0.155f;
			color += PHOSPHOR * scanLower * 0.135f;

			// Two calibration patterns orbit on the rim.
			float waferAngle = atan2(p.y, p.x);
			float rimClock = Time * 0.300f;
			float rimArcA = pow(saturate(0.5f + 0.5f * cos(waferAngle * 3.0f - rimClock)), 12.0f);
			float rimArcB = pow(saturate(0.5f + 0.5f * cos(waferAngle * 2.0f + rimClock * 0.63f + 2.1f)), 16.0f);
			float rimArc = saturate(rimArcA * 0.72f + rimArcB * 0.42f) * rim;

			// Twin silver rails, etched ticks, moving slots, and two tracker nodes surround the wafer.
			float hudOuterRail = 1.0f - smoothstep(0.0018f, 0.0048f, abs(radius - 0.472f));
			float hudInnerRail = 1.0f - smoothstep(0.0016f, 0.0042f, abs(radius - 0.458f));
			float hudDashPhase = 0.5f + 0.5f * cos(waferAngle * 24.0f - Time * 1.050f);
			float hudDash = smoothstep(0.360f, 0.760f, hudDashPhase);
			float hudTickPhase = 0.5f + 0.5f * cos(waferAngle * 56.0f);
			float hudTicks = smoothstep(0.620f, 0.900f, hudTickPhase)
				* smoothstep(0.461f, 0.464f, radius)
				* (1.0f - smoothstep(0.468f, 0.471f, radius));
			float hudRing = hudOuterRail * (0.420f + hudDash * 0.580f)
				+ hudInnerRail * 0.720f
				+ hudTicks * 0.820f;
			float trackerA = pow(saturate(0.5f + 0.5f * cos(waferAngle - Time * 0.340f)), 30.0f)
				* hudOuterRail;
			float trackerB = pow(saturate(0.5f + 0.5f * cos(waferAngle + Time * 0.240f + 2.7f)), 36.0f)
				* hudOuterRail;

			color += PHOSPHOR * rim * 0.210f;
			color += SILVER * rim * 0.260f;
			color += PHOSPHOR * notchRim * 0.260f;
			color += EXPOSURE * rimArc * 0.490f;
			color += SILVER * (hudOuterRail * 0.400f + hudInnerRail * 0.280f + hudTicks * 0.360f);
			color += PHOSPHOR * hudOuterRail * hudDash * 0.360f;
			color += EXPOSURE * trackerA * 0.620f;
			color += ALIGNMENT * trackerB * 0.520f;

			// Die interiors become genuine transparent vacancies after pick-up.
			float alpha = wafer * 0.045f;
			alpha += silverBase * 0.075f;
			alpha += grid * 0.180f;
			alpha += dieVisible * (0.800f + activeDie * 0.100f);
			alpha += pickupEdge * 0.150f;
			alpha += rim * 0.520f;
			alpha += scanCore * 0.038f;
			alpha += rimArc * 0.022f;
			alpha = max(alpha, hudRing * 0.580f);
			alpha = max(alpha, trackerA * 0.720f);
			alpha = max(alpha, trackerB * 0.660f);
			alpha = max(alpha, notchRim * 0.460f);
			alpha *= carrierAlpha;

			float4 OutColor = float4(saturate(color), saturate(alpha));
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
