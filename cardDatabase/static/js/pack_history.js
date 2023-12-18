$(document).ready(function () {
    let historyJson = localStorage.getItem('pulledCards');
    let exportArray = [];

    $('#historyContainer').empty();

    if (!historyJson) {
        $('#historyContainer').append('<div class="empty-wrapper"><h1>No cards in History.</h1></div>');
    }
    else {
        let history = JSON.parse(historyJson);

        history.forEach(entry => {
            let imgHtml = ''
            entry.pulls.forEach(card => {
                imgHtml += `<img class="card" title="${card.name}" src="${card.img}" />`
                exportArray.unshift(card.name);
            })


            let pullhtml =
                `<div class="pull-entry">
            <span>Pack Opened: ${entry.pulledAt}</span>
            <br />
            <span>Pack: ${entry.set}</span>
            <div class="card-container">
            ${imgHtml}
            </div>
            <hr />
        </div>
        `
            $('#historyContainer').append(pullhtml);
        });
    }

    $('#clearHistory').on('click', function () {
        localStorage.removeItem('pulledCards');
        $('#historyContainer').empty();
        $('#historyContainer').append('<div class="empty-wrapper"><h1>No cards in History.</h1></div>');
        exportArray = [];
    })

    $('#exportHistory').on('click', function () {
        $('#exportText').val('');
        $('#exportModal').css('display', 'block');
        let counts = {};
        exportArray.forEach(function (x) { counts[x] = (counts[x] || 0) + 1; });
        let cards = '';
        for (const [key, value] of Object.entries(counts)) {
            console.log(`${key}: ${value}`);
            cards += `${value} ${key}
`
        }

        $('#exportText').val(cards);
    });

    $('.dismiss-modal').on('click', function () {
        $('#exportModal').css('display', 'none');
    });

    window.onclick = function (event) {
        let modal = document.getElementById("exportModal");
        if (event.target == modal) {
            $('#exportModal').css('display', 'none');
        }
    };

    $('#packSelectBtn').on('click', function () {
        window.location.replace($(this).data('url'));
    });
});