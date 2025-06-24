let rulerBreakdownChart;

function getRandomHexColorForDarkLightMode() {
    // Hue: any (0-360)
    const hue = Math.floor(Math.random() * 360);

    // Saturation: 50% - 80% (vibrant but not neon)
    const saturation = Math.floor(50 + Math.random() * 30);

    // Lightness: 40% - 60% (mid-tone for contrast on both modes)
    const lightness = Math.floor(40 + Math.random() * 20);

    // Convert HSL to RGB
    function hslToRgb(h, s, l) {
        s /= 100;
        l /= 100;

        const c = (1 - Math.abs(2 * l - 1)) * s;
        const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
        const m = l - c / 2;
        let r = 0, g = 0, b = 0;

        if (h < 60) [r, g, b] = [c, x, 0];
        else if (h < 120) [r, g, b] = [x, c, 0];
        else if (h < 180) [r, g, b] = [0, c, x];
        else if (h < 240) [r, g, b] = [0, x, c];
        else if (h < 300) [r, g, b] = [x, 0, c];
        else[r, g, b] = [c, 0, x];

        r = Math.round((r + m) * 255);
        g = Math.round((g + m) * 255);
        b = Math.round((b + m) * 255);

        return [r, g, b];
    }

    const [r, g, b] = hslToRgb(hue, saturation, lightness);

    // Convert RGB to hex
    const toHex = (v) => v.toString(16).padStart(2, '0');

    return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

function drawStatsForRulers() {
    if(rulerBreakdownChart)
        rulerBreakdownChart.destroy();
    
    $('#ruler-export-img-btn').prop('disabled', true);
    $('#ruler-export-btn').prop('disabled', true);
    

    if (!window.rulers || Object.keys(window.rulers).length < 1) {
        console.error('Cannot load stats.')
        alertify.error('Error loading stats.');
        return;
    }

    const inwardLabelPlugin = {
            id: 'inwardLabels',
            afterDatasetsDraw(chart) {
            const ctx = chart.ctx;
            const meta = chart.getDatasetMeta(0);
            const dataset = chart.data.datasets[0];
            const labels = chart.data.labels;

            const centerX = (chart.chartArea.left + chart.chartArea.right) / 2;
            const centerY = (chart.chartArea.top + chart.chartArea.bottom) / 2;

            meta.data.forEach((arc, i) => {
                const angle = (arc.startAngle + arc.endAngle) / 2;
                const radius = arc.outerRadius * 0.7;

                const x = centerX + Math.cos(angle) * radius;
                const y = centerY + Math.sin(angle) * radius;

                ctx.save();
                ctx.translate(x, y);

                // Rotate depending on which side of the chart the label is on
                // angle in radians from 0 to 2π
                let rotation = angle;
                // Convert to degrees for readability
                const degrees = rotation * (180 / Math.PI);

                if (degrees > 90 && degrees < 270) {
                    // Left half - flip 180 degrees to keep text upright
                    rotation += Math.PI;
                }

                ctx.rotate(rotation);
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 14px sans-serif';

                const label = labels[i];
                const lines = label.split('\n');
                const lineHeight = 16; // px, adjust as needed
                const totalHeight = lines.length * lineHeight;
                // Center text vertically
                let startY = -totalHeight / 2 + lineHeight / 2;
                let first = true;

                for (const line of lines) {
                    let text;
                    if(first){
                        text = `${dataset.data[i]}x ${line}`;
                        first = false;
                    }
                    else 
                        text = line;
                        
                    if(FOWDB_IS_MOBILE){
                        if(dataset.data[i] > 1)
                            text = text.substring(0, 12)
                        else
                            text = ''
                    }
                        
                    ctx.fillText(text, 0, startY);
                    startY += lineHeight;
                }

                ctx.restore();
            });
        }
    };

    let rulerBreakdownCanvas = $('#ruler-breakdown-canvas');

    let textExport = '';

    let sortedRulerBreakdown = [];

    for (var rulerName in window.rulers) {
        sortedRulerBreakdown.push([rulerName.replaceAll(' + ', '\n'), window.rulers[rulerName], getRandomHexColorForDarkLightMode()]);
    }

    sortedRulerBreakdown.sort(function (a, b) {
        return a[1] - b[1];
    });

    sortedRulerBreakdown.forEach(e => textExport += `${e[1]};${e[0].replaceAll('\n', ' + ')};\n`);

    $('#ruler-breakdown-textarea').text(textExport);

    rulerBreakdownChart = new Chart(rulerBreakdownCanvas,
    {
        type: 'pie',
        options: {
            plugins: {
                legend: {
                    display: false,
                },
            }
        },
        plugins: [inwardLabelPlugin],
        data: {
            labels: sortedRulerBreakdown.map(ruler => ruler[0]),
            datasets: [{
                label: 'Ruler Count',
                data: sortedRulerBreakdown.map(ruler => ruler[1]),
                backgroundColor: sortedRulerBreakdown.map(ruler => ruler[2]),
                hoverOffset: 4
            }]
        }
    });

    $('#ruler-export-btn').prop('disabled', false);
    $('#ruler-export-img-btn').prop('disabled', false);
}

function exportRulerBreakdownAsImage(){
    if (!window.rulers || Object.keys(window.rulers).length < 1) {
        console.error('Cannot export stats.')
        alertify.error('Error export stats.');
        return;
    }

    const canvas = document.getElementById("ruler-breakdown-canvas");
    const dataURL = canvas.toDataURL("image/png");

    // Create a download link
    const link = document.createElement("a");
    link.href = dataURL;
    link.download = "ruler-breakdown.png";
    link.click();
}