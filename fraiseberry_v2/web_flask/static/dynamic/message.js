document.addEventListener("DOMContentLoaded", function() {


	const dms = document.querySelectorAll(".dm");
	const varThisUserID = document.getElementById("varThisUserID");
	const varMatchID = document.getElementById("varMatchID");
	const send_icons = document.getElementById("send_icon");
	const text_area = document.getElementById("text_area");
	const home = document.getElementById("home");
	const refreshTime = 2 * 60 * 1000;

	// Adds a class to add styles //
	dms.forEach(dm => {
		const senderID = dm.querySelector("#senderID");
		if (senderID.textContent == varThisUserID.textContent) {
			dm.classList.add('position_this_user')
		}
		if (senderID.textContent == varMatchID.textContent) {
			dm.classList.add('position_other_user')
		}

	});

	// Send the message content server side and then refresh the page //
	send_icons.addEventListener("click", () => {
		const id = varMatchID.textContent

		const form_data = {
			text: text_area.value
		};
		fetch(`/message/?match_id=${id}`, {
			method: "POST",
			body: JSON.stringify(form_data),
			headers: {"Content-Type": "application/json"}
		})
		.then(response => {
			const match_id = varMatchID.textContent
			fetch(`/message/?match_id=${match_id}`, {
				method: "GET",
				headers: {"Content-Type": "application/json"}
			})

			.then(response => {
				window.location.href = response.url;
			});
		});

	});

	home.addEventListener("click", () => {
		window.location.href = '/dashboard/';
	});

	const refreshtimer = setTimeout(refresh, refreshTime);

	// Refresh the page after a certain time //
	function refresh () {
		window.location.reload();
	}


});

