class SpinningWheel {
    constructor(canvas, categories) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.categories = categories;
        this.rotation = 0;
        this.isSpinning = false;
        this.audio = new Audio('/static/spin-sound.mp3');
        this.lastTime = null; // To track time between frames
        this.lastRotation = 0; // To calculate angular velocity
        this.minInterval = 50; // Minimum interval (ms) between sounds
        this.lastSoundTime = 0; // Time when the last sound was played
    }

    draw() {
        const ctx = this.ctx;
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const radius = Math.min(centerX, centerY) - 10;

        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        const sliceAngle = (2 * Math.PI) / this.categories.length;

        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate(this.rotation);

        this.categories.forEach((category, i) => {
            const startAngle = i * sliceAngle;
            const endAngle = startAngle + sliceAngle;

            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.arc(0, 0, radius, startAngle, endAngle);
            ctx.closePath();

            ctx.fillStyle = category.color;
            ctx.fill();
            ctx.stroke();

            // Draw text
            ctx.save();
            ctx.rotate(startAngle + sliceAngle / 2);
            ctx.textAlign = 'right';
            ctx.fillStyle = '#000000';
            ctx.font = '16px Arial';
            ctx.fillText(category.name, radius - 20, 0);
            ctx.restore();
        });

        ctx.restore();
    }

    spin() {
        if (this.isSpinning) return;

        this.isSpinning = true;
        this.lastTime = performance.now();
        this.lastRotation = this.rotation;
        const spinDuration = 5000; // 5 seconds
        const startRotation = this.rotation;
        const additionalRotation = 360 * 5 + Math.random() * 360; // 5+ full rotations
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / spinDuration, 1);

            // Easing function for smooth deceleration
            const easeOut = (t) => 1 - Math.pow(1 - t, 3);

            this.rotation = startRotation + (additionalRotation * easeOut(progress) * Math.PI / 180);

            this.playAudioInTime(currentTime); // Play sound based on velocity
            this.draw();

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                this.isSpinning = false;
                const selectedIndex = Math.floor(
                    (this.rotation % (2 * Math.PI)) / (2 * Math.PI / this.categories.length)
                );
                const selected = this.categories[selectedIndex];
                // Create and show the winner popup
                const existingPopup = document.querySelector('.winner-popup');
                if (existingPopup) {
                    existingPopup.remove();
                }
                
                const popup = document.createElement('div');
                popup.className = 'winner-popup';
                
                const winnerText = document.createElement('p');
                winnerText.className = 'winner-text';
                winnerText.textContent = selected.name;
                
                popup.appendChild(winnerText);
                document.body.appendChild(popup);
                
                // After 3 seconds, fade out and remove the popup
                setTimeout(() => {
                    popup.style.opacity = '0';
                    popup.style.transition = 'opacity 0.5s ease-out';
                    setTimeout(() => popup.remove(), 500);
                }, 3000);
            }
        };

        requestAnimationFrame(animate);
    }

    playAudioInTime(currentTime) {
        const deltaTime = currentTime - this.lastTime;
        const deltaRotation = this.rotation - this.lastRotation;

        // Angular velocity: radians per second
        const angularVelocity = Math.abs(deltaRotation / deltaTime) * 1000;

        // Map angular velocity to an interval for playing sounds
        const interval = Math.max(this.minInterval, 1000 / angularVelocity);

        if (currentTime - this.lastSoundTime > interval) {
            this.audio.play();
            this.lastSoundTime = currentTime;
        }

        // Update for next frame
        this.lastTime = currentTime;
        this.lastRotation = this.rotation;
    }
}

// Initialize wheel when page loads
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('wheel-canvas');
    const categories = JSON.parse(document.getElementById('categories-data').textContent);
    const wheel = new SpinningWheel(canvas, categories);
    wheel.draw();

    document.getElementById('spin-button').addEventListener('click', () => {
        wheel.spin();
    });
});
