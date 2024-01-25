const attributeRegex = /\{(\w)\}+/g;
let attributesChart;
let curveChart;


function calculateDiagramData(cardsToCalc, attributeCanvas, manaCurveCanvas, mobile) {
    let manaCurveThreshhold = 6;
    const voidX = 'X';

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
        { shortTerm: 'R', attribute: 'Fire', count: 0, color: "#ef1919", x: 0, cardCount: 0 },
        { shortTerm: 'U', attribute: 'Water', count: 0, color: "#199eef", x: 0, cardCount: 0 },
        { shortTerm: 'W', attribute: 'Light', count: 0, color: "#efea19", x: 0, cardCount: 0 },
        { shortTerm: 'B', attribute: 'Dark', count: 0, color: "#a451c8", x: 0, cardCount: 0 },
        { shortTerm: 'G', attribute: 'Wind', count: 0, color: "#19ef49", x: 0, cardCount: 0 },
        { shortTerm: 0, attribute: 'Void', count: 0, color: "#b1b5b2", x: 0, cardCount: 0 }
    ];


    cardsToCalc.forEach(card => {
        if (card.cost !== null) {
            card.cost = [...card.cost.matchAll(attributeRegex)].map((el) => el[1]);
            let cardCost = 0;
            let lastAttribute = '';
            card.cost.forEach(attribute => {
                if (lastAttribute !== attribute) {
                    if (isNaN(attribute) && attribute != voidX && attribute != 'M') {
                        attributeStatData[attributeStatData.findIndex((el) => el.shortTerm == attribute)].cardCount += card.quantity;
                    }
                    else if (attribute == 'M') {
                        attributeStatData[attributeStatData.findIndex((el) => el.shortTerm == 0)].cardCount += card.quantity;
                    }
                    else if (attribute !== voidX && parseInt(attribute) > 0) {
                        attributeStatData[attributeStatData.findIndex((el) => el.shortTerm == 0)].cardCount += card.quantity;
                    }
                    lastAttribute = attribute;
                }
                if (isNaN(attribute) && attribute != voidX && attribute != 'M') {
                    cardCost++;
                    attributeStatData[attributeStatData.findIndex((el) => el.shortTerm == attribute)].count += card.quantity;
                }
                else if (attribute == 'M') {
                    cardCost++;
                    attributeStatData[attributeStatData.findIndex((el) => el.shortTerm == 0)].cardCount += card.quantity;
                }
                else if (attribute !== voidX) {
                    let currentCost = parseInt(attribute)
                    cardCost += currentCost;
                    attributeStatData[attributeStatData.findIndex((el) => el.shortTerm == 0)].count += currentCost * card.quantity;
                }
            });

            if (cardCost >= manaCurveThreshhold) {
                manaCurveStatData[manaCurveStatData.findIndex((el) => el.cost == manaCurveThreshhold + '+')].count += card.quantity;
            }
            else {
                manaCurveStatData[manaCurveStatData.findIndex((el) => el.cost == cardCost)].count += card.quantity;
            }
        }
    });

    let fullAttributeCount = attributeStatData.reduce((accumulator, currentValue) => {
        return accumulator + currentValue.count
    }, 0);

    attributeStatData.sort((a, b) => b.count - a.count);
    attributeStatData.forEach((attribute) => {
        attribute.x = Math.round(attribute.count * 100 / (fullAttributeCount));
    });

    drawCharts(attributeCanvas, attributeStatData, manaCurveCanvas, manaCurveStatData, mobile);
}

function drawCharts(attributeCanvas, attributeStatData, manaCurveCanvas, manaCurveStatData, mobile) {
    if (attributesChart !== null && attributesChart !== undefined) {
        attributesChart.destroy();
    }

    attributesChart = new Chart(attributeCanvas,
        {
            type: 'bar',
            plugins: [ChartDataLabels],
            options: {
                parsing: {
                    xAxisKey: 'x',
                    yAxisKey: 'attribute'
                },
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: true,
                        callbacks: {
                            label: function (context) {
                                let label = context.dataset.label || '';

                                if (context.raw.cardCount > 1)
                                    return `${label}: ${context.raw.x} (${context.raw.cardCount} cards)`;
                                else
                                    return `${label}: ${context.raw.x} (${context.raw.cardCount} card)`;
                            }
                        }
                    },
                    colors: {
                        enabled: false,
                        forceOverride: true
                    },
                    title: {
                        display: true,
                        position: 'bottom',
                        text: 'Card attributes in %'
                    },
                    datalabels: {
                        formatter: function (value, _) {
                            let percent = value.x;
                            if (percent <= 0 || isNaN(percent))
                                return '';
                            else if (percent < 5 && mobile)
                                return percent;
                            else if (percent <= 1)
                                return percent;
                            else
                                return percent + ' %';
                        }
                    }
                },
            },
            data: {
                datasets: [
                    {
                        label: '%',
                        borderColor: 'white',
                        backgroundColor: attributeStatData.map(row => row.color),
                        data: attributeStatData,
                        datalabels: {
                            color: '#000000'
                        }
                    }
                ]
            }
        });

    if (curveChart !== null && curveChart !== undefined) {
        curveChart.destroy();
    }
    curveChart = new Chart(manaCurveCanvas,
        {
            type: 'bar',
            data: {
                labels: manaCurveStatData.map(row => row.cost),
                datasets: [
                    {
                        borderColor: 'white',
                        backgroundColor: '#a451c8',
                        label: 'Cards with cost',
                        data: manaCurveStatData.map(row => row.count)
                    }
                ]
            },
            options: {
                indexAxis: 'x',
                plugins: {
                    tooltip: {
                        enabled: true
                    },
                    legend: {
                        display: false
                    },
                    colors: {
                        enabled: false,
                        forceOverride: true
                    },
                    subtitle: {
                        display: true,
                        position: 'left',
                        text: 'Number of Cards'
                    },
                    title: {
                        display: true,
                        position: 'bottom',
                        text: 'Will Value'
                    }
                },
            }
        });
}

function isNumeric(str) {
    if (typeof str != "string") return false;
    return !isNaN(str) &&
        !isNaN(parseFloat(str));
}

function initStatistics(cards, attributeCanvas, manaCurveCanvas, zoneChangeButton, zoneSelect, mobile = false) {
    setStatistics(cards, attributeCanvas, manaCurveCanvas, zoneChangeButton, zoneSelect, mobile);

    $(zoneChangeButton).on('click', function () {
        setStatistics(cards, attributeCanvas, manaCurveCanvas, zoneChangeButton, zoneSelect, mobile);
    });
}

function setStatistics(cards, attributeCanvas, manaCurveCanvas, zoneChangeButton, zoneSelect, mobile) {
    let selectedZones = $(zoneSelect).val();

    let limitedCards = cards.filter((card) => selectedZones.find((zone) => zone == card.zone));

    //deep copy to avoid some issues with refs
    limitedCards = JSON.parse(JSON.stringify(limitedCards));

    calculateDiagramData(limitedCards, attributeCanvas, manaCurveCanvas, mobile);
}
