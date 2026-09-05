document.addEventListener('DOMContentLoaded', function() {
    console.log("Mandi AI: Script loaded");

    const predictBtn = document.getElementById('predict-btn');
    const resultsArea = document.getElementById('results-area');
    const statusMsg = document.getElementById('status-msg');
    let forecastChart = null;

    if (!predictBtn) {
        console.error('Predict button not found in DOM!');
        return;
    }

    // Load initial defaults from config
    fetch('/api/config')
        .then(res => {
            return res.json();
        })
        .then(data => {
            document.getElementById('state').value = data.state || '';
            document.getElementById('district').value = data.district || '';
            document.getElementById('mandi').value = data.mandi || '';
            document.getElementById('commodity').value = data.commodity || '';
        })
        .catch(err => console.error('Config fetch failed', err));

    predictBtn.addEventListener('click', function() {
        const payload = {
            state: document.getElementById('state').value,
            district: document.getElementById('district').value,
            mandi: document.getElementById('mandi').value,
            commodity: document.getElementById('commodity').value,
            days: document.getElementById('duration').value
        };

        if (!payload.state || !payload.district || !payload.mandi || !payload.commodity) {
            alert('Please fill all fields.');
            return;
        }

        predictBtn.disabled = true;
        predictBtn.textContent = 'Processing...';
        statusMsg.textContent = 'Fetching 3-year history and analyzing variety...';
        resultsArea.classList.add('hidden');

        fetch('/api/market/details', {
            method: 'POST',
            mode: 'cors', // Explicitly set CORS mode
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(response => {
            return response.json();
        })
        .then(data => {
            if (data.ok) {
                statusMsg.textContent = '✓ Forecast generated successfully!';
                renderDashboard(data.details);
                resultsArea.classList.remove('hidden');
                resultsArea.scrollIntoView({ behavior: 'smooth' });
            } else {
                statusMsg.textContent = '';
                alert('Error: ' + data.message);
            }
        })
        .catch(err => {
            console.error('Network/Pipeline crash', err);
            statusMsg.textContent = '';
            alert('Pipeline execution failed. Check terminal for details.');
        })
        .finally(() => {
            predictBtn.disabled = false;
            predictBtn.textContent = 'Predict Next 30 Days';
        });
    });

    function renderDashboard(data) {
        // Ensuring all fields match the backend response keys exactly
        const price = data.latest_price || data.latest_actual_price || '--';
        document.getElementById('latest-price').textContent = '₹' + price;
        document.getElementById('variety-label').textContent = 'प्रकार (Variety): ' + (data.variety || 'Standard');

        // Standardized Accuracy Calculation (100 - MAPE)
        const mape = parseFloat(data.accuracy);
        const accuracy = !isNaN(mape) ? (100 - mape).toFixed(1) : '--';
        document.getElementById('mae-val').textContent = accuracy + '%';

        document.getElementById('model-name').textContent = data.source === 'live_api' ? 'Real-time AI' : 'Saved Model';

        // Render Live Rates provided by the backend response
        if (data.live_rates && data.live_rates.length > 0) {
            renderMarketRows(data.live_rates, data.live_level);
        }

        // Update forecast title
        const forecastDays = data.forecast.length;
        const chartTitle = document.querySelector('.chart-card h3');
        if (chartTitle) chartTitle.textContent = `Price Forecast (Next ${forecastDays} Days)`;

        // Weather update
        if (data.weather) {
            const weatherDescEl = document.getElementById('weather-desc');
            const weatherPrecipEl = document.getElementById('weather-precip');
            const weatherCard = document.getElementById('weather-card');

            weatherDescEl.textContent = data.weather.description;

            // Note: weather data structure might vary, ensure safe access
            const precip = data.weather.precipitation_sum || '0.0';
            weatherPrecipEl.textContent = `Total 7-day Rain: ${precip} mm`;

            let icon = "☀️";
            if (precip > 20) icon = "⛈️";
            else if (precip > 5) icon = "🌦️";

            const title = weatherCard.querySelector('h3');
            title.innerHTML = `<span>${icon}</span> Weather Impact`;
        }

        const trendEl = document.getElementById('trend-val');
        trendEl.textContent = data.trend === 'Upward' ? 'तेजी (Upward)' : (data.trend === 'Downward' ? 'मंदी (Downward)' : 'स्थिर (Stable)');
        trendEl.className = 'trend-val trend-' + data.trend.toLowerCase();

        // Update coverage info
        if (data.history && data.history.length > 0) {
            const start = data.history[0].date;
            const end = data.history[data.history.length - 1].date;
            document.getElementById('coverage-info').textContent = `📊 विश्लेषण: ${data.history.length} रिकॉर्ड्स (${start} से ${end})`;
        }

        const tbody = document.querySelector('#forecast-table tbody');
        tbody.innerHTML = '';
        data.forecast.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${row.date}</td><td>₹${row.predicted_price}</td>`;
            tbody.appendChild(tr);
        });

        renderChart(data.history, data.forecast);
    }

    function renderChart(history, forecast) {
        const ctx = document.getElementById('forecastChart').getContext('2d');
        if (forecastChart) forecastChart.destroy();

        const formatDate = (dateStr) => {
            const d = new Date(dateStr);
            return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
        };

        const labels = [...history.map(h => formatDate(h.date)), ...forecast.map(f => formatDate(f.date))];

        // Data sets
        const historyPrices = history.map(h => h.price);
        const forecastPrices = forecast.map(f => f.predicted_price);

        // We want the forecast line to start from the last historical point
        const historyData = [...historyPrices, ...forecastPrices.map(() => null)];
        const forecastData = [
            ...historyPrices.map((_, i) => i === historyPrices.length - 1 ? historyPrices[i] : null),
            ...forecastPrices
        ];

        forecastChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Historical Price',
                        data: historyData,
                        borderColor: '#2e7d32',
                        backgroundColor: 'rgba(46, 125, 50, 0.1)',
                        fill: true,
                        tension: 0.1,
                        pointRadius: 1
                    },
                    {
                        label: `${forecast.length}-Day Forecast`,
                        data: forecastData,
                        borderColor: '#d32f2f',
                        borderDash: [5, 5],
                        fill: false,
                        tension: 0.4,
                        pointRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: { mode: 'index', intersect: false },
                    legend: { position: 'top' }
                },
                scales: {
                    x: {
                        ticks: { maxRotation: 45, minRotation: 45, autoSkip: true, maxTicksLimit: 15 }
                    },
                    y: {
                        beginAtZero: false,
                        title: { display: true, text: 'Price (₹/Quintal)' }
                    }
                }
            }
        });
    }

    // --- LIVE PRICE DASHBOARD (UNIFIED BACKEND SOURCE) ---
    const liveContainer = document.getElementById('live-price-container');
    const sourceBadge = document.getElementById('mandi-source-badge');

    function renderMarketRows(records, levelName) {
        if (sourceBadge) {
            sourceBadge.textContent = levelName;
            sourceBadge.style.background = levelName === "Mandi Match" ? "#eaf7ed" : "#fff1e8";
            sourceBadge.style.color = levelName === "Mandi Match" ? "#2e7d32" : "#f59e0b";
        }

        const hindiMap = {
            'Wheat': 'गेहूं', 'Rice': 'चावल', 'Potato': 'आलू',
            'Onion': 'प्याज', 'Mustard': 'सरसों', 'Tomato': 'टमाटर',
            'Maize': 'मक्का', 'Paddy(Dhan)(Common)': 'धान', 'Cotton': 'कपास'
        };

        liveContainer.innerHTML = '';
        records.slice(0, 6).forEach(item => {
            const commName = item.Commodity || item.commodity || 'Unknown';
            const hindiName = hindiMap[commName] || commName;
            const modalPrice = parseFloat(item.Modal_Price || item.modal_price || 0);
            const pricePerKg = (modalPrice / 100).toFixed(2);
            const marketName = item.Market || item.market || 'Regional';
            const dateVal = item.Arrival_Date || item.arrival_date || 'Today';

            const row = document.createElement('div');
            row.className = 'market-row';
            row.innerHTML = `
                <b>${hindiName} <small>(${marketName})</small></b>
                <span class="rate">₹${pricePerKg} / किलो</span>
                <span class="trend-indicator" style="color: #2e7d32; font-size: 0.7rem; font-weight:normal">
                    ${dateVal}
                </span>
            `;
            liveContainer.appendChild(row);
        });
    }

    function showNoData() {
        if (sourceBadge) {
            sourceBadge.textContent = "डेटा अनुपलब्ध";
            sourceBadge.style.background = "#f1f5f9";
            sourceBadge.style.color = "#64748b";
        }
        liveContainer.innerHTML = '<div class="live-placeholder">बाज़ार भाव लोड नहीं हो पाए। इंटरनेट या डेटा अपडेट चेक करें।</div>';
    }

    // --- DASHBOARD WEATHER (JS FETCH) ---
    async function fetchWeatherForDashboard() {
        const weatherEl = document.getElementById('dashboard-weather');
        if (!weatherEl) return;

        const city = document.getElementById('district').value || document.getElementById('state').value || "Lucknow";

        try {
            // Step 1: Geocoding
            const geoRes = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1&language=en&format=json`);
            const geoData = await geoRes.json();

            if (geoData.results && geoData.results.length > 0) {
                const { latitude, longitude, name } = geoData.results[0];

                // Step 2: Forecast
                const wRes = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current_weather=true`);
                const wData = await wRes.json();

                if (wData.current_weather) {
                    const temp = wData.current_weather.temperature;
                    const code = wData.current_weather.weathercode;
                    let icon = "☀️";
                    if (code > 50) icon = "🌧️";
                    else if (code > 0) icon = "☁️";

                    weatherEl.innerHTML = `${icon} ${name}: ${temp}°C (Live)`;
                }
            } else {
                weatherEl.textContent = "🌤️ मौसम: जानकारी उपलब्ध नहीं";
            }
        } catch (err) {
            weatherEl.textContent = "🌤️ मौसम: लोड करने में समस्या";
        }
    }

    // Initial fetch
    fetchWeatherForDashboard();

    // Auto-refresh
    setInterval(() => {
        fetchWeatherForDashboard();
    }, 120000);
});
});
