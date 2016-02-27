var apps = function (p) {
	// socket connect to server
	var socket;

	// elements in the topology
	var nodes = [];
	var links = [];
	var lsps = [];
	var flows = [];

	// color schema
	var colors = [
	'rgba(0,64,16,0.5)',
	'rgba(0,18,229,0.5)',
	'rgba(127,1,0,0.5)',
	'rgba(191,149,0,0.5)',
	'rgba(255,0,0,0.5)',
	'rgba(225,118,0,1)',
	'rgba(101,0,127,1)',
	'rgba(0,192,229,0.5)'
	];

	// counter for northstar update
	var northStarUpdate = 0;
	var redisUpdate = 0;
	var mySQLUpdate = 0;

	// size of canvas
	var width;
	var height;

	// array of buttons
	var buttons = [];

	// mouse press event handler
	function onMousePressed() {
		for (var i = 0; i < buttons.length; i++) {
			if (p.mouseX > buttons[i].l && p.mouseX < buttons[i].r && p.mouseY > buttons[i].u && p.mouseY < buttons[i].b) {
				if (buttons[i].show) {
					buttons[i].show = false;
				} else {
					buttons[i].show = true;
				}
			}
		}
	}

	function arrow(x1, y1, x2, y2, length) {
		var angle = p.atan2(y2-y1, x2-x1);
		// console.log(angle + " from (" + x1 + "," + y1 + ") to (" + x2 + "," + y2 + ")");
		p.push();
		p.translate(x1,y1);
		p.rotate(angle);
		p.beginShape();
		p.vertex(0,-2);
		p.vertex(5*length,-2);
		p.vertex(5*length,-6);
		p.vertex(9*length,0);
		p.vertex(5*length,6);
		p.vertex(5*length,2);
		p.vertex(0,2);
		p.endShape(p.CLOSE);
		p.pop();
	}

	// Visualization of topology in a Wide Area Network
	p.setup = function () {
		// console.log('in apps');
		// creat canvas
		const canvasHolder = p.select('#app-main'),
		      width = canvasHolder.width,
		      height = canvasHolder.height;
		// console.log(width);
		// console.log(height);
		canvas = p.createCanvas(width, height).parent('app-main');
		canvas.mousePressed(onMousePressed);

		// set frame rate as 25 fps
		p.frameRate(25);

		// Add buttons
		for (var i = 0; i < 4; i++) {
			var button = {
				l: width*0.91,
				r: width*0.91+width*0.07,
				u: height*0.2*i,
				b: height*0.2*i+height*0.1,
				show: false
			}
			buttons.push(button);
		}

		for (var i = 0; i < 4; i++) {
			var button = {
				l: width*0.02,
				r: width*0.02+width*0.07,
				u: height*0.2*i,
				b: height*0.2*i+height*0.1,
				show: false
			}
			buttons.push(button);
		}

		// Establish socket between browser and server
		socket = io.connect('http://localhost:8080');
		socket.emit('northstar');

		socket.on('welcome', function(data) {
			// console.log(data.welcome);
		});

		socket.on('nodes', function(data) {
			nodes = data;
			for (var i = 0; i < 8; i++) {
				nodes[i].x = p.map(nodes[i].longtitude, -130, -70, width*0.2, width*0.8);
				nodes[i].y = p.map(-nodes[i].latitude, -45, -25, height*0.2, height*0.8);
			}
			// console.log(nodes);
			// console.log('New nodes information received');
		});

		socket.on('links', function(data) {
			// console.log(data);
			links = data;
			// console.log('New links information received');
		})

		socket.on('lsps', function(data) {
			// console.log(data);
			lsps = data
			// console.log('New LSPs information received');

			flows = [];
			for (var i = 0; i < 8; i++) {
				// console.log(lsps[i]);
				console.log('Flow information updated');
				var flow = {
					lsps: [lsps[i]],
					health: i / 4.0,
					show: true
				}
				flows.push(flow);
			}
			// console.log(flows);
		})

		socket.on('flows', function(data) {
			flows = data;
		});
	}

	p.draw = function () {

		// counting whether to update northstar informations && redis information
		if (nodes.length == 8 && links.length == 15 && lsps.length == 8) {
			if (northStarUpdate < 75) {
				northStarUpdate++;
			} else {
				socket.emit('northstar_update');
				northStarUpdate = 0;
			}

			if (redisUpdate < 750) {
				redisUpdate++;
			} else {
				socket.emit('redis_update');
				redisUpdate = 0;
			}

			if (mySQLUpdate < 75) {
				mySQLUpdate++;
			} else {
				// socket.emit('mysql_update');

				mySQLUpdate = 0;
			}
		}

		p.background(255);

		// Links
		for (var i = 0; i < links.length; i++) {
			// console.log('drawing links');
			// console.log(links[i]);
			p.stroke(230,230,230);
			p.strokeWeight(5);
			p.line(nodes[links[i].endA-1].x, nodes[links[i].endA-1].y+5, nodes[links[i].endZ-1].x, nodes[links[i].endZ-1].y+5);
			p.line(nodes[links[i].endA-1].x, nodes[links[i].endA-1].y-5, nodes[links[i].endZ-1].x, nodes[links[i].endZ-1].y-5);
			p.stroke('rgba(0,0,0,0.5)');
			p.strokeWeight(5*links[i].utilA2Z);
			p.line(nodes[links[i].endA-1].x, nodes[links[i].endA-1].y+5, nodes[links[i].endZ-1].x, nodes[links[i].endZ-1].y+5);
			p.fill('rgba(0,0,0,'+links[i].utilA2Z+')');
			p.noStroke();
			arrow(nodes[links[i].endA-1].x, nodes[links[i].endA-1].y+5, nodes[links[i].endZ-1].x, nodes[links[i].endZ-1].y+5, 10);
			p.stroke('rgba(0,0,0,0.5)');
			p.strokeWeight(5*links[i].utilZ2A);
			p.line(nodes[links[i].endA-1].x, nodes[links[i].endA-1].y-5, nodes[links[i].endZ-1].x, nodes[links[i].endZ-1].y-5);
			p.fill('rgba(0,0,0,'+links[i].utilZ2A+')');
			p.noStroke();
			arrow(nodes[links[i].endZ-1].x, nodes[links[i].endZ-1].y-5, nodes[links[i].endA-1].x, nodes[links[i].endA-1].y-5, 10);
		}

		// Nodes
		p.stroke(50);
		p.strokeWeight(1);
		for (var i = 0; i < nodes.length; i++) {
			p.fill(100);
			p.ellipse(nodes[i].x, nodes[i].y, 25, 25);
			p.textSize(24);
			p.fill(0, 102, 153);
			p.text(nodes[i].name, nodes[i].x, nodes[i].y+25);
			// console.log(nodes);
		}

		// LSPs
		// console.log(buttons);
		for (var i = 0; i < lsps.length; i++) {
			// console.log(colors);
			// if (buttons[i].show) {
			if (false) {
				for (var j = 0; j < lsps[i].links.length; j++) {
					p.stroke(colors[i]);
					p.strokeWeight(4);
					p.line(
						nodes[links[lsps[i].links[j]].endA-1].x,
						nodes[links[lsps[i].links[j]].endA-1].y+i*2,
						nodes[links[lsps[i].links[j]].endZ-1].x,
						nodes[links[lsps[i].links[j]].endZ-1].y+i*2);
				}
			}

			// p.stroke(0);
			// p.strokeWeight(1);
			// if (buttons[i].show) {
			// 	p.fill(colors[i]);
			// } else {
			// 	p.fill(255);
			// }

			// var width = p.width;
			// var height = p.height;
			// // console.log(width + " " + height);
			// var w = width*0.07;
			// var h = height*0.1;
			// if (i < 4) {
			// 	// console.log('drawing button ' + (width*0.82) + " " + (height*0.3+height*0.2*i) + " " + w + " " + h);
			// 	p.rect(width*0.82, height*0.3+height*0.2*i, w, h);
			// 	p.textSize(h*0.2);
			// 	p.fill(0);
			// 	p.strokeWeight(1);
			// 	p.text(lsps[i].name, width*0.82, height*0.3+height*0.2*i, w, h);
			// }
			// if (i >= 4) {
			// 	// console.log('drawing button');
			// 	p.rect(width*0.91, height*0.3+height*0.2*(i-4), w, h);
			// 	p.textSize(h*0.2);
			// 	p.fill(0);
			// 	p.strokeWeight(1);
			// 	p.text(lsps[i].name, width*0.91, height*0.3+height*0.2*(i-4), w, h);
			// }
		}

		// flows
		// console.log(flows.length);
		for (var i = 0; i < flows.length; i++) {
			if (buttons[i].show) {
				// console.log(flows[i].lsps);
				for (var j = 0; j < flows[i].lsps.length; j++) {
					// console.log(flows[i].lsps[j].name);
					for (var k = 0; k < flows[i].lsps[j].links.length; k++) {
						// console.log("trying to draw flows");
						p.stroke(colors[i]);
						p.strokeWeight(4);
						p.line(
							nodes[links[flows[i].lsps[j].links[k]].endA-1].x,
							nodes[links[flows[i].lsps[j].links[k]].endA-1].y+i*2,
							nodes[links[flows[i].lsps[j].links[k]].endZ-1].x,
							nodes[links[flows[i].lsps[j].links[k]].endZ-1].y+i*2);
					}
				}
			}

			var width = p.width;
			var height = p.height;
			// console.log(width + " " + height);
			var w = width*0.07;
			var h = height*0.1;
			if (buttons[i].show) {
				p.fill(colors[i]);
			} else {
				p.fill(255);
			}
			p.stroke(0);
			p.strokeWeight(1);
			if (i < 4) {
				// console.log('drawing button ' + (width*0.82) + " " + (height*0.3+height*0.2*i) + " " + w + " " + h);
				p.rect(width*0.91, height*0.2*i, w, h);
				p.textSize(h*0.2);
				p.fill(0);
				p.strokeWeight(1);
				p.text("Flow " + i, width*0.91, height*0.2*i, w, h);
			}
			if (i >= 4) {
				// console.log('drawing button');
				p.rect(width*0.02, height*0.2*(i-4), w, h);
				p.textSize(h*0.2);
				p.fill(0);
				p.strokeWeight(1);
				p.text("Flow " + i, width*0.02, height*0.2*(i-4), w, h);
			}

			p.stroke(colors[i]);
			p.strokeWeight(4);
			if (i < 4) {
				p.line(width*0.91, height*0.2*i+h/2.0, nodes[6].x, nodes[6].y);
			}
			if (i >= 4) {
				p.line(width*0.02+w, height*0.2*(i-4)+h/2.0, nodes[0].x, nodes[0].y);
			}
		}
	}
}