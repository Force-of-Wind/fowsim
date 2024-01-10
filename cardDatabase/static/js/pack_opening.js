$(document).ready(function () {
	$('#pack-standard').on('click', function () {
		let body = $('body');
		body.removeClass().addClass('restart');
		$('.loader').css('visibility', 'visible');
		$('.pack-container').css('display', 'none');

		$('.card').on('click', function () {
			$(this).addClass('is-flipped');
			$(this).off('click');
			$(this).on('click', function () {
				let resultSide = $(this).children('.card__face--back')
				let src = resultSide.attr('src');
				let alt = resultSide.attr('alt');
				let link = resultSide.data('card-url')
				$('#highlight-img').attr('src', src);
				$('#highlight-img').attr('alt', alt);
				$('#highlight-link').attr('href', link)
				$('.card-highlight').css('display', 'flex');
				window.onclick = function (event) {
					let overlay = document.getElementById("card-highlight");
					if (event.target == overlay) {
						$('.card-highlight').css('display', 'none');
					}
				}
			});
		});

		$('.card img').on('dragstart', function (event) { event.preventDefault(); });

		setTimeout(() => {
			let body = $('body');
			body.addClass('loading');
		}, 30);

		setTimeout(() => {
			let body = $('body');
			body.addClass('loaded');
		}, 300);

		setTimeout(() => {
			let body = $('body');
			body.removeClass('restart').addClass('new-page');
			$('.pack-wrapper').css('display', 'flex');
			$('.loader-wrapper').css('visibility', 'hidden');
			$('.actions-wrapper').css('visibility', 'visible');

			let pulledCards = localStorage.getItem('pulledCards');
			if (!pulledCards)
				pulledCards = [];
			else
				pulledCards = JSON.parse(pulledCards);

			let pulls = [];
			$('.card__face--back').each(function () {
				let pull = {
					name: $(this).attr('title'),
					img: $(this).attr('src'),
					detailLink: $(this).data('card-url'),
					slot: $(this).data('slot')
				};

				pulls.push(pull);
			})

			let set = (window.location.href.split('/pack_opening/')[1]).split('/')[0];

			pulledCards.unshift({ pulls: pulls, pulledAt: new Date(Date.now()).toLocaleString(), set: set });
			localStorage.setItem('pulledCards', JSON.stringify(pulledCards));
			refreshCounter();
		}, 700);
	});

	$('#openNewBtn').on('click', function () {
		location.reload();
	});

	$('#exportBtn').on('click', function () {
		$('#exportModal').css('display', 'block');
	});

	$('.dismiss-modal').on('click', function () {
		$('#exportModal').css('display', 'none');
	});

	$('#packSelectBtn').on('click', function () {
		window.location.replace($(this).data('url'));
	});

	$('#packHistoryBtn').on('click', function () {
		window.location.replace($(this).data('url'));
	});

	window.onclick = function (event) {
		let modal = document.getElementById("exportModal");
		if (event.target == modal) {
			$('#exportModal').css('display', 'none');
		}
	}

	function refreshCounter() {
		let set = (window.location.href.split('/pack_opening/')[1]).split('/')[0];
		let pulledCards = localStorage.getItem('pulledCards');
		if (!pulledCards)
			pulledCards = [];
		else
			pulledCards = JSON.parse(pulledCards);

		let setBooster = pulledCards.filter((pack) => pack.set === set);
		$('#packCounter').text(setBooster.length);
	}

	refreshCounter();
});
