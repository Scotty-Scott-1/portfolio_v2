
document.addEventListener("DOMContentLoaded", function() {
	const signInButton = document.getElementById("signin");
	let latitude;
	let longitude;
	signInButton.addEventListener("click", () => {

		if ("geolocation" in navigator) {
			navigator.geolocation.getCurrentPosition((postiton) => {
					latitude = postiton.coords.latitude;
					longitude = postiton.coords.longitude;
					console.log(latitude);
					console.log(longitude);
					const form_data = {
						user_name: document.querySelector('input[name="user_name"]').value,
						user_password: document.querySelector('input[name="password"]').value,
						latitude: latitude,
						longitude: longitude,

					};
					fetch("/signin", {
						method: "POST",
						body: JSON.stringify(form_data),
						headers: {"Content-Type": "application/json"}

					})

					.then(response => response.json())
					.then(data =>window.location.href = "/new_match_passive/")
					.catch(error => console.error('Error:', error));
				});

		} else {
			console.log("geolocation not supported")
		}

	});

});




