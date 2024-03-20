
document.addEventListener("DOMContentLoaded", function() {
	const candidates = document.querySelectorAll(".card");
	let index = 0;
	const home = document.getElementById("home");

	home.addEventListener("click", () => {
		window.location.href = '/dashboard/';
	});

	function show(index) {
		// Add a like or pass the current canidate//
		candidates.forEach((candidate, idx) => {
			if(idx === index) {
				candidate.classList.add('active')
				let yes = candidate.querySelector("#yes");
				let no = candidate.querySelector("#no");

				yes.addEventListener("click", () => {
					index++;

					show(index);
					console.log(index);

					user_name_element = candidate.querySelector("#card_info_2");
					user_name = user_name_element.textContent;
					const form_data = {
						canidate_user_name: user_name,
					};
					fetch('/swipe/', {
						method: "POST",
						body: JSON.stringify(form_data),
						headers: {"Content-Type": "application/json"}

					})
					.then(result => {
						return result.text();
					})
					.then(result2 => {
						console.log(result2);
						if (result2 == "New Match") {
							window.location.href = '/new_match/';
						}
						if (index >= candidates.length && result2 != "New Match") {
							index = 0;
							window.location.href = '/swipe/';
						}
					});

				});


				no.addEventListener("click", () => {
					index++;
					if (index >= candidates.length) {
						index = 0;
						window.location.href = '/swipe/';
					}
					show(index);
					console.log(index);
				});
			} else {
				candidate.classList.remove('active')
			}
		});
	}

	show(index);
});

function like() {

}

