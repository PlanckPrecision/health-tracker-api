// Theme tokens — must stay in sync with tailwind.config in base.html
const THEME = {
    primary:        '#47eaed',
    surface:        '#121416',
    surfaceContainer: '#1e2022',
    surfaceContainerHighest: '#333537',
    outlineVariant: '#3b4949',
    onSurface:      '#e2e2e5',
    error:          '#ff5252',
};

document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('weightChart');
    if (!canvas) return;

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

            // Gradient fill: primary at top, transparent at bottom
            const ctx = canvas.getContext('2d');
            const gradient = ctx.createLinearGradient(0, 0, 0, canvas.offsetHeight || 300);
            gradient.addColorStop(0,   'rgba(71, 234, 237, 0.18)');
            gradient.addColorStop(0.6, 'rgba(71, 234, 237, 0.04)');
            gradient.addColorStop(1,   'rgba(71, 234, 237, 0)');

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Weight (kg)',
                        data: weights,
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
                    }]
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
                                label: item => `${item.parsed.y} kg`,
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
        })
        .catch(err => {
            console.error('Chart fetch failed:', err);
            canvas.parentElement.innerHTML =
                `<div class="flex items-center justify-center h-full text-error text-sm">Failed to load chart data.</div>`;
        });
});
