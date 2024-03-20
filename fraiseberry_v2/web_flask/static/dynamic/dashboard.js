
document.addEventListener("DOMContentLoaded", function() {
	const popbutton = document.getElementById("pp");
	const pref_icon = document.getElementById("prefs");
	const camera = document.getElementById("camera");
	let profile_pic = document.getElementById("pp");
	const heartButton = document.getElementById("heart")
	const userIcon = document.getElementById("user_icon");
	const mailIcon = document.getElementById("notifications");
	const messageIcon = document.getElementById("message");

	popbutton.addEventListener("click", () => {
		showPopover();
	});

	pref_icon.addEventListener("click", () => {
		window.location.href="/preferences/"
	});

	camera.addEventListener("click", () => {
		window.location.href="/camera/"
	});

	profile_pic.src = ""

	heartButton.addEventListener("click", () => {
		alert("update your profile pic")
	})

	userIcon.addEventListener("click", () => {
		window.location.href="/update-user-info/"
	});

	mailIcon.addEventListener("click", () => {
		window.location.href="/new_match/"
	});

	messageIcon.addEventListener("click", () => {
		window.location.href="/view_matches/"
	});

});





	function showPopover () {
		// Show the popover//
		const pop = document.getElementById("popover")
		if (pop.style.display === "none") {
			pop.style.display= "block";
			pop.classList.remove("hidden");
		}
		// Hide the popover //
		else {
			pop.classList.add("hidden");
			pop.style.display = "none";
		}
	}
