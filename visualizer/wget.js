var wget = function (p) {
	var socket;

	var wgets = [];

	var mySQLUpdate = 0;

	var width;
	var height;
	var maxRate = 0;

	var mButton;

	p.setup = function () {
		const canvasHolder = p.select('#plot2-main'),
			  width = canvasHolder.width,
			  height = canvasHolder.height;
		canvas = p.createCanvas(width, height).parent('plot2-main');
		canvas.mousePressed(onMousePressed);

		p.frameRate(25);

		mButton = {
			l: width*0.02,
			r: width*0.12,
			u: height*0.02,
			b: height*0.12,
			enabled: true
		}

		socket = io.connect('http://localhost:8080');

		socket.on('wget_stat', function (data) {
			// console.log(data);
			wgets = data;

			for (var i = 0; i < wgets.length; i++) {
				if (wgets[i].rate > maxRate) {
					maxRate = wgets[i].rate;
				}
			}

			mButton.enabled = checkButton();
		});
	}

	p.draw = function () {
		if (mButton.enabled == false) {
			if (mySQLUpdate < 50) {
				mySQLUpdate++;
			} else {
				socket.emit('get_wget_stat');
				mySQLUpdate = 0;
			}
		}

		p.background(255);

		drawButton(mButton);
		drawWgets();
	}

	function drawButton(b) {
		if (b.enabled && mouseIn(p.mouseX, p.mouseY, b)) {
			p.stroke(0);
			p.strokeWeight(1);
			p.fill(50,170,200);
			p.rect(b.l, b.u, b.r-b.l, b.b-b.u);

			p.textSize(20);
			p.noStroke();
			p.strokeWeight(1);
			p.fill(0);
			p.text("Test wget", b.l, b.u+20);
		} else if (b.enabled) {
			p.stroke(0);
			p.strokeWeight(1);
			p.fill(70,100,200);
			p.rect(b.l, b.u, b.r-b.l, b.b-b.u);

			p.textSize(20);
			p.noStroke();
			p.strokeWeight(1);
			p.fill(0);
			p.text("Test wget", b.l, b.u+20);
		} else {
			p.stroke(0);
			p.strokeWeight(1);
			p.fill(100);
			p.rect(b.l, b.u, b.r-b.l, b.b-b.u);

			p.textSize(20);
			p.noStroke();
			p.strokeWeight(1);
			p.fill(0);
			p.text("Testing...", b.l, b.u+20);
		}

		p.textSize(20);
		p.noStroke();
		p.strokeWeight(1);
		p.fill(0);
		p.text("Max rate: " + maxRate + " Bbps", b.r+20, b.u+60);
	}

	function mouseIn(mx, my, b) {
		// console.log(i);
		if (mx > b.l && mx < b.r && my > b.u && my < b.b) {
			return true;
		}
	}

	// mouse press event handler
	function onMousePressed() {
		if (p.mouseX > mButton.l && p.mouseX < mButton.r && p.mouseY > mButton.u && p.mouseY < mButton.b) {
			if (mButton.enabled) {
				wgets = [];
				maxRate = 0;
				socket.emit('run_wget');
				mButton.enabled = false;
			}
		}
	}

	function drawWgets() {
		p.stroke(0);
		p.strokeWeight(1);
		p.line(0,p.height*0.12,p.width*0.5,p.height*0.12);

		var len = wgets.length;
		for (var i = 0; i < len; i++) {
			p.stroke(0);
			p.strokeWeight(2);
			var alp = wgets[i].progress/100.0;
			p.fill('rgba(255,65,0,'+alp+')');
			// p.fill(c);
			p.rect(p.width*0.5/len*i, p.height-p.height*0.88*wgets[i].rate/maxRate, p.width*0.5/len, p.height*0.88*wgets[i].rate/maxRate);

			p.textSize(15);
			p.noStroke();
			p.strokeWeight(2);
			p.fill('rgba(255,65,0,'+alp+')');
			p.text(wgets[i].rate, p.width*0.5/len*i, p.height-p.height*0.88*wgets[i].rate/maxRate);

			p.noStroke();
			p.strokeWeight(0);
			p.fill('rgba(0, 255, 200, 0.8)');
			p.rect(p.width*0.6, p.height*(i+0.4)/len, p.width*0.39*wgets[i].progress/100.0, p.height*0.5/len);

			p.stroke(0);
			p.strokeWeight(1);
			p.fill('rgba(255,255,255,0)');
			p.rect(p.width*0.6, p.height*(i+0.4)/len, p.width*0.39, p.height*0.5/len);

			p.textSize(20);
			p.noStroke();
			p.strokeWeight(1);
			p.fill(0);
			p.text(wgets[i].progress+"%", p.width*0.78, p.height*(i+0.8)/len);
		}
	}

	function checkButton() {
		for (var i = 0; i < wgets.length; i++) {
			if (wgets[i].completed == 0) {
				return false;
			}
		}
		return true;
	}
}