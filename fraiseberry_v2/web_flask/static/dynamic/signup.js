
document.addEventListener("DOMContentLoaded", function() {
	const signInButton = document.getElementById("signin");
	let latitude;
	let longitude;
	signInButton.addEventListener("click", () => {

		// get the users coordinates //
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
					.then(result => {
						return result.text();
					})
					.then(result2 => {
						console.log(result2);
						if (result2 == "email not verified") {
							window.location.href = "/verify_email/"
						}
						if (result2 == "email verified") {
							window.location.href = "/new_match_passive/"
						}
						if (result2 == "incorrect username or password") {
							alert("incorrect username or password")
						}


					});
			});
		} else {
			alert("geolocation not supported")
		}

	});

});




