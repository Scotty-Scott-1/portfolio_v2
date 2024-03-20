
document.addEventListener("DOMContentLoaded", function() {
	const saveButton = document.getElementById("save-button");
	const backButton = document.getElementById("back-button");

	saveButton.addEventListener("click", () => {
		makeRequest();
	});

	backButton.addEventListener("click", () => {
		window.location.href="/dashboard/"
	});




});

function makeRequest() {
	// Get form data and send server side//

	const form_data = {
		first_name: document.querySelector('#first_name').value,
		last_name: document.querySelector('#last_name').value,
		date_of_birth: document.querySelector('#date_of_birth').value,
		email: document.querySelector('#email').value,
		user_name: document.querySelector('#user_name').value,
		gender: document.querySelector('#gender').value,
		bio: document.querySelector('#bio').value,
	};

	fetch("/update-user-info/", {
		method: "POST",
		body: JSON.stringify(form_data),
		headers: {"Content-Type": "application/json"}

	})

	.then(response => response.json())
	.then(data => {
		console.log(data);
		alert("Profile info updated");
		window.location.href="/dashboard/"
	})
	.catch(error => console.error('Error:', error));
}
