amoeba.factory("robot", ["$http",
	function($http) {

	return {
		"forwards": function() {
			return $http({ "method": "GET", "url": "/drive/forwards" });
		},
		"left": function() {
			return $http({ "method": "GET", "url": "/drive/left" });
		},
		"right": function() {
			return $http({ "method": "GET", "url": "/drive/right" });
		},
		"stop": function() {
			return $http({ "method": "GET", "url": "/drive/stop" });
		},
		"light": {
			"top": {
				"on": function() {
					return $http({ "method": "GET", "url": "/light/top/on" });
				},
				"off": function() {
					return $http({ "method": "GET", "url": "/light/top/off" });
				}
			},
			"front": {
				"on": function() {
					return $http({ "method": "GET", "url": "/light/front/on" });
				},
				"off": function() {
					return $http({ "method": "GET", "url": "/light/front/off" });
				}
			}
		}
	}

}]);
