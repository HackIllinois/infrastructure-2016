'use strict';

function getWidth() {
    var maxWidth = 1300;
    return (window.innerWidth > maxWidth) ? maxWidth : window.innerWidth;
}

function scaleImages() {
    var ratio = 1.6;

    w   = canvas.width;
    h   = canvas.width / ratio;

    compassX = posX*w;
    compassY = posY*h;
}

function drawClip(x, y) {
    ctx.drawImage(night, 0, 0, w, h);

    sctx.clearRect(0, 0, scratchCanvas.width, scratchCanvas.height);

    sctx.globalCompositeOperation = 'source-over'; //default

    sctx.drawImage(day, 0, 0, w, h);
    sctx.drawImage(compass, compassX, compassY, compassW, compassH);

    sctx.fillStyle = '#fff'; //color doesn't matter, but we want full opacity
    sctx.globalCompositeOperation = 'destination-in';
    sctx.beginPath();
    sctx.arc(x, y, clipRadius, 0, Math.PI*2, true);
    sctx.closePath();
    sctx.fill();

    ctx.drawImage(scratchCanvas, 0, 0);
}

function isCompass(x, y) {
    if(x > compassX &&
       x < compassX + compassW &&
       y > compassY &&
       y < compassY + compassY) {
        return true;
    }
    return false;
}

function clickCompass(x, y) {
    if(isCompass(x, y)) {
        $('#game').removeClass('running');
        $('footer').fadeOut();
        $('#volume').fadeOut();
        var theme = document.getElementById('theme');
        theme.pause();

        $('#compass-wrapper').addClass('found');
        $('#event-title').addClass('found');
        $('#found-title').addClass('found');
        $('#replay').addClass('found');
        $('#landing').fadeIn(800);
    }
}

function draw() {
    rect = canvas.getBoundingClientRect();

    ctx.drawImage(night, 0, 0, w, h);

    drawClip(mouse.x, mouse.y);
    setTimeout(draw, 35);
}

function redraw() {
    scaleImages();

    ctx.canvas.width = getWidth();
    ctx.canvas.height = h;
    clipRadius = canvas.width * 0.04;
}

function setupMouse(canvas, updateCanvas, checkClick, preventDefault) {
    var hook = canvas.addEventListener.bind(canvas);
    hook('mousemove', onMouseMove);

    canvas.addEventListener('click', onMouseClick, false);

    function onMouseMove(e) {
        mouse.x = (e.clientX - rect.left);
        mouse.y = (e.clientY - rect.top);
    }
    function onMouseClick(e) {
        mouse.x = (e.clientX - rect.left);
        mouse.y = (e.clientY - rect.top);
        checkClick(mouse.x, mouse.y);
    }
}

function init() {
    canvas        = document.getElementById('forest');
    ctx           = canvas.getContext('2d');
    scratchCanvas = document.createElement('canvas');
    sctx          = scratchCanvas.getContext('2d');

    day           = document.getElementById('day');
    night         = document.getElementById('night');

    rect          = null;

    setupMouse(canvas, drawClip, clickCompass, true);
    ctx.canvas.width  = getWidth();
    ctx.canvas.height = window.innerHeight;
    scratchCanvas.width = ctx.canvas.width;
    scratchCanvas.height = ctx.canvas.height;

    compass = new Image();
    compass.src = 'assets/img/glowingcompass.png';
    compassLocations = [
        {x: 0.14, y: 0.61},
        {x: 0.28, y: 0.86},
        {x: 0.58, y: 0.59},
        {x: 0.69, y: 0.82},
        {x: 0.83, y: 0.61}
    ];

    rand = Math.floor(Math.random()*5);
    posX = compassLocations[rand].x;
    posY = compassLocations[rand].y;

    compassX = 0;
    compassY = 0;
    compassW = 40;
    compassH = 46;

    clipRadius = 50;
    w = 0; h = 0;
    mouse = { x: -200, y: -200 };

    if (day.readyState === 4) {
        scaleImages();

        draw();
        $('.loader').addClass('done');
    } else {
        setTimeout(init, 100);
    }

    window.onresize = redraw;
}

var canvas,
    ctx,
    scratchCanvas,
    sctx,

    day,
    night,

    rect,

    compass,
    compassLocations,

    rand,
    posX, posY,
    compassX, compassY,
    compassW, compassH,

    clipRadius,
    w, h,
    mouse;
