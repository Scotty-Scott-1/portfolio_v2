
document.addEventListener("DOMContentLoaded", function() {
	const popbutton = document.getElementById("pp");
	const pref_icon = document.getElementById("prefs");
	const camera = document.getElementById("camera");
	let profile_pic = document.getElementById("pp");
	const heartButton = document.getElementById("heart");
	const isActive = document.getElementById("is_active");
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
		if (isActive.textContent === "False") {
			alert("Update your preferences")
			return
		}
		window.location.href="/swipe/"
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
		const pop = document.getElementById("popover")
		if (pop.style.display === "none") {
			pop.style.display= "block";
			pop.classList.remove("hidden");
		}
		else {
			pop.classList.add("hidden");
			pop.style.display = "none";
		}
	}
