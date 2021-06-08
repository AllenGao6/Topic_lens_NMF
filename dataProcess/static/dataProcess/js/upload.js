$(document).ready(function() {

	is_file_upload = false;
    // The event listener for the file upload
    document.getElementById('txtFileUpload').addEventListener('change', upload, false);

    // Method that checks that the browser supports the HTML5 File API
    function browserSupportFileUpload() {
        var isCompatible = false;
        if (window.File && window.FileReader && window.FileList && window.Blob) {
        isCompatible = true;
        }
        return isCompatible;
    }

	function csvToArray(array) {

		title_list = []
		content_list = []
		for (var i = 1; i < array.length; i++) {

			var item = array[i];
			title_list.push(item[0]);
			content_list.push(item[1]);
		}
		// return the arrays
		return [title_list, content_list];
	}
		
	$('body').on("click", "#start", function () {
		if (!is_file_upload) {
			alert("Please Upload a Valid File");
		} else {
			$("#start").text('computing the range of optimal topic number... please wait');
			$("#start").addClass('disabled');
			$.ajax({
				url: 'upload/analyze/',
				type: 'POST',
				data: {
				},
				success: function (xhr) {
					$('.holder').hide()
					$('.analyze_holder').show()
				  	console.log("success222!");
				},
				error: function(xhr) {
				  if (xhr.status == 403) {
					Utils.notify('error', xhr.responseText);
				  }
				}
			  });
		}
	});
	
    // Method that reads and processes the selected file
    function upload(evt) {
    if (!browserSupportFileUpload()) {
        alert('The File APIs are not fully supported in this browser!');
        } else {
            var data2 = null;
            var file = evt.target.files[0];
            var reader = new FileReader();
            reader.readAsText(file);
            reader.onload = function(event) {
                var csvdata2 = event.target.result;
				data2 = $.csv.toArrays(csvdata2);
				//convert 2d array into 2 seperate array
				var data_list = csvToArray(data2);
				
				if (data2 && data2.length > 0) { // if data recieved successful by browser
					$('#start').addClass('disabled loading');
					$.ajax({
						url: 'upload/data_recieve/',
						type: 'POST',
						data: {
							'titles': data_list[0],
							'contents': data_list[1],
						},
						success: function(xhr) {
							is_file_upload = true;
							$('#start').removeClass('disabled loading');
							$("#start").text('Start Analyzing');
						  console.log("success!");
						},
						error: function(xhr) {
						  if (xhr.status == 403) {
							Utils.notify('error', xhr.responseText);
						  }
						}
					  });
                  //alert('Imported -' + data2.length + '- rows successfully!');
                } else { //not recieved or empty 
                    alert('No data2 to import!');
                }
            };
            reader.onerror = function() {
                alert('Unable to read ' + file.fileName);
            };
        }
    }
});