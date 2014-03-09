amoeba.controller("Amoeba", ["$scope", "$timeout",
	function($scope, $timeout) {
	
	// The current image
	$scope.image = false;
	
	// The current state from the robot
	$scope.state = false;
	
	// The current socket
	$scope.socket = false;
	
	// Whether we are attempting to reconnect
	$scope.reconnecting = false;
	
	// Whether to show admin box
	$scope.showAdmin = false;

	// Initialises the server websocket connection
	$scope.connect = function(name) {
		if (!name) {
			name = "";
		}
		if ($scope.socket) {
			return;
		}
		$scope.socket = new WebSocket("ws://" + window.location.host + "/socket/" + name);
		$scope.reconnecting = false;
		$scope.socket.onclose = function() {
			$scope.socket = false;
			$scope.state = false;
			$scope.reconnecting = true;
			$scope.$apply();
			$timeout(function() {
				$scope.connect(name);
			}, 1000);
		}
		$scope.socket.onmessage = function(msg) {
			var data = JSON.parse(msg.data);
			$scope.handleMessage(data);
		}
	}

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
			case "CAMERA_IMAGE":
				$scope.image = "data:image/jpeg;base64," + message.data.image;
				break;
			case "STATE":
				$scope.state = message.data;
				break;
		}
		$scope.$apply();
	}
	
	$scope.execCommand = function(cmd) {
		return function() {
			$scope.dispatchMessage(cmd);
		}
	}
	
	// Robot controls
	$scope.forward = $scope.execCommand("DRIVE_FORWARD");
	$scope.left = $scope.execCommand("DRIVE_LEFT");
	$scope.right = $scope.execCommand("DRIVE_RIGHT");
	$scope.stop = $scope.execCommand("DRIVE_STOP");
	$scope.panic = $scope.execCommand("PANIC");
	$scope.frontLightOn = $scope.execCommand("LIGHT_FRONT_ON");
	$scope.frontLightOff = $scope.execCommand("LIGHT_FRONT_OFF");
	$scope.topLightOn = $scope.execCommand("LIGHT_TOP_ON");
	$scope.topLightOff = $scope.execCommand("LIGHT_TOP_OFF");
	$scope.takeover = $scope.execCommand("COMMAND_TAKEOVER");
	$scope.yield = $scope.execCommand("COMMAND_YIELD");
	$scope.unpanic = $scope.execCommand("UNPANIC");

	$scope.toggleCamera = function() {
		if ($scope.state.client.camera_on) {
			$scope.dispatchMessage("CAMERA_OFF");
		} else {
			$scope.dispatchMessage("CAMERA_ON");
		}
	}
	
	// Elevate to admin
	$scope.elevate = function(password) {
		$scope.dispatchMessage("ELEVATE", { "password": password });
	}
}]);
