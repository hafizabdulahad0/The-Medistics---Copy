document.addEventListener("DOMContentLoaded", function () {
    // Select all radio buttons and the map image
    const radioButtons = document.querySelectorAll('.radio-input');
    const mapImage = document.getElementById('mapImage');

    // Add event listener to each radio button
    radioButtons.forEach(radio => {
        radio.addEventListener('change', function () {
            // Check if the radio button is selected and update the image
            if (this.checked) {
                mapImage.src = this.getAttribute('data-map');
            }
        });
    });

    // Prevent script from running multiple times
    if (!window.radioButtonListenerAdded) {
        window.radioButtonListenerAdded = true;

        // Enable Continue button when a radio is selected
        const continueBtn = document.getElementById('no-id');
        const hearedRadios = document.querySelectorAll('input[name="heared"]');

        hearedRadios.forEach(radio => {
            radio.addEventListener('change', function () {
                continueBtn.disabled = false;
            });
        });
    }
});
