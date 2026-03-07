import * as THREE from 'three';

        //Creación de la escena
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        //Código proporcionado para los shaders
        const vertexShader = `
            varying vec2 vUv;
            varying vec3 vNormal;
            uniform float time;

            // Funcion para generar el rudio (semi-aleatoria)
            float hash(float n) { return fract(sin(n) * 43758.5453123); }
            float noise(vec3 x) {
                vec3 p = floor(x);
                vec3 f = fract(x);
                f = f*f*(3.0-2.0*f);
                float n = p.x + p.y*57.0 + 113.0*p.z;
                return mix(mix(mix(hash(n+0.0), hash(n+1.0),f.x),
                        mix(hash(n+57.0), hash(n+58.0),f.x),f.y),
                        mix(mix(hash(n+113.0),hash(n+114.0),f.x),
                        mix(hash(n+170.0),hash(n+171.0),f.x),f.y),f.z);
            }
            void main() {
                vUv = uv;
                vNormal = normal;

                // Procedural Noise
                float noiseVal = noise(vec3(position.x * 2.0, position.y * 2.0, time));
                vec3 pos = position + normal * noiseVal * 0.4;

                // Animacion con uniforms
                float distortion = sin(position.y * 3.0 + time) * 0.2;
                pos = pos + normal * distortion;


                // Deformación con onda (original)
                // vec3 pos = position;
                // pos.z += sin(pos.x * 5.0 + time) * 0.1;

                gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
            }
        `;

        const fragmentShader = `
            varying vec2 vUv;
            varying vec3 vNormal;
            uniform float time;
            void main() {

                // Fresnel Effect
                vec3 viewDir = vec3(0.0, 0.0, 1.0);
                float fresnel = pow(1.0 - dot(vNormal, viewDir), 2.0);

                // Rim Lighting
                vec3 baseColor = vec3(vUv.x, 0.5, vUv.y);
                vec3 color = mix(baseColor, vec3(1.0), fresnel);
                // Viñetado
                float v = smoothstep(0.7, 0.2, distance(vUv, vec2(0.5)));

                // Shader de color Original
                // vec3 color = vec3(vUv, 0.5);
                // color *= dot(vNormal, vec3(0, 0, 1)) * 0.5 + 0.5;


                gl_FragColor = vec4(color*v, 1.0);
            }

        `;

        //Creación del objeto con el shader
        const geometry = new THREE.SphereGeometry(2, 64, 64); // Plano con muchos segmentos para que se doble
        const material = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0.0 }
            },
            vertexShader: vertexShader,
            fragmentShader: fragmentShader,
            side: THREE.DoubleSide
        });

        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        camera.position.z = 5;

        //Animación principal
        function animate(now) {
            requestAnimationFrame(animate);
            const t = now * 0.001;
            material.uniforms.time.value = t;

            //Rotación automática del objeto
            //mesh.rotation.y = t * 0.5;
            //mesh.rotation.x = t * 0.2;

            renderer.render(scene, camera);
        }
        animate();