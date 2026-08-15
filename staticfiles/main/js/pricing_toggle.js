document.addEventListener("DOMContentLoaded", function() {
    const btnNpr = document.getElementById("btn-npr");
    const btnUsd = document.getElementById("btn-usd");
    const priceCols = document.querySelectorAll(".price-col");
    
    let exchangeRate = 0.0075; // Fallback rate (1 NPR = 0.0075 USD)

    // Fetch live exchange rate
    fetch('https://open.er-api.com/v6/latest/NPR')
      .then(res => res.json())
      .then(data => {
        if (data && data.rates && data.rates.USD) {
          exchangeRate = data.rates.USD;
        }
        processPrices();
      })
      .catch(err => {
        console.error("Failed to fetch exchange rate:", err);
        processPrices(); // Process with fallback
      });

    function processPrices() {
      priceCols.forEach(col => {
        const rawText = col.getAttribute('data-raw-price');
        if (!rawText) return;
        
        // Find numbers (with optional commas) and convert them to USD
        const usdText = rawText.replace(/\d[\d,]*/g, match => {
          let num = parseInt(match.replace(/,/g, ''));
          let converted = Math.round(num * exchangeRate);
          return '$' + converted.toLocaleString();
        });
        
        // Format NPR with Rupee sign
        const nprText = rawText.replace(/\d[\d,]*/g, match => {
          return 'रु ' + match;
        });
        
        col.setAttribute('data-usd-price', usdText);
        col.setAttribute('data-npr-price', nprText);
        
        // Update display to NPR by default
        const display = col.querySelector('.price-display');
        if (display) display.textContent = nprText;
      });
    }

    btnNpr.addEventListener("click", function() {
      btnNpr.style.background = "rgba(14,90,79,0.1)";
      btnNpr.classList.remove("text-muted");
      btnUsd.style.background = "transparent";
      btnUsd.classList.add("text-muted");
      
      priceCols.forEach(col => {
        const display = col.querySelector('.price-display');
        const npr = col.getAttribute('data-npr-price');
        if (display && npr) display.textContent = npr;
      });
    });

    btnUsd.addEventListener("click", function() {
      btnUsd.style.background = "rgba(14,90,79,0.1)";
      btnUsd.classList.remove("text-muted");
      btnUsd.style.color = "var(--cf-primary-dark)";
      btnNpr.style.background = "transparent";
      btnNpr.classList.add("text-muted");
      btnNpr.style.color = "";
      
      priceCols.forEach(col => {
        const display = col.querySelector('.price-display');
        const usd = col.getAttribute('data-usd-price');
        if (display && usd) display.textContent = usd;
      });
    });
  });