var audio = document.getElementById('audio');
audio.onloadedmetadata = function(){
    var durAudio = document.getElementById('durAudio');
    durAudio.innerHTML = Math.floor(audio.duration);
        
};