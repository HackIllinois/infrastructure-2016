'use strict';

function loadSounds(obj) {
    var len = obj.length, i;

    // iterate over sounds obj
    for (i in obj) {
        if (obj.hasOwnProperty(i)) {
        // load sound
        loadSoundObj(obj[i]);
        }
    }
}

function loadSoundObj(obj) {
    var request = new XMLHttpRequest();
    request.open('GET', obj.src + format, true);
    request.responseType = 'arraybuffer';

    request.onload = function() {
        audioCtx.decodeAudioData(request.response, function(buffer) {
            obj.buffer = buffer;
        }, function(err) {
            throw new Error(err);
        });
    };
}

function playSound(sound){
    var source = audioCtx.createBufferSource();
    source.buffer = sound;
    source.connect(audioCtx.destination);
    //source.start(0);
}

var audioFiles = {
  owl : {
  //  src : '../audio/horned-owl.mp3'
  },
};

// Create an audio context
window.AudioContext = window.AudioContext || window.webkitAudioContext;
var audioCtx = new AudioContext();

// load file
var request = new XMLHttpRequest();
request.open("GET", 'assets/audio/horned-owl.mp3', true);
request.responseType = 'arraybuffer';

request.onload = function() {
    // request.response is encoded... so decode it now
    audioCtx.decodeAudioData(request.response, function(buffer) {
        var sound = buffer;
        playSound(sound);
    }, function(err) {
        throw new Error(err);
    });
};
request.send();
