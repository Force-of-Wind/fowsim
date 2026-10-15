$(document).ready(function () {
	const opener = $('#pack-opener');
	if (opener.length === 0) {
		return; // Invalid / not-implemented pack page
	}

	const setCode = opener.data('setcode');
	const decksUrl = opener.data('decks-url');
	const addUrl = opener.data('add-url');
	const skipPrefUrl = opener.data('skip-pref-url');
	const csrfToken = opener.find('input[name=csrfmiddlewaretoken]').val();

	let alwaysSkip = String(opener.data('skip-animation')) === '1';
	let revealed = false;
	let opening = false;
	let historyRecorded = false;
	let animTimers = [];
	let cachedDecks = null;
	let pendingCards = []; // cards queued for the add-to-deck modal

	/* ----------------------------------------------------------------- *
	 *  Card interactions (flip / preview / add)
	 * ----------------------------------------------------------------- */
	$('.card').each(function () {
		const card = $(this);

		card.on('click', function () {
			if (!card.hasClass('is-flipped')) {
				card.addClass('is-flipped');
				return;
			}
			showHighlight(card);
		});

		card.find('.card-action-view').on('click', function (event) {
			event.stopPropagation();
			showHighlight(card);
		});

		card.find('.card-action-add').on('click', function (event) {
			event.stopPropagation();
			openAddDeckModal([cardDataFrom(card)], 'single');
		});
	});

	$('.card img').on('dragstart', function (event) {
		event.preventDefault();
	});

	function cardDataFrom(card) {
		const back = card.find('.card__face--back');
		return {
			card_id: card.data('card-id'),
			name: back.data('card-name'),
			zone_suggestion: card.data('zone-suggestion'),
			img: back.attr('src'),
			detailLink: back.data('card-url')
		};
	}

	function showHighlight(card) {
		const back = card.find('.card__face--back');
		$('#highlight-img').attr('src', back.attr('src'));
		$('#highlight-img').attr('alt', back.attr('alt'));
		$('#highlight-link').attr('href', back.data('card-url'));
		$('#card-highlight').css('display', 'flex');
	}

	/* ----------------------------------------------------------------- *
	 *  Opening / skipping animation
	 * ----------------------------------------------------------------- */
	$('#pack-standard').on('click', function (event) {
		event.preventDefault();
		if (alwaysSkip) {
			finishOpening(true); // honour the saved preference: reveal instantly on open
		} else {
			startAnimatedOpening();
		}
	});

	function startAnimatedOpening() {
		if (revealed || opening) {
			return;
		}
		opening = true;
		// The opening is now committed; there is no animation left to meaningfully skip,
		// so disable the skip button to avoid the reveal firing behind the skip modal.
		$('#skipBtn').prop('disabled', true);
		const pack = $('#pack-standard').css('pointer-events', 'none');
		pack.addClass('shake');

		// Burst the pack open, fire the light flash, then drop in the cards.
		animTimers.push(setTimeout(() => {
			pack.removeClass('shake').addClass('burst');
			$('.pack-flash').addClass('active');
		}, 300));
		animTimers.push(setTimeout(() => finishOpening(false), 720));
	}

	function finishOpening(flipAll) {
		if (revealed) {
			return;
		}
		revealed = true;
		opening = false;
		animTimers.forEach(clearTimeout);
		animTimers = [];

		$('.pack-stage').css('display', 'none');
		$('.pack-wrapper').css('display', 'flex');
		$('.actions-wrapper').css('display', 'flex');

		if (flipAll) {
			$('.card').removeClass('enter in').addClass('is-flipped');
		} else {
			revealEntrance();
		}

		recordHistory();
	}

	function revealEntrance() {
		$('.card').each(function (index) {
			const card = $(this);
			card.css('animation-delay', (index * 70) + 'ms');
			// Once the entrance animation finishes, drop the helper classes so the
			// flip transition is free to take over the transform.
			card.one('animationend', function () {
				card.removeClass('enter in').css('animation-delay', '');
			});
			card.addClass('in');
		});
	}

	$('#skipBtn').on('click', function () {
		if (alwaysSkip) {
			finishOpening(true);
			return;
		}
		openModal('skipModal');
	});

	$('#skipConfirm').on('click', function () {
		const always = $('#skipAlwaysCheck').is(':checked');
		closeModal('skipModal');
		finishOpening(true);
		if (always && !alwaysSkip) {
			alwaysSkip = true;
			$('#skipAnimationToggle').prop('checked', true);
			saveSkipPreference(true);
		}
	});

	// Persisted "skip every time" toggle in the top bar
	$('#skipAnimationToggle').on('change', function () {
		alwaysSkip = $(this).is(':checked');
		saveSkipPreference(alwaysSkip);
	});

	function saveSkipPreference(skip) {
		$.ajax({
			type: 'POST',
			url: skipPrefUrl,
			data: JSON.stringify({ skip: skip }),
			contentType: 'application/json',
			headers: { 'X-CSRFToken': csrfToken }
		});
	}

	/* ----------------------------------------------------------------- *
	 *  Add to deck
	 * ----------------------------------------------------------------- */
	$('#addAllBtn').on('click', function () {
		const cards = [];
		$('.card').each(function () {
			cards.push(cardDataFrom($(this)));
		});
		openAddDeckModal(cards, 'all');
	});

	function openAddDeckModal(cards, mode) {
		pendingCards = cards;
		const context = $('.add-deck-context');
		if (mode === 'all') {
			context.text(`Adding ${cards.length} pulled card${cards.length === 1 ? '' : 's'} to a deck.`);
			$('#addZoneSelect').val('auto');
		} else {
			context.text(`Adding "${cards[0].name}" to a deck.`);
			$('#addZoneSelect').val(cards[0].zone_suggestion || 'auto');
		}
		$('.add-deck-status').hide().empty();
		$('#addDeckConfirm').prop('disabled', false);
		openModal('addDeckModal');
		loadDecks();
	}

	function loadDecks() {
		const form = $('.add-deck-form');
		const empty = $('.add-deck-empty');
		const loading = $('.add-deck-loading');

		const render = (decks) => {
			loading.hide();
			if (!decks || decks.length === 0) {
				form.hide();
				$('#addDeckConfirm').prop('disabled', true);
				empty.show();
				return;
			}
			empty.hide();
			const select = $('#addDeckSelect').empty();
			decks.forEach((deck) => {
				select.append($('<option>').val(deck.id).text(deck.name));
			});
			form.show();
		};

		if (cachedDecks !== null) {
			render(cachedDecks);
			return;
		}

		form.hide();
		empty.hide();
		loading.show();
		$.ajax({
			type: 'GET',
			url: decksUrl,
			dataType: 'json',
			success: function (data) {
				cachedDecks = data.decks || [];
				render(cachedDecks);
			},
			error: function () {
				loading.hide();
				showAddStatus('Could not load your decks. Please try again.', true);
			}
		});
	}

	$('#addDeckConfirm').on('click', function () {
		const deckId = $('#addDeckSelect').val();
		if (!deckId) {
			return;
		}
		const zoneChoice = $('#addZoneSelect').val();
		const payloadCards = pendingCards.map((card) => ({
			card_id: card.card_id,
			zone: zoneChoice === 'auto' ? card.zone_suggestion : zoneChoice
		}));

		const confirmBtn = $(this).prop('disabled', true);
		const deckName = $('#addDeckSelect option:selected').text();

		$.ajax({
			type: 'POST',
			url: addUrl,
			data: JSON.stringify({ decklist_id: deckId, cards: payloadCards }),
			contentType: 'application/json',
			headers: { 'X-CSRFToken': csrfToken },
			success: function (data) {
				closeModal('addDeckModal');
				const count = data.added || payloadCards.length;
				showToast(`Added ${count} card${count === 1 ? '' : 's'} to ${deckName}.`);
			},
			error: function () {
				confirmBtn.prop('disabled', false);
				showAddStatus('Could not add the cards to that deck.', true);
			}
		});
	});

	function showAddStatus(message, isError) {
		$('.add-deck-status')
			.removeClass('text-danger text-success')
			.addClass(isError ? 'text-danger' : 'text-success')
			.text(message)
			.show();
	}

	/* ----------------------------------------------------------------- *
	 *  Export & navigation
	 * ----------------------------------------------------------------- */
	$('#exportBtn').on('click', function () {
		openModal('exportModal');
	});

	$('#openNewBtn').on('click', function () {
		location.reload();
	});

	$('#packSelectBtn').on('click', function () {
		window.location.assign($(this).data('url'));
	});

	$('#packHistoryBtn').on('click', function () {
		window.location.assign($(this).data('url'));
	});

	/* ----------------------------------------------------------------- *
	 *  Modal helpers
	 * ----------------------------------------------------------------- */
	function openModal(id) {
		$('#' + id).css('display', 'flex');
	}

	function closeModal(id) {
		$('#' + id).css('display', 'none');
	}

	$('[data-close-modal]').on('click', function () {
		closeModal($(this).data('close-modal'));
	});

	$('.pack-modal').on('click', function (event) {
		if (event.target === this) {
			$(this).css('display', 'none');
		}
	});

	$('#card-highlight').on('click', function (event) {
		if (event.target === this) {
			$(this).css('display', 'none');
		}
	});

	/* ----------------------------------------------------------------- *
	 *  Pack history (localStorage)
	 * ----------------------------------------------------------------- */
	function recordHistory() {
		if (historyRecorded) {
			return;
		}
		historyRecorded = true;

		let pulledCards = localStorage.getItem('pulledCards');
		pulledCards = pulledCards ? JSON.parse(pulledCards) : [];

		const pulls = [];
		$('.card__face--back').each(function () {
			pulls.push({
				name: $(this).attr('title'),
				img: $(this).attr('src'),
				detailLink: $(this).data('card-url'),
				slot: $(this).data('slot')
			});
		});

		pulledCards.unshift({
			pulls: pulls,
			pulledAt: new Date(Date.now()).toLocaleString(),
			set: setCode
		});
		localStorage.setItem('pulledCards', JSON.stringify(pulledCards));
		refreshCounter();
	}

	function refreshCounter() {
		let pulledCards = localStorage.getItem('pulledCards');
		pulledCards = pulledCards ? JSON.parse(pulledCards) : [];
		// Compare case-insensitively so history written before the set key was uppercased
		// (older entries used the raw URL segment) still counts toward this set.
		const target = String(setCode).toUpperCase();
		const setBooster = pulledCards.filter((pack) => String(pack.set).toUpperCase() === target);
		$('#packCounter').text(setBooster.length);
	}

	/* ----------------------------------------------------------------- *
	 *  Toast
	 * ----------------------------------------------------------------- */
	let toastTimer = null;

	function showToast(message) {
		const toast = $('#packToast').text(message).addClass('show');
		clearTimeout(toastTimer);
		toastTimer = setTimeout(() => toast.removeClass('show'), 3200);
	}

	/* ----------------------------------------------------------------- *
	 *  Init
	 * ----------------------------------------------------------------- */
	refreshCounter();
	// Note: when alwaysSkip is on we do NOT auto-open on load — opening still requires a
	// deliberate click (it just reveals instantly), so navigating/refreshing the page
	// never silently records a pull to history.
});
