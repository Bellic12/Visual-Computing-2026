import * as THREE from 'three';

        // --- 1. ESCENA BÁSICA ---
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        // --- 2. EL SHADER (Código que te pasaron) ---
        const vertexShader = `
            uniform float time;
            varying vec2 vUv;
            void main() {
                vUv = uv;
                vec3 pos = position;
                // Deformación de onda
                pos.z += sin(pos.x * 5.0 + time) * 0.2;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
            }
        `;

        const fragmentShader = `
            varying vec2 vUv;
            uniform float time;
            void main() {
                // Color basado en coordenadas y tiempo
                vec3 color = vec3(vUv.x, vUv.y, abs(sin(time)));
                gl_FragColor = vec4(color, 1.0);
            }
        `;

        // --- 3. CREAR EL OBJETO ---
        const geometry = new THREE.PlaneGeometry(5, 5, 32, 32); // Plano con muchos segmentos para que se doble
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

        // --- 4. BUCLE DE ANIMACIÓN ---
        function animate(now) {
            requestAnimationFrame(animate);
            
            // Actualizamos el uniform 'time' (convertido a segundos)
            material.uniforms.time.value = now * 0.001;
            
            renderer.render(scene, camera);
        }
        animate();