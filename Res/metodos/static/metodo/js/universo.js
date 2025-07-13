document.addEventListener('DOMContentLoaded', function() {
    // Configuración del universo
    const container = document.getElementById('universe-container');
    const galaxiesContainer = document.getElementById('galaxies-container');
    const blackHole = document.getElementById('black-hole');
    const infoPanel = document.getElementById('info-panel');
    const infoContent = document.getElementById('info-content');
    const closeInfo = document.getElementById('close-info');
    const tryButton = document.getElementById('try-button');
    
    // Variables de estado
    let currentGalaxy = null;
    let particles = [];
    let shootingStars = [];
    let threeJSScene, threeJSCamera, threeJSRenderer, threeJSStars;
    let galaxyPositions = [];
    let isAnimating = false;
    
    // Inicialización del universo
    initUltimateUniverse();
    
    // Configuración de eventos
    blackHole.addEventListener('click', showUltimateBlackHoleInfo);
    closeInfo.addEventListener('click', hideUltimateInfoPanel);
    window.addEventListener('resize', handleUltimateResize);
    
    // Función de inicialización
    function initUltimateUniverse() {
        createParticles(500);
        createShootingStars(5);
        createUltimateGalaxies();
        initUltimateThreeJS();
        animateUniverse();
    }
    
    // Crear partículas de fondo
    function createParticles(count) {
        for (let i = 0; i < count; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            const size = Math.random() * 3;
            const opacity = 0.2 + Math.random() * 0.8;
            const x = Math.random() * 100;
            const y = Math.random() * 100;
            const duration = 15 + Math.random() * 30;
            const delay = Math.random() * 15;
            
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.opacity = opacity;
            particle.style.left = `${x}%`;
            particle.style.top = `${y}%`;
            particle.style.animationDuration = `${duration}s`;
            particle.style.animationDelay = `-${delay}s`;
            
            container.appendChild(particle);
            particles.push(particle);
        }
    }
    
    // Crear estrellas fugaces
    function createShootingStars(count) {
        for (let i = 0; i < count; i++) {
            const star = document.createElement('div');
            star.className = 'shooting-star';
            
            // Posición inicial aleatoria
            const startX = Math.random() * window.innerWidth;
            const startY = Math.random() * window.innerHeight * 0.5;
            
            star.style.left = `${startX}px`;
            star.style.top = `${startY}px`;
            
            container.appendChild(star);
            shootingStars.push(star);
            
            // Animar estrella fugaz
            animateShootingStar(star);
        }
    }
    
    // Animación de estrella fugaz
    function animateShootingStar(star) {
        const duration = 2 + Math.random() * 3;
        const delay = 5 + Math.random() * 20;
        
        // Resetear posición
        const startX = -100;
        const startY = Math.random() * window.innerHeight * 0.5;
        const endX = window.innerWidth + 100;
        const endY = startY + (Math.random() * 200 - 100);
        
        star.style.left = `${startX}px`;
        star.style.top = `${startY}px`;
        star.style.opacity = '0';
        
        // Crear cola
        const tail = document.createElement('div');
        tail.className = 'shooting-star-tail';
        tail.style.position = 'absolute';
        tail.style.width = '0';
        tail.style.height = '2px';
        tail.style.background = 'linear-gradient(90deg, rgba(255,255,255,0), white)';
        tail.style.transformOrigin = 'left center';
        star.appendChild(tail);
        
        // Animación
        gsap.to(star, {
            left: endX,
            top: endY,
            opacity: 1,
            duration: duration,
            delay: delay,
            ease: "power1.in",
            onUpdate: function() {
                // Actualizar cola
                const dx = parseFloat(star.style.left) - startX;
                const dy = parseFloat(star.style.top) - startY;
                const distance = Math.sqrt(dx * dx + dy * dy);
                tail.style.width = `${distance}px`;
                tail.style.transform = `rotate(${Math.atan2(dy, dx)}rad)`;
            },
            onComplete: function() {
                tail.remove();
                star.style.opacity = '0';
                // Repetir animación
                setTimeout(() => animateShootingStar(star), 1000);
            }
        });
    }
    
    // Crear galaxias dispersas
    function createUltimateGalaxies() {
        const margin = 150;
        const maxX = window.innerWidth - margin;
        const maxY = window.innerHeight - margin;
        
        galaxiesConfig.forEach((galaxy, index) => {
            // Posición aleatoria pero equilibrada
            let x, y;
            
            if (index % 2 === 0) {
                // Algunas más hacia los lados
                x = margin + Math.random() * (window.innerWidth * 0.3);
                if (Math.random() > 0.5) x = window.innerWidth - x;
                y = margin + Math.random() * (window.innerHeight - margin * 2);
            } else {
                // Otras más centradas
                x = window.innerWidth * 0.3 + Math.random() * (window.innerWidth * 0.4);
                y = margin + Math.random() * (window.innerHeight - margin * 2);
            }
            
            // Asegurar que estén dentro de los límites
            x = Math.max(margin, Math.min(x, maxX));
            y = Math.max(margin, Math.min(y, maxY));
            
            // Profundidad Z (efecto 3D)
            const zDepth = (Math.random() * 20) - 10;
            
            const galaxyEl = document.createElement('div');
            galaxyEl.className = 'galaxy';
            galaxyEl.id = `galaxy-${galaxy.id}`;
            galaxyEl.style.left = `${x}px`;
            galaxyEl.style.top = `${y}px`;
            galaxyEl.style.color = galaxy.color;
            galaxyEl.style.transform = `translateZ(${zDepth}px)`;
            
            galaxyEl.innerHTML = `
                <div class="galaxy-inner">
                    <div class="galaxy-core" style="color: ${galaxy.color}"></div>
                    ${createGalaxyArms(galaxy.color)}
                </div>
                <div class="absolute -bottom-8 w-full text-center text-sm font-bold tracking-wider" 
                     style="color: ${galaxy.color}; text-shadow: 0 0 15px ${galaxy.color}">
                    ${galaxy.name}
                </div>
            `;
            
            galaxyEl.addEventListener('click', () => showUltimateGalaxyInfo(galaxy));
            galaxyEl.addEventListener('mouseenter', () => onGalaxyHover(galaxyEl));
            galaxyEl.addEventListener('mouseleave', () => onGalaxyHoverEnd(galaxyEl));
            
            galaxiesContainer.appendChild(galaxyEl);
            
            // Guardar posición para animaciones
            galaxyPositions.push({
                element: galaxyEl,
                x: x,
                y: y,
                z: zDepth,
                floating: {
                    amplitude: 10 + Math.random() * 20,
                    speed: 0.5 + Math.random() * 0.5,
                    offset: Math.random() * Math.PI * 2
                }
            });
        });
    }
    
    // Efectos hover galaxia mejorados
    function onGalaxyHover(element) {
        if (isAnimating) return;
        
        gsap.to(element, {
            scale: 1.2,
            duration: 0.5,
            ease: "elastic.out(1, 0.5)"
        });
        
        const core = element.querySelector('.galaxy-core');
        gsap.to(core, {
            boxShadow: `0 0 50px 20px currentColor`,
            duration: 0.5
        });
    }
    
    function onGalaxyHoverEnd(element) {
        if (isAnimating) return;
        
        gsap.to(element, {
            scale: 1,
            duration: 0.5,
            ease: "back.out(2)"
        });
        
        const core = element.querySelector('.galaxy-core');
        gsap.to(core, {
            boxShadow: `0 0 40px 15px currentColor`,
            duration: 0.5
        });
    }
    
    // Crear brazos de galaxia con más detalle
    function createGalaxyArms(color) {
        let arms = '';
        const armCount = 4 + Math.floor(Math.random() * 3);
        const coreSize = 40;
        
        for (let i = 0; i < armCount; i++) {
            const angle = i * ((2 * Math.PI) / armCount);
            const armLength = 30 + Math.random() * 40;
            const armWidth = 10 + Math.random() * 20;
            
            // Crear segmentos del brazo
            const segmentCount = 3 + Math.floor(Math.random() * 3);
            for (let j = 0; j < segmentCount; j++) {
                const segmentPos = j / segmentCount;
                const size = armWidth * (1 - segmentPos * 0.7);
                const distance = coreSize/2 + armLength * segmentPos;
                const x = 50 + distance * Math.cos(angle + Math.sin(segmentPos * Math.PI) * 0.3);
                const y = 50 + distance * Math.sin(angle + Math.sin(segmentPos * Math.PI) * 0.3);
                const opacity = 0.6 + (1 - segmentPos) * 0.4;
                const duration = 3 + Math.random() * 3;
                const rotation = angle + (Math.random() * 0.4 - 0.2);
                
                arms += `
                    <div class="galaxy-arm" 
                         style="width: ${size}px; height: ${size}px; 
                                background-color: ${color}; left: ${x}px; 
                                top: ${y}px; opacity: ${opacity};
                                animation-duration: ${duration}s;
                                transform: rotate(${rotation}rad) translateZ(${j * 2}px)"></div>
                `;
            }
        }
        return arms;
    }
    
    // Three.js ultra mejorado
    function initUltimateThreeJS() {
        if (typeof THREE === 'undefined') return;
        
        // Escena
        threeJSScene = new THREE.Scene();
        
        // Cámara
        threeJSCamera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        threeJSCamera.position.z = 15;
        
        // Renderer
        threeJSRenderer = new THREE.WebGLRenderer({ 
            alpha: true,
            antialias: true 
        });
        threeJSRenderer.setPixelRatio(window.devicePixelRatio);
        threeJSRenderer.setSize(window.innerWidth, window.innerHeight);
        threeJSRenderer.domElement.style.position = 'fixed';
        threeJSRenderer.domElement.style.top = '0';
        threeJSRenderer.domElement.style.left = '0';
        threeJSRenderer.domElement.style.zIndex = '0';
        threeJSRenderer.domElement.style.pointerEvents = 'none';
        
        container.insertBefore(threeJSRenderer.domElement, container.firstChild);
        
        // Estrellas 3D con diferentes tamaños y colores
        const starGeometry = new THREE.BufferGeometry();
        const starMaterial = new THREE.PointsMaterial({
            size: 0.2,
            sizeAttenuation: true,
            transparent: true,
            opacity: 1,
            vertexColors: true,
            blending: THREE.AdditiveBlending
        });
        
        const positions = [];
        const colors = [];
        const sizes = [];
        
        for (let i = 0; i < 10000; i++) {
            // Posición en forma esférica
            const radius = 10 + Math.random() * 50;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos((Math.random() * 2) - 1);
            
            const x = radius * Math.sin(phi) * Math.cos(theta);
            const y = radius * Math.sin(phi) * Math.sin(theta);
            const z = radius * Math.cos(phi);
            
            positions.push(x, y, z);
            
            // Colores aleatorios con tendencia al blanco/azul
            const color = new THREE.Color();
            if (Math.random() > 0.8) {
                // Algunas estrellas de colores
                color.setHSL(Math.random(), 0.8, 0.7);
            } else {
                // Mayoría blancas/azuladas
                const intensity = 0.7 + Math.random() * 0.3;
                color.r = intensity;
                color.g = intensity;
                color.b = 0.9 + Math.random() * 0.1;
            }
            colors.push(color.r, color.g, color.b);
            
            // Tamaños aleatorios
            sizes.push(0.05 + Math.random() * 0.3);
        }
        
        starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        starGeometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        starGeometry.setAttribute('size', new THREE.Float32BufferAttribute(sizes, 1));
        
        threeJSStars = new THREE.Points(starGeometry, starMaterial);
        threeJSScene.add(threeJSStars);
        
        // Nebulosas mejoradas
        createNebulae();
        
        // Animación
        animateThreeJS();
    }
    
    // Crear nebulosas con más detalle
    function createNebulae() {
        const nebulaColors = [
            new THREE.Color(0x4F46E5),  // Violeta
            new THREE.Color(0x3B82F6),  // Azul
            new THREE.Color(0x10B981),  // Verde
            new THREE.Color(0xF59E0B)   // Amarillo
        ];
        
        for (let i = 0; i < 4; i++) {
            const geometry = new THREE.SphereGeometry(10 + Math.random() * 10, 32, 32);
            const material = new THREE.MeshBasicMaterial({
                color: nebulaColors[i],
                transparent: true,
                opacity: 0.03 + Math.random() * 0.03,
                blending: THREE.AdditiveBlending
            });
            
            const nebula = new THREE.Mesh(geometry, material);
            nebula.position.set(
                (Math.random() - 0.5) * 100,
                (Math.random() - 0.5) * 100,
                (Math.random() - 0.5) * 100
            );
            nebula.scale.setScalar(2 + Math.random() * 3);
            threeJSScene.add(nebula);
        }
    }
    
    // Animación Three.js mejorada
    function animateThreeJS() {
        requestAnimationFrame(animateThreeJS);
        
        // Rotación suave de estrellas
        threeJSStars.rotation.x += 0.0001;
        threeJSStars.rotation.y += 0.0002;
        
        // Render
        threeJSRenderer.render(threeJSScene, threeJSCamera);
    }
    
    // Animación principal del universo
    function animateUniverse() {
        // Flotar galaxias
        galaxyPositions.forEach(pos => {
            const now = Date.now() / 1000;
            const offsetY = Math.sin(now * pos.floating.speed + pos.floating.offset) * pos.floating.amplitude;
            
            gsap.to(pos.element, {
                y: pos.y + offsetY,
                duration: 2,
                ease: "sine.inOut"
            });
        });
        
        requestAnimationFrame(animateUniverse);
    }
    
    // Mostrar información de galaxia ultra mejorada
    function showUltimateGalaxyInfo(galaxy) {
        if (isAnimating) return;
        isAnimating = true;
        
        currentGalaxy = galaxy;
        infoContent.innerHTML = `
            <h2 class="text-3xl font-bold mb-6" style="color: ${galaxy.color}">${galaxy.name}</h2>
            ${galaxy.content}
        `;
        tryButton.href = galaxy.url;
        tryButton.style.background = `linear-gradient(135deg, ${galaxy.color}, ${lightenColor(galaxy.color, 20)})`;
        
        const galaxyElement = document.getElementById(`galaxy-${galaxy.id}`);
        const allGalaxies = document.querySelectorAll('.galaxy');
        
        // Efecto de zoom y atracción hacia la galaxia seleccionada
        allGalaxies.forEach(g => {
            if (g !== galaxyElement) {
                gsap.to(g, {
                    x: galaxyElement.offsetLeft - g.offsetLeft,
                    y: galaxyElement.offsetTop - g.offsetTop,
                    scale: 0.2,
                    opacity: 0.3,
                    duration: 1.5,
                    ease: "power2.in",
                    overwrite: true
                });
            }
        });
        
        // Mover la galaxia seleccionada al centro con efecto dramático
        const targetX = window.innerWidth / 2 - galaxyElement.offsetLeft - galaxyElement.offsetWidth / 2;
        const targetY = window.innerHeight / 2 - galaxyElement.offsetTop - galaxyElement.offsetHeight / 2;
        
        gsap.to(galaxyElement, {
            x: targetX,
            y: targetY,
            scale: 2.5,
            duration: 1.5,
            ease: "power2.out",
            onComplete: () => {
                // Mostrar panel de información con animación
                infoPanel.classList.add('info-panel-visible');
                gsap.to(infoContent.parentElement, {
                    scale: 1,
                    duration: 0.8,
                    ease: "elastic.out(1, 0.5)",
                    onComplete: () => {
                        isAnimating = false;
                    }
                });
                
                // Efecto de partículas hacia la galaxia
                createParticleExplosion(galaxyElement, galaxy.color);
            }
        });
        
        // Animación del hoyo negro
        gsap.to(blackHole, {
            scale: 0.7,
            opacity: 0.6,
            duration: 1
        });
    }
    
    // Efecto de partículas al seleccionar galaxia
    function createParticleExplosion(sourceElement, color) {
        for (let i = 0; i < 100; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.backgroundColor = color;
            particle.style.width = `${2 + Math.random() * 5}px`;
            particle.style.height = particle.style.width;
            particle.style.position = 'absolute';
            particle.style.borderRadius = '50%';
            particle.style.pointerEvents = 'none';
            particle.style.zIndex = '15';
            particle.style.filter = 'blur(1px)';
            
            const startX = sourceElement.offsetLeft + sourceElement.offsetWidth / 2;
            const startY = sourceElement.offsetTop + sourceElement.offsetHeight / 2;
            
            particle.style.left = `${startX}px`;
            particle.style.top = `${startY}px`;
            
            container.appendChild(particle);
            
            const angle = Math.random() * Math.PI * 2;
            const distance = 100 + Math.random() * 200;
            const duration = 0.8 + Math.random() * 1.2;
            
            gsap.to(particle, {
                x: Math.cos(angle) * distance,
                y: Math.sin(angle) * distance,
                opacity: 0,
                scale: 0.1,
                duration: duration,
                ease: "power3.out",
                onComplete: () => {
                    particle.remove();
                }
            });
        }
    }
    
    // Mostrar información del hoyo negro ultra mejorada
    function showUltimateBlackHoleInfo() {
        if (isAnimating) return;
        isAnimating = true;
        
        currentGalaxy = null;
        infoContent.innerHTML = blackHoleContent;
        tryButton.href = '#';
        tryButton.style.background = 'linear-gradient(135deg, #7C3AED, #4F46E5)';
        
        // Efecto de succión mejorado
        const allGalaxies = document.querySelectorAll('.galaxy');
        
        allGalaxies.forEach(g => {
            const targetX = blackHole.offsetLeft - g.offsetLeft + blackHole.offsetWidth / 2;
            const targetY = blackHole.offsetTop - g.offsetTop + blackHole.offsetHeight / 2;
            
            gsap.to(g, {
                x: targetX,
                y: targetY,
                scale: 0.1,
                opacity: 0,
                duration: 1.5,
                ease: "power2.in",
                overwrite: true
            });
        });
        
        // Animación del hoyo negro mejorada
        gsap.to(blackHole, {
            scale: 1.3,
            duration: 1,
            ease: "elastic.out(1, 0.5)",
            onComplete: () => {
                // Mostrar panel de información con animación
                infoPanel.classList.add('info-panel-visible');
                gsap.to(infoContent.parentElement, {
                    scale: 1,
                    duration: 0.8,
                    ease: "elastic.out(1, 0.5)",
                    onComplete: () => {
                        isAnimating = false;
                    }
                });
                
                // Efecto de ondas concéntricas mejorado
                createBlackHoleRipple();
            }
        });
    }
    
    // Efecto de ondas del hoyo negro mejorado
    function createBlackHoleRipple() {
        for (let i = 0; i < 8; i++) {
            const ripple = document.createElement('div');
            ripple.className = 'absolute rounded-full border-2 border-purple-500 opacity-0';
            ripple.style.width = '0px';
            ripple.style.height = '0px';
            ripple.style.left = `${blackHole.offsetLeft + blackHole.offsetWidth / 2}px`;
            ripple.style.top = `${blackHole.offsetTop + blackHole.offsetHeight / 2}px`;
            ripple.style.transform = 'translate(-50%, -50%)';
            ripple.style.pointerEvents = 'none';
            ripple.style.zIndex = '10';
            
            container.appendChild(ripple);
            
            gsap.to(ripple, {
                width: '2000px',
                height: '2000px',
                opacity: 0.4,
                duration: 3,
                delay: i * 0.4,
                ease: "power2.out",
                onComplete: () => {
                    ripple.remove();
                }
            });
        }
    }
    
    // Ocultar panel de información ultra mejorado
    function hideUltimateInfoPanel() {
        if (isAnimating) return;
        isAnimating = true;
        
        // Animación de salida del panel
        gsap.to(infoContent.parentElement, {
            scale: 0.95,
            duration: 0.5,
            ease: "power2.in"
        });
        
        gsap.to(infoPanel, {
            opacity: 0,
            duration: 0.5,
            onComplete: () => {
                infoPanel.classList.remove('info-panel-visible');
            }
        });
        
        // Restaurar galaxias a sus posiciones originales
        galaxyPositions.forEach((pos, index) => {
            gsap.to(pos.element, {
                x: 0,
                y: 0,
                scale: 1,
                opacity: 1,
                duration: 1.5,
                delay: index * 0.05,
                ease: "elastic.out(1, 0.5)",
                overwrite: true,
                onComplete: index === galaxyPositions.length - 1 ? () => {
                    isAnimating = false;
                } : null
            });
        });
        
        // Restaurar hoyo negro
        gsap.to(blackHole, {
            scale: 1,
            opacity: 1,
            duration: 0.8,
            ease: "back.out(2)"
        });
    }
    
    // Manejar redimensionamiento ultra mejorado
    function handleUltimateResize() {
        // Actualizar Three.js
        if (threeJSCamera && threeJSRenderer) {
            threeJSCamera.aspect = window.innerWidth / window.innerHeight;
            threeJSCamera.updateProjectionMatrix();
            threeJSRenderer.setSize(window.innerWidth, window.innerHeight);
        }
        
        // Reposicionar estrellas fugaces
        shootingStars.forEach(star => {
            star.style.left = `${-100}px`;
            star.style.top = `${Math.random() * window.innerHeight * 0.5}px`;
        });
    }
    
    // Función para aclarar colores
    function lightenColor(color, percent) {
        const num = parseInt(color.replace("#", ""), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) + amt;
        const G = (num >> 8 & 0x00FF) + amt;
        const B = (num & 0x0000FF) + amt;
        
        return `#${(
            0x1000000 +
            (R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000 +
            (G < 255 ? (G < 1 ? 0 : G) : 255) * 0x100 +
            (B < 255 ? (B < 1 ? 0 : B) : 255)
        ).toString(16).slice(1)}`;
    }
});

