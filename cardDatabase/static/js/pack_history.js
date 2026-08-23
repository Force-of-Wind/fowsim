$(document).ready(function () {
	const historyJson = localStorage.getItem('pulledCards');
	const container = $('#historyContainer');
	let exportArray = [];

	container.empty();

	function renderEmpty() {
		container.html(
			'<div class="empty-wrapper text-center text-muted py-5">' +
			'<i class="fa-solid fa-box-open fa-3x mb-3"></i>' +
			'<h4>No packs opened yet</h4>' +
			'<p>Open a pack and your pulls will show up here.</p>' +
			'</div>'
		);
	}

	function escapeHtml(value) {
		// Escape quotes too: these values are interpolated into HTML attributes
		// (title/alt/src/data-card-url), where the jQuery .text().html() trick alone
		// leaves " and ' intact and lets a quoted value break out of the attribute.
		return String(value == null ? '' : value)
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/"/g, '&quot;')
			.replace(/'/g, '&#39;');
	}

	if (!historyJson) {
		renderEmpty();
	} else {
		const history = JSON.parse(historyJson);

		if (!history.length) {
			renderEmpty();
		}

		history.forEach((entry) => {
			let cardsHtml = '';
			entry.pulls.forEach((card) => {
				const slot = escapeHtml(card.slot);
				const name = escapeHtml(card.name);
				const img = escapeHtml(card.img);
				const link = escapeHtml(card.detailLink);
				cardsHtml +=
					`<div class="history-card">` +
					`<div class="${slot}"></div>` +
					`<img class="card-img" title="${name}" alt="${name}" src="${img}" data-card-url="${link}" />` +
					`</div>`;
				exportArray.unshift(card.name);
			});

			const count = entry.pulls.length;
			const entryHtml =
				`<div class="history-entry card mb-4">` +
				`<div class="history-entry-header">` +
				`<span class="badge badge-primary history-set">${escapeHtml(entry.set)}</span>` +
				`<span class="history-time"><i class="fa-regular fa-clock mr-1"></i>${escapeHtml(entry.pulledAt)}</span>` +
				`<span class="history-count">${count} card${count === 1 ? '' : 's'}</span>` +
				`</div>` +
				`<div class="history-cards">${cardsHtml}</div>` +
				`</div>`;
			container.append(entryHtml);
		});

		container.on('click', '.card-img', function () {
			const img = $(this);
			$('#highlight-img').attr('src', img.attr('src'));
			$('#highlight-img').attr('alt', img.attr('alt'));
			$('#highlight-link').attr('href', img.data('card-url'));
			$('#card-highlight').css('display', 'flex');
		});

		container.on('click', '.foil', function () {
			$(this).siblings('img').trigger('click');
		});
	}

	$('#clearHistory').on('click', function () {
		localStorage.removeItem('pulledCards');
		exportArray = [];
		renderEmpty();
	});

	$('#exportHistory').on('click', function () {
		const counts = {};
		exportArray.forEach((name) => {
			counts[name] = (counts[name] || 0) + 1;
		});
		let cards = '';
		for (const [name, value] of Object.entries(counts)) {
			cards += `${value} ${name}\n`;
		}
		$('#exportText').val(cards);
		$('#exportModal').css('display', 'flex');
	});

	$('.dismiss-modal').on('click', function () {
		$('#exportModal').css('display', 'none');
	});

	$('#exportModal').on('click', function (event) {
		if (event.target === this) {
			$(this).css('display', 'none');
		}
	});

	$('#card-highlight').on('click', function (event) {
		if (event.target === this) {
			$(this).css('display', 'none');
		}
	});
});
