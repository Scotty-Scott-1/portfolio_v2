
document.addEventListener("DOMContentLoaded", function() {
	const minAge = document.getElementById("min_age");
	const agevalue = document.getElementById("age_value");
	const maxAge = document.getElementById("max_age");
	const maxAgeValue = document.getElementById("age_value_max");
	const distannce = document.getElementById("distance");
	const distanceValue = document.getElementById("distance_value");
	const saveButton = document.getElementById("save-button");
	const backButton = document.getElementById("back-button");

	minAge.addEventListener("input" , () => {
		// Move the max age slider if min age is the same //
		agevalue.textContent = minAge.value;
		if(minAge.value > maxAge.value) {
			maxAge.value = minAge.value;
			maxAgeValue.textContent = minAge.value;
		}
	});

	maxAge.addEventListener("input", () => {
		maxAgeValue.textContent = maxAge.value;

	});

	distannce.addEventListener("input", () => {
		distanceValue.textContent = distannce.value;
	});

	saveButton.addEventListener("click", () => {
		makeRequest();
	});

	backButton.addEventListener("click", () => {
		window.location.href="/dashboard/"
	});




});

function makeRequest() {
	// Get form data and send server side //

	const form_data = {
		min_age: document.querySelector('input[name="min_age"]').value,
		max_age: document.querySelector('input[name="max_age"]').value,
		distance: document.querySelector('input[name="distance"]').value,
		intentions: document.querySelector('#intent').value,
		gender: document.querySelector('#gender').value
	};

	fetch("/preferences/", {
		method: "POST",
		body: JSON.stringify(form_data),
		headers: {"Content-Type": "application/json"}

	})

	.then(response => response.json())
	.then(data => {
		console.log(data);
		alert("prefernces updated");
		window.location.href="/dashboard/"
	})
	.catch(error => console.error('Error:', error));
}
