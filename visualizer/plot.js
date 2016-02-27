var plot = function (p) {
	var socket;

	var flows = [];
	var plots = [];

	var mySQLUpdate = 0;

	var width;
	var height;

	p.setup = function() {
		const canvasHolder = p.select('#plot-main'),
		      width = canvasHolder.width,
		      height = canvasHolder.height;
		canvas = p.createCanvas(width, height).parent('plot-main');

		p.frameRate(25);

		socket = io.connect('http://localhost:8080');

		socket.on('flows', function (data) {
			flows = data;
		});

		var _plot = {
			x: 0,
			y: 0,
			w: width,
			h: height,
			ys: [0,0,0,0,0,0,0,0,0,0],
			counter: 0
		}
		plots.push(_plot);

		var flow = {
			health: p.random(1)
		}
		flows.push(flow);

		for (var i = 0; i < flows.length; i++) {
			plots[i].ys.push(flows[i].health);
		}
	}

	p.draw = function () {
		if (flows.length == 1) {
			if (mySQLUpdate < 75) {
				mySQLUpdate++;
			} else {
				mySQLUpdate = 0;

				for (var i = 0; i < flows.length; i++) {
					flows[i].health = p.random(1);
					plots[i].ys.shift();
					plots[i].ys.push(flows[i].health);
					console.log("Update health: " + flows[i].health);
				}
			}
		}

		p.background(255);

		for (var i = 0; i < flows.length; i++) {
			plot(i);
		}
	}

	function plot(index) {
		for (var i = 1; i < plots[index].ys.length; i++) {
			p.stroke(0);
			p.strokeWeight(3);
			p.line(
				plots[index].x+plots[index].w*0.1*(i-1),
				plots[index].h-plots[index].h*plots[index].ys[i-1],
				plots[index].x+plots[index].w*0.1*i,
				plots[index].h-plots[index].h*plots[index].ys[i]);
		}
	}
}