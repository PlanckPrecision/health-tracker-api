// Weight Chart - Fetches data from /api/entries and displays as a time series line chart
document.addEventListener('DOMContentLoaded', function() {
    const chartContainer = document.getElementById('weightChart');
    if (!chartContainer) return;

    // Fetch entries data from the API endpoint
    fetch('/api/entries')
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                chartContainer.innerHTML = '<p>No weight data available</p>';
                return;
            }

            // Parse dates and prepare data for the chart
            const dates = data.map(entry => entry.date);
            const weights = data.map(entry => entry.weight);

            // Create the chart
            const ctx = chartContainer.getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Weight (kg)',
                        data: weights,
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        borderWidth: 2,
                        pointRadius: 5,
                        pointBackgroundColor: '#007bff',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: 'Weight (kg)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching entries:', error);
            chartContainer.innerHTML = '<p>Error loading chart data</p>';
        });
});
