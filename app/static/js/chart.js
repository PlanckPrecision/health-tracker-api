// Theme tokens — must stay in sync with tailwind.config in base.html
const THEME = {
    primary:                  '#47eaed',
    surface:                  '#121416',
    surfaceContainer:         '#1e2022',
    surfaceContainerHighest:  '#333537',
    outlineVariant:           '#3b4949',
    onSurface:                '#e2e2e5',
    error:                    '#ff5252',
};

const parseDate = str => {
    const [d, m, y] = str.split('.');
    return new Date(+y, +m - 1, +d);
};

// Exponential Moving Average — weights recent entries more than older ones.
// alpha controls responsiveness: 0.2 = smooth, 0.4 = more reactive.
// This cuts through daily noise (water weight, salt spikes) better than SMA.
const buildEma = (weights, alpha = 0.3) => {
    if (weights.length === 0) return [];
    const ema = [weights[0]];
    for (let i = 1; i < weights.length; i++) {
        ema.push(+(alpha * weights[i] + (1 - alpha) * ema[i - 1]).toFixed(2));
    }
    return ema;
};

const formatDate = date => {
    const d = String(date.getDate()).padStart(2, '0');
    const m = String(date.getMonth() + 1).padStart(2, '0');
    return `${d}.${m}.${date.getFullYear()}`;
};

// Mirrors the Intelligent Forecasting logic from validate.py:
// projects weekly steps using weeklyPace (kg/week, negative = losing),
// starting from the last recorded weight.
// Stops when the goal is crossed or after 26 weeks.
const buildForecast = (dates, weights, weeklyPace, goalWeight) => {
    if (weeklyPace === null) return { futureLabels: [], futureWeights: [] };

    const lastWeight = weights[weights.length - 1];
    const lastDate   = parseDate(dates[dates.length - 1]);
    const MAX_WEEKS  = 26;

    const futureLabels  = [];
    const futureWeights = [];

    for (let w = 1; w <= MAX_WEEKS; w++) {
        const projected = +(lastWeight + weeklyPace * w).toFixed(2);

        const futureDate = new Date(lastDate);
        futureDate.setDate(lastDate.getDate() + w * 7);
        futureLabels.push(formatDate(futureDate));
        futureWeights.push(projected);

        if (goalWeight !== null) {
            if (weeklyPace < 0 && projected <= goalWeight) break;
            if (weeklyPace > 0 && projected >= goalWeight) break;
        }
    }

    return { futureLabels, futureWeights };
};

