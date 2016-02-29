var plot = function (p) {
	var socket;

	var lsps = [];
	var plots = [];
	var name = ['NY_SF_1',
				'NY_SF_2',
				'NY_SF_3',
				'NY_SF_4',
				'SF_NY_1',
				'SF_NY_2',
				'SF_NY_3',
				'SF_NY_4'];

	var mySQLUpdate = 0;
	var toShow = 0;

	var width;
	var height;

	p.setup = function() {
		const canvasHolder = p.select('#plot-main'),
		      width = canvasHolder.width,
		      height = canvasHolder.height;
		canvas = p.createCanvas(width, height).parent('plot-main');

		p.frameRate(25);

		for (var i = 0; i < 8; i++) {
			var _plot = {
				x: width*0.1,
				y: height*0.1,
				w: width*0.9,
				h: height*0.9,
				bw: [0,0,0,0,0,0,0,0,0,0],
				ls: [0,0,0,0,0,0,0,0,0,0],
				latency: [0,0,0,0,0,0,0,0,0,0]
			}
			plots.push(_plot);
		}

		socket = io.connect('http://localhost:8080');

		socket.on('mysql_lsps_answer', function (data) {
			lsps = data;

			for (var i = 0; i < 8; i++) {
				plots[i].bw.shift();
				plots[i].bw.push(lsps[i].bandwidth/1000.0);
				plots[i].latency.shift();
				plots[i].latency.push(lsps[i].latency/400.0);
				plots[i].ls.shift();
				plots[i].ls.push(lsps[i].loss_rate);
				// console.log(plots[i].bw);
			}
		});

		socket.emit('mysql_lsps');

		// var flow = {
		// 	health: p.random(1)
		// }
		// flows.push(flow);

		// for (var i = 0; i < flows.length; i++) {
		// 	plots[i].ys.push(flows[i].health);
		// }
	}

	p.draw = function () {
		if (lsps.length == 8) {
			if (mySQLUpdate < 125) {
				mySQLUpdate++;
			} else {
				mySQLUpdate = 0;
				socket.emit('mysql_lsps');
			}
		}

		p.background(255);

		plot(toShow);
	}

	p.keyPressed = function () {
		// console.log(p.key + " pressed.");
		if (p.key > 0 && p.key < 9) {
			toShow = p.key-1;
		}
		return false;
	}

	function plot(index) {
		if (lsps.length == 0) return

		for (var i = 0; i < plots[index].bw.length; i++) {
			p.stroke(255,0,0);
			p.strokeWeight(3);
			// console.log(plots[index].bw);
			p.line(
				plots[index].x+plots[index].w*0.1*(i-1),
				plots[index].h-plots[index].h*plots[index].bw[i-1],
				plots[index].x+plots[index].w*0.1*i,
				plots[index].h-plots[index].h*plots[index].bw[i]);
			p.stroke(0,125,0);
			p.strokeWeight(3);
			// console.log(plots[index].bw);
			p.line(
				plots[index].x+plots[index].w*0.1*(i-1),
				plots[index].h-plots[index].h*plots[index].ls[i-1],
				plots[index].x+plots[index].w*0.1*i,
				plots[index].h-plots[index].h*plots[index].ls[i]);
			p.stroke(0,0,255);
			p.strokeWeight(3);
			// console.log(plots[index].bw);
			p.line(
				plots[index].x+plots[index].w*0.1*(i-1),
				plots[index].h-plots[index].h*plots[index].latency[i-1],
				plots[index].x+plots[index].w*0.1*i,
				plots[index].h-plots[index].h*plots[index].latency[i]);
		}

		// printing bandwidth
		p.textSize(20);
		p.fill(255, 0, 0);
		p.stroke(255, 0, 0);
		p.strokeWeight(1);
		p.text("bandwidth: " + lsps[index].bandwidth + " Mbps", plots[index].w*0.8, plots[index].h-plots[index].h*plots[index].bw[9]);

		// printing loss rate
		p.textSize(20);
		p.fill(0, 125, 0);
		p.stroke(0, 125, 0);
		p.strokeWeight(1);
		p.text("loss rate: " + (lsps[index].loss_rate*100) + "%", plots[index].w*0.8, plots[index].h-plots[index].h*plots[index].ls[9]);

		// printing latency
		p.textSize(20);
		p.fill(0, 0, 255);
		p.stroke(0, 0, 255);
		p.strokeWeight(1);
		p.text("latency: " + (lsps[index].latency) + "ms", plots[index].w*0.8, plots[index].h-plots[index].h*plots[index].latency[9]);

		// printing title
		p.textSize(30);
		p.fill(0);
		p.stroke(0);
		p.strokeWeight(2);
		p.text(name[index], plots[index].w/2, 30);

		// printing limits
		p.textSize(20);
		p.fill(255, 0, 0);
		p.stroke(255, 0, 0);
		p.strokeWeight(2);
		p.text("1 Gb", 0, 20);

		p.textSize(20);
		p.fill(255, 0, 0);
		p.stroke(255, 0, 0);
		p.strokeWeight(2);
		p.text("0 Gb", 0, plots[index].h-20);

		p.textSize(20);
		p.fill(0, 125, 0);
		p.stroke(0, 125, 0);
		p.strokeWeight(2);
		p.text("100%", 50, 20);

		p.textSize(20);
		p.fill(0, 125, 0);
		p.stroke(0, 125, 0);
		p.strokeWeight(2);
		p.text("0%", 60, plots[index].h-20);

		p.textSize(20);
		p.fill(0, 0, 255);
		p.stroke(0, 0, 255);
		p.strokeWeight(2);
		p.text("400ms", 120, 20);

		p.textSize(20);
		p.fill(0, 0, 255);
		p.stroke(0, 0, 255);
		p.strokeWeight(2);
		p.text("0ms", 120, plots[index].h-20);
	}
}