amoeba.controller("Amoeba", ["$scope", "robot",
	function($scope, robot) {

	$scope.forwards = robot.forwards;
	$scope.left = robot.left;
	$scope.right = robot.right;
	$scope.stop = robot.stop;
	$scope.light = {
		"top": {
			"on": robot.light.top.on,
			"off": robot.light.top.off
		},
		"front": {
			"on": robot.light.front.on,
			"off": robot.light.front.off
		}
	}

	$scope.image = false;

	$scope.init = function() {
		$scope.socket = new WebSocket("ws://" + window.location.host + "/image");
		$scope.socket.onmessage = function(msg) {
			$scope.image = "data:image/jpeg;base64," + msg.data;
			$scope.$apply();
		}
	}
	$scope.init();

}]);
