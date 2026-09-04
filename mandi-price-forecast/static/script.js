document.addEventListener('DOMContentLoaded', function() {
    console.log("Mandi AI: Script loaded");

    const predictBtn = document.getElementById('predict-btn');
    const resultsArea = document.getElementById('results-area');
    const statusMsg = document.getElementById('status-msg');
    const debugLogs = document.getElementById('debug-logs');
    const clearLogsBtn = document.getElementById('clear-logs');
    let forecastChart = null;

    function logToUI(type, message, data = null) {
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        const timestamp = new Date().toLocaleTimeString();
        let text = `[${timestamp}] ${message}`;
        if (data) {
            text += `\n${JSON.stringify(data, null, 2)}`;
        }
        entry.textContent = text;
        debugLogs.appendChild(entry);
        console.log(`[${type.toUpperCase()}] ${message}`, data || "");
    }

    if (clearLogsBtn) {
        clearLogsBtn.addEventListener('click', () => {
            debugLogs.innerHTML = '';
            logToUI('system', 'Logs cleared.');
        });
    }

    if (!predictBtn) {
        logToUI('error', 'Predict button not found in DOM!');
        return;
    }

    logToUI('system', 'Application initialized. Fetching default config...');

    // Load initial defaults from config
    fetch('/api/config')
        .then(res => {
            logToUI('response', `GET /api/config -> ${res.status}`);
            return res.json();
        })
        .then(data => {
            logToUI('system', 'Config applied to form.', data);
            document.getElementById('state').value = data.state || '';
            document.getElementById('district').value = data.district || '';
            document.getElementById('mandi').value = data.mandi || '';
            document.getElementById('commodity').value = data.commodity || '';
        })
        .catch(err => logToUI('error', 'Config fetch failed', err));

    predictBtn.addEventListener('click', function() {
        const payload = {
            state: document.getElementById('state').value,
            district: document.getElementById('district').value,
            mandi: document.getElementById('mandi').value,
            commodity: document.getElementById('commodity').value
        };

        logToUI('request', 'POST /api/forecast initiated', payload);

        if (!payload.state || !payload.district || !payload.mandi || !payload.commodity) {
            logToUI('error', 'Validation failed: Missing fields');
            alert('Please fill all fields.');
            return;
        }

        predictBtn.disabled = true;
        predictBtn.textContent = 'Processing...';
        statusMsg.textContent = 'Fetching data and training model. This may take a minute...';
        resultsArea.classList.add('hidden');

        fetch('/api/forecast', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(response => {
            logToUI('response', `POST /api/forecast -> ${response.status} ${response.statusText}`);
            return response.json();
        })
        .then(data => {
            if (data.ok) {
                logToUI('system', 'Forecast pipeline successful', {
                    model: data.model,
                    mae: data.mae,
                    trend: data.trend,
                    records: data.history.length
                });
                statusMsg.textContent = 'Forecast generated successfully!';
                renderDashboard(data);
                resultsArea.classList.remove('hidden');
                resultsArea.scrollIntoView({ behavior: 'smooth' });
            } else {
                logToUI('error', 'Pipeline returned error', data.error);
                statusMsg.textContent = '';
                alert('Error: ' + data.error);
            }
        })
        .catch(err => {
            logToUI('error', 'Network/Pipeline crash', err.toString());
            statusMsg.textContent = '';
            alert('Pipeline execution failed. Check terminal for details.');
        })
        .finally(() => {
            predictBtn.disabled = false;
            predictBtn.textContent = 'Predict Next 30 Days';
        });
    });

    function renderDashboard(data) {
        document.getElementById('latest-price').textContent = '₹' + data.latest_actual_price;
        document.getElementById('variety-label').textContent = 'Variety: ' + (data.variety || 'Standard');
        document.getElementById('mae-val').textContent = '₹' + (data.mae || '--');
        document.getElementById('model-name').textContent = data.model;

        // Weather update
        if (data.weather) {
            const weatherDescEl = document.getElementById('weather-desc');
            const weatherPrecipEl = document.getElementById('weather-precip');
            const weatherCard = document.getElementById('weather-card');

            const precip = data.weather.data && data.weather.data.precipitation_sum ?
                           data.weather.data.precipitation_sum.reduce((a, b) => a + b, 0).toFixed(1) : '0.0';

            weatherDescEl.textContent = data.weather.description;
            weatherPrecipEl.textContent = `Total 7-day Rain: ${precip} mm`;

            let icon = "☀️";
            if (precip > 20) {
                icon = "⛈️";
                weatherCard.style.borderLeft = "5px solid #d32f2f";
                weatherCard.style.backgroundColor = "#fff5f5";
            } else if (precip > 5) {
                icon = "🌦️";
                weatherCard.style.borderLeft = "5px solid #ffa000";
                weatherCard.style.backgroundColor = "#fffaf0";
            } else {
                weatherCard.style.borderLeft = "5px solid #2e7d32";
                weatherCard.style.backgroundColor = "#f5fff5";
            }

            const title = weatherCard.querySelector('h3');
            title.innerHTML = `<span>${icon}</span> Weather Impact`;
        }

        const trendEl = document.getElementById('trend-val');
        trendEl.textContent = data.trend;
        trendEl.className = 'trend-val trend-' + data.trend.toLowerCase();

        // Update coverage info
        if (data.history && data.history.length > 0) {
            const start = data.history[0].date;
            const end = data.history[data.history.length - 1].date;
            document.getElementById('coverage-info').textContent = `📊 Analysis covering ${data.history.length} records from ${start} to ${end}`;
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

        const labels = [...history.map(h => h.date), ...forecast.map(f => f.date)];

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
                        label: '30-Day Forecast',
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
});
