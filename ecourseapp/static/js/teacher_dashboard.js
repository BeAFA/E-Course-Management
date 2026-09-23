document.addEventListener('DOMContentLoaded', () => {
    const chartCanvas = document.getElementById('revenueChart');
    if (!chartCanvas) return;

    // Lấy dữ liệu an toàn từ window (được truyền từ template)
    const labels = (window.teacherChartData && window.teacherChartData.labels) ? window.teacherChartData.labels : [];
    const values = (window.teacherChartData && window.teacherChartData.data) ? window.teacherChartData.data : [];

    const ctx = chartCanvas.getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels.length > 0 ? labels : ['Chưa có dữ liệu'],
            datasets: [{
                label: 'Doanh thu (VNĐ)',
                data: values.length > 0 ? values : [0],
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.08)',
                borderWidth: 2.5,
                fill: true,
                tension: 0.35,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString('vi-VN') + ' đ';
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Doanh thu: ' + context.parsed.y.toLocaleString('vi-VN') + ' VNĐ';
                        }
                    }
                }
            }
        }
    });
});