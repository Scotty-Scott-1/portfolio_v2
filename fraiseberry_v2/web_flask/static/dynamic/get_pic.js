document.addEventListener("DOMContentLoaded", function() {

	const video = document.getElementById("vid");
	const captureButton = document.getElementById("cap_button");
	const image = document.getElementById("im");
	const save = document.getElementById("save");
	const back = document.getElementById("back");

	// Hide the canvas until it contains an img//
	canvas.style.display = "none";

	// Active video //
	navigator.mediaDevices.getUserMedia({ video: true})
	.then((stream) => {
		video.srcObject = stream
		console.log("video running")
	})
	.catch((error) => {
		console.error("Could not access the camera", error)
	});

	captureButton.addEventListener("click", () => {
		// Capture an image from the video //
		const context = canvas.getContext("2d");
		context.drawImage(video, 0, 0, canvas.width, canvas.height);
		image.src = canvas.toDataURL("image/jpeg");
		canvas.style.display = "block";
		video.style.display = "none";
		captureButton.style.display="none";

		save.style.display = "block";
		back.style.display = "block";

	});

	back.addEventListener("click", () => {
		window.location.href="/dashboard/"
	});

	save.addEventListener("click", () => {
		// Send the img server side and then navigate to dashboard
		fetch("/camera/", {
			method: "POST",
			body: JSON.stringify({ImageData: image.src}),
			headers: {"Content-Type": "application/json"}
		})
		.then(response => {
			response.json()
			window.location.href="/dashboard/"
		})
		.catch(error => {
			console.error("error saving image", error);
		});
	})

});

