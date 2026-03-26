Shader "Custom/Fire_Shader"
{
    Properties
    {
        // Color base
        [MainColor] _BaseColor("Base Color", Color) = (0.5, 0, 0.5, 1)
        [MainTexture] _BaseMap("Base Map (Fire Pattern)", 2D) = "white" {}

        // Mapas adicionales
        _NormalMap("Normal Map", 2D) = "bump" {}
        _EmissiveMap("Emissive Map", 2D) = "black" {}

        // Propiedades de color morado dinámico
        _PurpleIntensity("Purple Intensity", Range(0, 2)) = 1.0
        _TimeSpeed("Time Animation Speed", Range(0, 5)) = 1.0

        // Input dinámico
        _MouseInfluence("Mouse Influence", Range(0, 1)) = 0.5
        _AudioInfluence("Audio Influence", Range(0, 1)) = 0.5
        _AudioLevel("Audio Level", Range(0, 1)) = 0

        // Distorsión UV
        _DistortionStrength("Distortion Strength", Range(0, 1)) = 0.3
        _DistortionSpeed("Distortion Speed", Range(0, 3)) = 1.0

        // Propiedades de emisión
        _EmissiveIntensity("Emissive Intensity", Range(0, 10)) = 2.0

        // Color secondary para gradiente
        [MainColor] _SecondaryColor("Secondary Color", Color) = (0.8, 0.2, 0.8, 1)
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" }

        Pass
        {
            HLSLPROGRAM

            #pragma vertex vert
            #pragma fragment frag

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionHCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                float3 viewDir : TEXCOORD2;
            };

            TEXTURE2D(_BaseMap);
            SAMPLER(sampler_BaseMap);
            TEXTURE2D(_NormalMap);
            SAMPLER(sampler_NormalMap);
            TEXTURE2D(_EmissiveMap);
            SAMPLER(sampler_EmissiveMap);

            CBUFFER_START(UnityPerMaterial)
                half4 _BaseColor;
                half4 _SecondaryColor;
                float4 _BaseMap_ST;
                float _PurpleIntensity;
                float _TimeSpeed;
                float _MouseInfluence;
                float _AudioInfluence;
                float _AudioLevel;
                float _DistortionStrength;
                float _DistortionSpeed;
                float _EmissiveIntensity;
            CBUFFER_END

            // Función para ruido simple (Simplex-like)
            float noise(float2 uv)
            {
                return frac(sin(dot(uv, float2(12.9898, 78.233))) * 43758.5453);
            }

            // Función para value noise suavizado
            float smoothNoise(float2 uv, float time)
            {
                float2 i = floor(uv);
                float2 f = frac(uv);

                // Corner sampling
                float a = noise(i + float2(0, 0) + time);
                float b = noise(i + float2(1, 0) + time);
                float c = noise(i + float2(0, 1) + time);
                float d = noise(i + float2(1, 1) + time);

                // Interpolación smooth
                float2 u = f * f * (3.0 - 2.0 * f);

                return lerp(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
            }

            Varyings vert(Attributes IN)
            {
                Varyings OUT;
                OUT.positionHCS = TransformObjectToHClip(IN.positionOS.xyz);
                OUT.uv = TRANSFORM_TEX(IN.uv, _BaseMap);
                OUT.normalWS = TransformObjectToWorldNormal(IN.normalOS);
                OUT.viewDir = GetWorldSpaceViewDir(TransformObjectToWorld(IN.positionOS.xyz));
                return OUT;
            }

            half4 frag(Varyings IN) : SV_Target
            {
                float time = _Time.y * _TimeSpeed;

                // === DISTRESIÓN UV para simular fluidez ===
                // Crear patrón de fuego oscilante
                float2 distortedUV = IN.uv;

                // Distorsión basada en noise y tiempo
                float noiseVal = smoothNoise(IN.uv * 3.0, time * _DistortionSpeed);
                float waveX = sin(IN.uv.y * 10.0 + time * 2.0) * _DistortionStrength;
                float waveY = cos(IN.uv.x * 8.0 + time * 1.5) * _DistortionStrength * 0.5;

                // Mover UVs hacia arriba (como fuego)
                distortedUV.x += waveX + (noiseVal - 0.5) * _DistortionStrength;
                distortedUV.y += waveY + time * 0.2;

                // Sample de mapas con UV distorsionado
                half4 baseColor = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, distortedUV);
                half4 normalMap = SAMPLE_TEXTURE2D(_NormalMap, sampler_NormalMap, distortedUV);
                half4 emissiveMap = SAMPLE_TEXTURE2D(_EmissiveMap, sampler_EmissiveMap, distortedUV);

                // === COLOR MORADO DINÁMICO ===
                // Calcular factor de cambio de color basado en Time
                float timeFactor = sin(time * 2.0) * 0.5 + 0.5;

                // Gradiente vertical para fuego (más intenso arriba)
                float verticalGradient = 1.0 - IN.uv.y;

                // === INPUTS DINÁMICOS ===
                // Simular input de mouse (usando coordenadas normalizadas del tiempo)
                float mouseEffect = sin(time * 3.0 + IN.uv.x * 5.0) * _MouseInfluence;

                // Input de audio
                float audioEffect = _AudioLevel * _AudioInfluence;

                // Combinar todos los factores dinámicos
                float dynamicFactor = timeFactor * 0.4 + mouseEffect * 0.3 + audioEffect * 0.3;

                // Color morado base
                float3 purpleColor = float3(0.5, 0.0, 0.5); // Morado base
                float3 brightPurple = float3(0.8, 0.2, 0.8); // Morado brillante
                float3 deepPurple = float3(0.3, 0.0, 0.4);   // Morado oscuro

                // Interpolación de colores según factor dinámico
                float3 dynamicPurple = lerp(deepPurple, brightPurple, dynamicFactor);
                dynamicPurple = lerp(dynamicPurple, purpleColor, 0.3);

                // Aplicar intensidad
                dynamicPurple *= _PurpleIntensity;

                // Mezclar color de la textura con el color morado dinámico
                float3 finalColor = baseColor.rgb * dynamicPurple;

                // Combinar con color secundario para gradiente
                finalColor = lerp(finalColor, _SecondaryColor.rgb, verticalGradient * 0.5);

                // Añadir efecto del normal map (simulado - iluminación básica)
                float3 normalPerturb = normalMap.rgb * 2.0 - 1.0;
                float lightIntensity = dot(normalPerturb, normalize(float3(1, 1, 1)));
                finalColor *= (0.8 + lightIntensity * 0.4);

                // Añadir emisión
                finalColor += emissiveMap.rgb * _EmissiveIntensity;

                //OUTPUT
                return half4(finalColor, 1.0);
            }
            ENDHLSL
        }
    }
}