document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('weightChart');
    if (!canvas) return;

    const goalRaw          = canvas.dataset.goal;
    const paceRaw          = canvas.dataset.weeklyPace;
    const committedPaceRaw = canvas.dataset.committedPace;
    const goalWeight       = goalRaw          !== '' && !isNaN(+goalRaw)          ? +goalRaw          : null;
    const weeklyPace       = paceRaw          !== '' && !isNaN(+paceRaw)          ? +paceRaw          : null;
    // committedPace is kg/week (positive number); negate it to match the convention
    // that weeklyPace < 0 means losing weight.
    const committedPace    = committedPaceRaw !== '' && !isNaN(+committedPaceRaw) ? -(+committedPaceRaw) : null;

    fetch('/api/entries')
        .then(r => r.json())
        .then(data => {
            if (data.length === 0) {
                canvas.parentElement.innerHTML =
                    `<div class="flex items-center justify-center h-full text-slate-500 text-sm">No entries yet — log your first weight to see the chart.</div>`;
                return;
            }

            const dates   = data.map(e => e.date);
            const weights = data.map(e => e.weight);
            const emaData = buildEma(weights);

            // Use the committed-rate pace for the forecast line when set;
            // fall back to the actual weekly pace extrapolation.
            const forecastPace = committedPace !== null ? committedPace : weeklyPace;
            const { futureLabels, futureWeights } = buildForecast(dates, weights, forecastPace, goalWeight);

            // allLabels includes future dates; chart starts with historical only
            const allLabels = [...dates, ...futureLabels];

            // Historical dataset has no trailing nulls initially — labels match 1:1
            const historicalData = weights.slice();

            // Forecast dataset: nulls for all historical slots except the last
            // (join point for visual continuity), then projected values
            const forecastData = [
                ...Array(weights.length - 1).fill(null),
                weights[weights.length - 1],
                ...futureWeights,
            ];

            const ctx = canvas.getContext('2d');

            const gradient = ctx.createLinearGradient(0, 0, 0, canvas.offsetHeight || 300);
            gradient.addColorStop(0,   'rgba(71, 234, 237, 0.18)');
            gradient.addColorStop(0.6, 'rgba(71, 234, 237, 0.04)');
            gradient.addColorStop(1,   'rgba(71, 234, 237, 0)');

            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    // Start with historical labels only; expand on forecast toggle
                    labels: dates,
                    datasets: [
                        {
                            label: 'Weight (kg)',
                            data: historicalData,
                            borderColor: THEME.primary,
                            backgroundColor: gradient,
                            borderWidth: 2,
                            pointRadius: 4,
                            pointHoverRadius: 6,
                            pointBackgroundColor: THEME.surface,
                            pointBorderColor: THEME.primary,
                            pointBorderWidth: 2,
                            tension: 0.4,
                            fill: true,
                            spanGaps: false,
                        },
                        {
                            label: 'Trend (EMA)',
                            data: emaData,
                            borderColor: 'rgba(71, 234, 237, 0.35)',
                            backgroundColor: 'transparent',
                            borderWidth: 2,
                            borderDash: [4, 3],
                            pointRadius: 0,
                            pointHoverRadius: 0,
                            tension: 0.5,
                            fill: false,
                            spanGaps: false,
                        },
                        {
                            label: committedPace !== null ? 'Target Pace' : 'Forecast',
                            data: forecastData,
                            borderColor: 'rgba(71, 234, 237, 0.45)',
                            backgroundColor: 'transparent',
                            borderWidth: 2,
                            borderDash: [6, 4],
                            pointRadius: 3,
                            pointHoverRadius: 5,
                            pointBackgroundColor: THEME.surface,
                            pointBorderColor: 'rgba(71, 234, 237, 0.45)',
                            pointBorderWidth: 1.5,
                            tension: 0.3,
                            fill: false,
                            hidden: true,
                            spanGaps: false,
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: {
                            display: false,
                        },
                        tooltip: {
                            backgroundColor: THEME.surfaceContainer,
                            titleColor: THEME.onSurface,
                            bodyColor: THEME.primary,
                            borderColor: THEME.outlineVariant,
                            borderWidth: 1,
                            padding: 12,
                            displayColors: false,
                            callbacks: {
                                title: items => items[0].label,
                                label: item => {
                                    if (item.parsed.y === null) return null;
                                    if (item.datasetIndex === 1) return null; // hide EMA from tooltip
                                    const isTarget = committedPace !== null;
                                    const suffix = item.datasetIndex === 2
                                        ? (isTarget ? ' (target)' : ' (forecast)')
                                        : '';
                                    return `${item.parsed.y} kg${suffix}`;
                                },
                                filter: item => item.parsed.y !== null && item.datasetIndex !== 1,
                            },
                        },
                    },
                    scales: {
                        x: {
                            grid: {
                                color: `${THEME.outlineVariant}40`,
                                drawBorder: false,
                            },
                            ticks: {
                                color: '#64748b',
                                font: { family: 'Manrope', size: 11 },
                                maxTicksLimit: 8,
                            },
                        },
                        y: {
                            position: 'right',
                            beginAtZero: false,
                            grid: {
                                color: `${THEME.outlineVariant}40`,
                                drawBorder: false,
                            },
                            ticks: {
                                color: '#64748b',
                                font: { family: 'Manrope', size: 11 },
                                callback: v => `${v} kg`,
                            },
                        },
                    },
                },
            });

            // Forecast toggle: swap labels and show/hide forecast dataset
            const toggleBtn = document.getElementById('forecast-toggle');
            if (toggleBtn) {
                // Disable button if there's no pace data to project from
                if (forecastPace === null || futureLabels.length === 0) {
                    toggleBtn.disabled = true;
                    toggleBtn.title = 'Not enough data for a forecast yet';
                    toggleBtn.classList.add('opacity-40', 'cursor-not-allowed');
                }

                toggleBtn.addEventListener('click', () => {
                    if (toggleBtn.disabled) return;

                    const isActive = toggleBtn.getAttribute('aria-pressed') === 'true';
                    const forecastDataset = chart.data.datasets[2];

                    if (!isActive) {
                        // Expand x-axis to include future dates
                        chart.data.labels = allLabels;
                        forecastDataset.hidden = false;
                    } else {
                        // Collapse back to historical only
                        chart.data.labels = dates;
                        forecastDataset.hidden = true;
                    }

                    chart.update();

                    toggleBtn.setAttribute('aria-pressed', String(!isActive));
                    toggleBtn.classList.toggle('border-primary/50', !isActive);
                    toggleBtn.classList.toggle('text-primary', !isActive);
                    toggleBtn.classList.toggle('bg-primary/5', !isActive);
                    toggleBtn.classList.toggle('border-outline-variant/30', isActive);
                    toggleBtn.classList.toggle('text-slate-500', isActive);
                });
            }
        })
        .catch(err => {
            console.error('Chart fetch failed:', err);
            canvas.parentElement.innerHTML =
                `<div class="flex items-center justify-center h-full text-error text-sm">Failed to load chart data.</div>`;
        });
});
