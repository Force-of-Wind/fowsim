function setupAlertify() {
	alertify.defaults.notifier.delay = 2;
	if (FOWDB_IS_MOBILE) {
		alertify.defaults.notifier.position = 'top-left';
	} else {
		alertify.defaults.notifier.position = 'bottom-left';
	}
}

function initExporter() {
	const CsvGenerator = {
		_headers: [],
		_rows: [],

		setHeaders: function (headerArray) {
			this._headers = headerArray;
		},

		setData: function (dataArray) {
			if (Array.isArray(dataArray) && dataArray.length > 0) {
				if (typeof dataArray[0] === "object" && !Array.isArray(dataArray[0])) {
					// Convert array of objects to array of arrays using headers
					this._rows = dataArray.map(row =>
						this._headers.map(h => row[h] ?? "")
					);
				} else {
					// Assume it's already array of arrays
					this._rows = dataArray;
				}
			} else {
				this._rows = [];
			}
		},

		download: function (filename) {
			if(!filename){
				console.error('filename empty');
				return;
			}

			const escapeCsv = (str) =>
				`"${String(str).replace(/"/g, '""')}"`;

			const csvContent = [
				this._headers.map(escapeCsv).join(";"),
				...this._rows.map(row => row.map(escapeCsv).join(";"))
			].join("\n");

			const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
			const url = URL.createObjectURL(blob);

			const link = document.createElement("a");
			link.setAttribute("href", url);
			link.setAttribute("download", filename);
			link.style.display = "none";
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
			URL.revokeObjectURL(url);

			this._headers = [];
			this._rows = [];
		}
	};

	// Expose globally
	window.CsvGenerator = CsvGenerator;
}


$(document).ready(function () {
	setupAlertify();
	initExporter();
});