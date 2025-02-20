// Sayfa yüklendiğinde
window.onload = function() {
    const increaseButton = document.querySelector('button[name="action"][value="increase"]');
    const decreaseButton = document.querySelector('button[name="action"][value="decrease"]');
    const waterLevel = document.querySelector('.water');
    const currentIntakeDisplay = document.getElementById('current-intake');
    const goalDisplay = document.getElementById('daily-goal');

    let currentIntake = parseInt(currentIntakeDisplay.innerText); // Başlangıç içilen su
    const dailyGoal = parseInt(goalDisplay.innerText); // Hedef

    // Şişedeki su seviyesini hesapla
    function updateWaterLevel() {
        const percentage = (currentIntake / dailyGoal) * 100;
        waterLevel.style.height = percentage + '%';

        // Hedef tamamlandığında yeşil göster
        if (currentIntake >= dailyGoal) {
            waterLevel.style.backgroundColor = '#32CD32'; // Yeşil
        } else {
            waterLevel.style.backgroundColor = '#00bfff'; // Mavi
        }
    }

    // Artırma butonuna tıklama
    increaseButton.addEventListener('click', function(event) {
        event.preventDefault();
        currentIntake += 100;
        currentIntakeDisplay.innerText = currentIntake;
        updateWaterLevel();
    });

    // Azaltma butonuna tıklama
    decreaseButton.addEventListener('click', function(event) {
        event.preventDefault();
        currentIntake -= 100;
        currentIntakeDisplay.innerText = currentIntake;
        updateWaterLevel();
    });

    // Başlangıçta su seviyesini ayarla
    updateWaterLevel();
};
