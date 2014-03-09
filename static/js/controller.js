amoeba.controller("Amoeba", ["$scope", "$timeout",
	function($scope, $timeout) {
	
	// Whether the WebSocket connection is open
	$scope.connected = false;

	// Whether we have control
	$scope.control = false;

	// Whether control is available
	$scope.controlAvailable = false;

	// Number of users connected
	$scope.userCount = 0;

	// Whether the camera is on
	$scope.camera = false;

	// Toggle camera state
	$scope.toggleCamera = function() {
		if ($scope.camera) {
			$scope.dispatchMessage("CAMERA_OFF");
		} else {
			$scope.dispatchMessage("CAMERA_ON");
		}
	}
	$scope.enableCamera = function() {
		$scope.camera = true;
	}
	$scope.disableCamera = function() {
		$scope.camera = false;
		$scope.image = false;
	}

	// Managing control
	$scope.yield = function() {
		$scope.dispatchMessage("COMMAND_YIELD");
	}
	$scope.takeover = function() {
		$scope.dispatchMessage("COMMAND_TAKEOVER");
	}

	// Which way we are driving
	$scope.drive = "stop";

	// Robot action command mapping
	$scope.forwards = function() {
		$scope.dispatchMessage("DRIVE_FORWARD");
	}
	$scope.left = function() {
		$scope.dispatchMessage("DRIVE_LEFT");
	}
	$scope.right = function() {
		$scope.dispatchMessage("DRIVE_RIGHT");
	}
	$scope.stop = function() {
		$scope.dispatchMessage("DRIVE_STOP");
	}
	$scope.light = {
		"top": {
			"on": function() {
				$scope.dispatchMessage("LIGHT_TOP_ON");
			},
			"off": function() {
				$scope.dispatchMessage("LIGHT_TOP_OFF");
			}
		},
		"front": {
			"on": function() {
				$scope.dispatchMessage("LIGHT_FRONT_ON");
			},
			"off": function() {
				$scope.dispatchMessage("LIGHT_FRONT_OFF");
			}
		}
	}

	// Panic
	$scope.panic = function() {
		$scope.dispatchMessage("PANIC");
	}

	// The current image
	$scope.image = false;

	// Initialises the server websocket connection
	$scope.init = function() {
		if ($scope.socket) {
			return;
		}
		$scope.socket = new WebSocket("ws://" + window.location.host + "/socket");
		$scope.socket.onclose = function() {
			$scope.socket = false;
			$scope.connected = false;
			$scope.control = false;
			$scope.controlAvailable = false;
			$scope.userCount = 0;
			$scope.$apply();
			$timeout(function() {
				$scope.init();
			}, 1000);
		}
		$scope.socket.onopen = function() {
			$scope.connected = true;
			$scope.$apply();
		}
		$scope.socket.onmessage = function(msg) {
			var data = JSON.parse(msg.data);
			$scope.handleMessage(data);
		}
	}
	// Initialise when the page loads
	$scope.init();

	// Sends a message to the socket, if it is open
	$scope.dispatchMessage = function(cmd, data) {
		var msg = JSON.stringify({ "command": cmd, "data": data });
		if ($scope.socket) {
			$scope.socket.send(msg);
		}
	}

	// Handles a message from server
	$scope.handleMessage = function(message) {
		console.log(message);
		switch(message.command) {
			case "CAMERA_OFF":
				$scope.disableCamera();
				break;
			case "CAMERA_ON":
				$scope.enableCamera();
				break;
			case "CAMERA_IMAGE":
				$scope.image = "data:image/jpeg;base64," + message.data.image;
				break;
			case "COMMAND_USERS":
				$scope.userCount = message.data.count;
				break;
			case "COMMAND_YIELDED":
				$scope.control = false;
				$scope.controlAvailable = message.data.available;
				break;
			case "COMMAND_TAKENOVER":
				$scope.control = true;
				$scope.controlAvailable = false;
				break;
			case "CONTROL_AVAILABLE":
				$scope.controlAvailable = message.data.available;
				break;
			case "DRIVE_FORWARD":
				$scope.drive = "forward";
				break;
			case "DRIVE_LEFT":
				$scope.drive = "left";
				break;
			case "DRIVE_RIGHT":
				$scope.drive = "right";
				break;
			case "DRIVE_STOP":
				$scope.drive = "stop";
				break;
		}
		$scope.$apply();
	}

}]);
