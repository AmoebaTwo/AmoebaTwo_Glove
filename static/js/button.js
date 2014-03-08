amoeba.directive("smartButton", [function() {

	var t = function(callme) {
		return function(e) {
			e.preventDefault();
			callme();
		}
	}

	return {
		"restrict": "A",
		"scope": {
			"touchStart": "&",
			"touchEnd": "&",
			"clickStart": "&",
			"clickEnd": "&"
		},
		"link": function($scope, element) {
			element.on("touchstart", t($scope.touchStart)).on("touchend", t($scope.touchEnd))
				.on("touchcancel", t($scope.touchEnd))
				.on("mousedown", $scope.clickStart).on("mouseup", $scope.clickEnd);
		}
	}

}]);
