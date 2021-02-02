URL = window.URL || window.webkitURL;

var gumStream;
var rec;
var input;

var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var pauseButton = document.getElementById("pauseButton");
var nameInput = document.getElementById("name");  //This is to take name from the formfield.
//("name") is from forms.py


recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
pauseButton.addEventListener("click", pauseRecording);

// 4 important funtions

// Record Button
function startRecording(){
  console.log("recordButton clicked");


var constraints = {
  audio: true,
  video: false
}

  recordButton.disabled = true;
  stopButton.disabled = false;
  pauseButton.disabled = false;

// Using the standard promise based getUserMedia()
  navigator.mediaDevices.getUserMedia(constraints).then(function(stream){
    console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

    audioContext = new AudioContext();

    gumStream = stream;
    input = audioContext.createMediaStreamSource(stream);
    rec = new Recorder(input,{numChannels: 1})

    //start the recording process
    rec.record()
    console.log("Recording Started");
  }).catch(function(err){
  //enable the record button if getUserMedia() fails
  recordButton.disabled = false;
  stopButton.disabled = true;
  pauseButton.disabled = true;
  });
}

//Pause button
function pauseRecording(){
  console.log("pauseButton clicked rec.recording=", rec.recording);
  if(rec.recording){
    rec.stop();
    pauseButton.innerHTML = "Resume";
  }else{
    rec.record();
    pauseButton.innerHTML = "Pause";
  }
}

//Stop button
function stopRecording(){
  console.log("stopButton clicked");

  recordButton.disabled = false;
  stopButton.disabled = true;
  pauseButton.disabled = true;

  pauseButton.innerHTML = "Pause";

  //tell the recorder to stop Recording
  rec.stop(); //stop mic access
  gumStream.getAudioTracks()[0].stop();

  //create the wav blob and pass it on to createDownloadLink
  rec.exportWAV(createDownloadLink);
}


//Download link
function createDownloadLink(blob) {

	var url = URL.createObjectURL(blob);
	var au = document.createElement('audio');
	var li = document.createElement('li');
	var link = document.createElement('BUTTON');

	//name of .wav file to use during upload and download (without extendion)
	var filename = new Date().toISOString();

	//add controls to the <audio> element
	au.controls = true;
	au.src = url;

	//save to disk link
  link.setAttribute("class", "btn btn-success");
  link.setAttribute("id", "save-btn");
	link.href = url;
	link.download = filename+".wav"; //download forces the browser to donwload the file using the  filename
	link.innerHTML = "Save to disk";

	//add the new audio element to li
	li.appendChild(au);

	//add the filename to the li
	// li.appendChild(document.createTextNode(filename+".wav "))

	//add the save to disk link to li
	// li.appendChild(link);

	//upload link
	var upload = document.createElement("BUTTON");
  var image = document.createElement("img");
  image.src = "static/upload.png"
  image.setAttribute("id", "upload-img")
	upload.href="#";
  upload.setAttribute("class", " upload-btn btn btn-warning");
  upload.setAttribute("id", "upload-btn-id")
  upload.appendChild(image);
	// upload.innerHTML = "Upload";
	upload.addEventListener("click", function(event){
		  var xhr=new XMLHttpRequest();

		  xhr.onload=function(e) {
		      if(this.readyState === 4) {
		          console.log("Server returned: ",e.target.responseText, e.target.responseText.status);
              // var obj = JSON.parse(e.target.responseText)
              // console.log(obj)
              if(e.target.responseText == "ok"){
                console.log("redirect")

                window.location.href = "https://ai-bonenkai.geekdev.tokyo/list";
              }

		      }
		  };
		  var fd=new FormData();
      console.log("nameInput:",nameInput.value);  //to see in the console if this working
      fd.append("recorder_name", nameInput.value); //to rename from input on form field
		  fd.append("audio_data",blob, filename);
		  xhr.open("POST",'/upload',true);
		  xhr.send(fd);
	})
	li.appendChild(document.createTextNode (" ")) //add a space in between
	li.appendChild(upload) //add the upload link to li

	//add the li element to the ol
	recordingsList.appendChild(li);
}
