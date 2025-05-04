document.addEventListener("DOMContentLoaded", function() {
    // Existing variable declarations
    let bioA = document.querySelector(".bio-a");
    let chemA = document.querySelector(".chem-a");
    let phyA = document.querySelector(".phy-a");
    let engA = document.querySelector(".eng-a");
    let lrA = document.querySelector(".lr-a");
    let tA = document.querySelector(".t-a");

    let bioB = document.querySelector(".bio-b");
    let chemB = document.querySelector(".chem-b");
    let phyB = document.querySelector(".phy-b");
    let engB = document.querySelector(".eng-b");
    let lrB = document.querySelector(".lr-b");
    let tB = document.querySelector(".t-b");

    let biobar = document.querySelector(".biobar");
    let chembar = document.querySelector(".chembar");
    let phybar = document.querySelector(".phybar");
    let engbar = document.querySelector(".engbar");
    let lrbar = document.querySelector(".lrbar");
    let tbar = document.querySelector(".tbar");

    let percBio = document.querySelector(".perc-bio");
    let percChem = document.querySelector(".perc-chem");
    let percPhy = document.querySelector(".perc-phy");
    let percEng = document.querySelector(".perc-eng");
    let percLr = document.querySelector(".perc-lr");
    let percT = document.querySelector(".perc-t");
    let remarks = document.querySelector(".remarks");

    // Compliment messages based on percentage ranges
    const compliments = [
        { min: 0, max: 30, message: "Keep practicing! You'll improve with more effort." },
        { min: 31, max: 50, message: "Good attempt! Focus on weak areas for better results." },
        { min: 51, max: 70, message: "Well done! You're making good progress." },
        { min: 71, max: 85, message: "Excellent work! You're performing really well." },
        { min: 86, max: 95, message: "Outstanding! You're mastering the material." },
        { min: 96, max: 100, message: "Perfect! You're at the top of your game!" }
    ];

    // Function to update remarks based on percentage
    function updateRemarks(percentage) {
        const foundCompliment = compliments.find(c => percentage >= c.min && percentage <= c.max);
        remarks.textContent = foundCompliment ? foundCompliment.message : "Analyzing your performance...";
    }

    // Modified updateTBar function to include remarks update
    function updateTBar() {
        let valueA = parseFloat(tA.textContent) || 0;
        let valueB = parseFloat(tB.textContent) || 1;
        let percentage = (valueA / valueB) * 100;
        percentage = Math.min(Math.max(percentage, 0), 100);
        
        tbar.style.width = percentage + "%";
        percT.textContent = percentage.toFixed(1) + "%";
        updateRemarks(percentage); // Update the remarks
    }

    // Existing update functions (unchanged)
    function updateBioBar() {
        let valueA = parseFloat(bioA.textContent) || 0;
        let valueB = parseFloat(bioB.textContent) || 1;
        let percentage = (valueA / valueB) * 100;
        percentage = Math.min(Math.max(percentage, 0), 100);
        biobar.style.width = percentage + "%";
        percBio.textContent = percentage.toFixed(1) + "%";
    }

    function updateChemBar() {
        let valueA = parseFloat(chemA.textContent) || 0;
        let valueB = parseFloat(chemB.textContent) || 1;
        let percentage = (valueA / valueB) * 100;
        percentage = Math.min(Math.max(percentage, 0), 100);
        chembar.style.width = percentage + "%";
        percChem.textContent = percentage.toFixed(1) + "%";
    }

    function updatePhyBar() {
        let valueA = parseFloat(phyA.textContent) || 0;
        let valueB = parseFloat(phyB.textContent) || 1;
        let percentage = (valueA / valueB) * 100;
        percentage = Math.min(Math.max(percentage, 0), 100);
        phybar.style.width = percentage + "%";
        percPhy.textContent = percentage.toFixed(1) + "%";
    }

    function updateEngBar() {
        let valueA = parseFloat(engA.textContent) || 0;
        let valueB = parseFloat(engB.textContent) || 1;
        let percentage = (valueA / valueB) * 100;
        percentage = Math.min(Math.max(percentage, 0), 100);
        engbar.style.width = percentage + "%";
        percEng.textContent = percentage.toFixed(1) + "%";
    }

    function updateLrBar() {
        let valueA = parseFloat(lrA.textContent) || 0;
        let valueB = parseFloat(lrB.textContent) || 1;
        let percentage = (valueA / valueB) * 100;
        percentage = Math.min(Math.max(percentage, 0), 100);
        lrbar.style.width = percentage + "%";
        percLr.textContent = percentage.toFixed(1) + "%";
    }

    function updateTotalA() {
        let bioA = parseFloat(document.querySelector(".bio-a").innerText) || 0;
        let phyA = parseFloat(document.querySelector(".phy-a").innerText) || 0;
        let chemA = parseFloat(document.querySelector(".chem-a").innerText) || 0;
        let engA = parseFloat(document.querySelector(".eng-a").innerText) || 0;
        let lrA = parseFloat(document.querySelector(".lr-a").innerText) || 0;
        let totalA = bioA + phyA + chemA + engA + lrA;
        document.querySelector(".t-a").textContent = totalA;
    }

    function updateTotalB() {
        let phyB = parseFloat(document.querySelector(".phy-b").innerText) || 0;
        let bioB = parseFloat(document.querySelector(".bio-b").innerText) || 0;
        let chemB = parseFloat(document.querySelector(".chem-b").innerText) || 0;
        let engB = parseFloat(document.querySelector(".eng-b").innerText) || 0;
        let lrB = parseFloat(document.querySelector(".lr-b").innerText) || 0;
        let totalB = bioB + phyB + chemB + engB + lrB;
        document.querySelector(".t-b").textContent = totalB;
    }

    // Optimization: Single update function that calls all others
    function updateAll() {
        updateBioBar();
        updateChemBar();
        updatePhyBar();
        updateEngBar();
        updateLrBar();
        updateTotalA();
        updateTotalB();
        updateTBar();
    }

    // Initial update
    updateAll();

    // Set interval for updates (optimized to update all at once)
    setInterval(updateAll, 500);
});