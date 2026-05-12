let currentStep = 0;
let pollingInterval;

function startProcess() {
    document.getElementById("resetButton").disabled = true;

    const startButton = document.getElementById("startButton");
    const buttonText = startButton.querySelector('.button-text');
    const spinner = startButton.querySelector('.spinner');

    startButton.disabled = true;
    buttonText.textContent = "Processing...";
    spinner.classList.remove('hidden');

    fetch('/start_process', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            pollingInterval = setInterval(pollProgress, 4000);
        })
        .catch(err => {
            console.error('Error starting the process:', err);
            resetButton();
        });
}

function pollProgress() {
    fetch('/progress')
        .then(response => response.json())
        .then(data => {
            updateProgress(data);
            if (data.status === "Completed") {
                clearInterval(pollingInterval);
                document.getElementById("startButton").disabled = false;
                document.getElementById("resetButton").disabled = false;
                if (data.step === 5) {
                    resetButton();
                }
            }
        })
        .catch(err => {
            console.error('Error fetching progress:', err);
        });
}

function resetButton() {
    const startButton = document.getElementById("startButton");
    const buttonText = startButton.querySelector('.button-text');
    const spinner = startButton.querySelector('.spinner');

    startButton.disabled = false;
    buttonText.textContent = "Start";
    spinner.classList.add('hidden');
}

function updateProgress(data) {
    if (data.step > currentStep) {
        for (let i = currentStep + 1; i <= data.step; i++) {
            const stepElement = document.getElementById(`step${i}`);
            stepElement.classList.add("active");
            const content = stepElement.querySelector('.step-content');
            content.innerHTML = `Status: ${data.status}`;
        }
        currentStep = data.step;

        if (data.result) {
            const stepElement = document.getElementById(`step${currentStep}`);
            const content = stepElement.querySelector('.step-content');
            content.innerHTML += `<br>${data.result}`;
        }
        if (data.final_result && data.step === 5) {
            const stepElement = document.getElementById(`step5`);
            const content = stepElement.querySelector('.step-content');
            content.innerHTML += `<br>${data.final_result}`;
        }
    } else if (data.step === currentStep) {
        const stepElement = document.getElementById(`step${currentStep}`);
        const content = stepElement.querySelector('.step-content');
        content.innerHTML = `Status: ${data.status}`;
        if (data.result) {
            content.innerHTML += `<br>${data.result}`;
        }
    }
}

function resetProcess() {
    clearInterval(pollingInterval);
    currentStep = 0;
    document.getElementById("startButton").disabled = false;
    document.getElementById("resetButton").disabled = false;

    for (let i = 1; i <= 5; i++) {
        const stepElement = document.getElementById(`step${i}`);
        stepElement.classList.remove("active");
        const content = stepElement.querySelector('.step-content');
        content.innerHTML = '';
    }

    fetch('/reset', { method: 'POST' })
        .then(response => response.json())
        .then(data => console.log(data.message))
        .catch(err => console.error('Error resetting the process:', err));

    resetButton();
}
