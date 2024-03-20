document.addEventListener("DOMContentLoaded", function() {

	const verifyButton = document.getElementById("verify");
	const no1 = document.getElementById("no1");
	const no2 = document.getElementById("no2");
	const no3 = document.getElementById("no3");
	const no4 = document.getElementById("no4");
	const anotherCode = document.getElementById("another_code")

	no1.addEventListener("input", () => {
		// Add styles when a value is typed //
		let value = no1.value;
		if (value == "") {
			no1.style.borderStyle = "dotted"
			no1.style.borderColor = "#000000"
		} else {
			no1.style.borderColor = "#189921"
			no1.style.borderStyle = "solid"
		}
	});

	no2.addEventListener("input", () => {
		// Add styles when a value is typed //
		let value = no2.value;
		if (value == "") {
			no2.style.borderStyle = "dotted"
			no2.style.borderColor = "#000000"
		} else {
			no2.style.borderColor = "#189921"
			no2.style.borderStyle = "solid"
		}
	});

	no3.addEventListener("input", () => {
		// Add styles when a value is typed //
		let value = no3.value;
		if (value == "") {
			no3.style.borderStyle = "dotted"
			no3.style.borderColor = "#000000"
		} else {
			no3.style.borderColor = "#189921"
			no3.style.borderStyle = "solid"
		}
	});

	no4.addEventListener("input", () => {
		// Add styles when a value is typed //
		let value = no4.value;
		if (value == "") {
			no4.style.borderStyle = "dotted"
			no4.style.borderColor = "#000000"
		} else {
			no4.style.borderColor = "#189921"
			no4.style.borderStyle = "solid"
		}
	});

	anotherCode.addEventListener("click", () => {
		// Refresh the page//
		alert("a new code has been sent")
		window.location.href = "/verify_email/"
	});

	verifyButton.addEventListener("click", () => {
		// Send form data server side//
		const form_data = {
			no1: no1.value,
			no2: no2.value,
			no3: no3.value,
			no4:no4.value
		};

		fetch("/verify_email/", {
			method: "POST",
			body: JSON.stringify(form_data),
			headers: {"Content-Type": "application/json"}
		})

		.then(result => {
			return result.text();
		})
		.then(result2 => {
			console.log(result2);
			if (result2 == "incorrect code") {
				alert("the code was incorrect. A new code has been sent")
				window.location.href = "/verify_email/"
			}
			if (result2 == "email has been verified") {
				window.location.href = "/new_match_passive/"
			}
		});
	});


});
