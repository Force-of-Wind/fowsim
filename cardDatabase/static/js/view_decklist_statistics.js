const attributeRegex = /\{(\w)\}+/g;

function calculateDiagramData(cardsToCalc, attributeCanvas, manaCurveCanvas) {
    let manaCurveThreshhold = 6;
    manaCurveStatData = [
        { cost: '0', count: 0 },
        { cost: '1', count: 0 },
        { cost: '2', count: 0 },
        { cost: '3', count: 0 },
        { cost: '4', count: 0 },
        { cost: '5', count: 0 },
        { cost: '6+', count: 0 },
    ];
    attributeStatData = [
        { shortTerm: 'R', attribute: 'Fire', count: 0, color: "#ef1919" },
        { shortTerm: 'U', attribute: 'Water', count: 0, color: "#199eef" },
        { shortTerm: 'W', attribute: 'Light', count: 0, color: "#efea19" },
        { shortTerm: 'B', attribute: 'Darkness', count: 0, color: "#a451c8" },
        { shortTerm: 'G', attribute: 'Wind', count: 0, color: "#19ef49" },
        { shortTerm: 0, attribute: 'Void', count: 0, color: "#b1b5b2" }
    ];

    cardsToCalc.forEach(card => {
        if (card.cost !== null) {
            card.cost = [...card.cost.matchAll(attributeRegex)].map((el) => el[1]);
            let cardCost = 0;
            card.cost.forEach(attribute => {
                if (isNaN(attribute)) {
                    cardCost++;
                    attributeStatData[attributeStatData.findIndex((el) => el.shortTerm == attribute)].count += card.quantity;
                }
                else{
                    cardCost += parseInt(attribute);
                    attributeStatData[attributeStatData.findIndex((el) => el.shortTerm == 0)].count += card.quantity;
                }
            });

            if(cardCost >= manaCurveThreshhold){
                manaCurveStatData[manaCurveStatData.findIndex((el) => el.cost == manaCurveThreshhold + '+')].count += card.quantity;
            }
            else{
                manaCurveStatData[manaCurveStatData.findIndex((el) => el.cost ==cardCost)].count += card.quantity;
            }
        }
    });

    attributeStatData.sort((a, b) => b.count - a.count);

    drawCharts(attributeCanvas, attributeStatData, manaCurveCanvas, manaCurveStatData);
}

function drawCharts(attributeCanvas, attributeStatData, manaCurveCanvas, manaCurveStatData) {
    new Chart(attributeCanvas,
        {
            type: 'bar',
            options: {
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: true
                    },
                    colors: {
                        enabled: false,
                        forceOverride: true
                    }
                },
            },
            data: {
                labels: attributeStatData.map(row => row.attribute),
                datasets: [
                    {
                        label: '',
                        borderColor: 'white',
                        backgroundColor: attributeStatData.map(row => row.color),
                        data: attributeStatData.map(row => row.count)
                    }
                ]
            }
        });
    new Chart(manaCurveCanvas,
        {
            type: 'bar',
            options: {
                indexAxis: 'x',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: true
                    },
                    colors: {
                        enabled: false,
                        forceOverride: true
                    }
                },
            },
            data: {
                labels: manaCurveStatData.map(row => row.cost),
                datasets: [
                    {
                        label: 'Card total',
                        borderColor: 'white',
                        backgroundColor: '#a451c8',
                        data: manaCurveStatData.map(row => row.count)
                    }
                ]
            }
        });
}

function isNumeric(str) {
    if (typeof str != "string") return false;
    return !isNaN(str) &&
        !isNaN(parseFloat(str))
}

function initStatistics(cards, attributeCanvas, manaCurveCanvas) {
    calculateDiagramData(cards, attributeCanvas, manaCurveCanvas);
}
