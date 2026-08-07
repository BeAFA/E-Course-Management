document.addEventListener('DOMContentLoaded', function () {
    const chartCanvas = document.getElementById('revenueChart');
    if (!chartCanvas) return;

    const labelsElem = document.getElementById('chart-labels-data');
    const valuesElem = document.getElementById('chart-values-data');

    let chartLabels = [];
    let chartDataValues = [];

    try {
        if (labelsElem) chartLabels = JSON.parse(labelsElem.textContent || '[]');
        if (valuesElem) chartDataValues = JSON.parse(valuesElem.textContent || '[]');
    } catch (e) {
        console.error('Lỗi giải mã dữ liệu biểu đồ:', e);
    }

    const ctx = chartCanvas.getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartLabels,
            datasets: [{
                label: 'Doanh thu (nghìn đồng)',
                data: chartDataValues,
                borderColor: '#2b6cb0',
                backgroundColor: 'rgba(43, 108, 176, 0.1)',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});