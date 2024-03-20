document.addEventListener("DOMContentLoaded", function() {

	const home = document.getElementById("home");
	const candidate = document.querySelectorAll(".card");


	home.addEventListener("click", () => {
		window.location.href = '/dashboard/';
	});

	candidate.forEach((candidate) => {
		const bin = candidate.querySelector(".bin")
		const message = candidate.querySelector(".message")

		bin.addEventListener("click", () =>{
			// Send form data server side //
			const id = candidate.querySelector(".not_visable")
			const form_data = {
				id: id.textContent,
			};
			fetch('/view_matches/', {
				method: "DELETE",
				body: JSON.stringify(form_data),
				headers: {"Content-Type": "application/json"}

			})
			.then(result => {
				return result.text();
			})
			.then(result2 => {
				console.log(result2)
				alert("this match has been deleted")
				window.location.href = "/view_matches/"
			});
		});

		message.addEventListener("click", () => {
			// Send match ID server side as an arg //
			const id = candidate.querySelector(".not_visable")
			const match_id = id.textContent
			fetch(`/message/?match_id=${match_id}`, {
				method: "GET",
				headers: {"Content-Type": "application/json"}
			})

			.then(response => {
				window.location.href = response.url;
			});
		});




	});
});
