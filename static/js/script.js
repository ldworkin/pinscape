$(document).ready(function() {

    $('.dropdown-toggle').dropdown();

    var user_input = $('#user');

    user_input.keypress(function(e) {
	if (e.keyCode == 13) {
	    $(this).trigger('blur');
	    e.preventDefault();
	    return false;
	}
    });

    user_input.blur(function() {
	user = $('#user').val();
	boards_url = 'user/boards/' + user
	_this = $(this)
	$.getJSON(boards_url, function(data) {
	    form_remainder = $('#form-remainder');
	    board_select = $('#board-select');
	    board_select.html(''); // clear board options from previous user
	    form_remainder.hide();
	    if (data['status'] == 'failure') {
		// no user found
		//$('#form-alert').show().attr('class', 'alert alert-error').find('span').html(data['message']);
		_this.parent().parent().addClass('error')
		_this.parent().find('p').html(data['message'])
	    }
	    else {
		//$('#form-alert').hide().find('span').html("");
		_this.parent().parent().removeClass('error')
		_this.parent().find('p').html('')
		var availableBoards = data['boards'];
		$("#board-select-option").tmpl(availableBoards).appendTo(board_select);
		form_remainder.show();
	    }
	});
    });

    $('#template-select').change(function() {
	if ($(this).val() == 'monitor') {
	    $('#resolution-div').show();
	}
	else {
	    $('#resolution-div').hide();
	}

    });

    $('#submit').click(function() {
	var user = $('#user').val();
	var board = $('#board-select').val();
	var template = $('#template-select').val();
	var resolution = $('#resolution-div')

	if (template == 'monitor') {
	    var width = $('#width').val();
	    var height = $('#height').val();
	    if (width == '' || height == '' || isNaN(width) || isNaN(height) || Number(height) == 0) {
		resolution.addClass('error')
		resolution.find('p').html('Please enter a valid height and width.')
		return false;
	    }
	    else if (Number(width) < 200) {
		resolution.addClass('error')
		resolution.find('p').html('That width is too small.')
		return false;
	    }
	    else {
		resolution.removeClass('error')
		resolution.find('p').html('')
	    }
	    template = template + '-' + width + 'x' + height
	}
	var seed = Math.floor(Math.random() * 101)
	var verify_url = 'collage/verify/' + user + '/' + board + '/' + seed + '/' + template;
	var show_url = 'collage/show/' + user + '/' + board + '/' + seed + '/'+ template;
	var download_url = 'collage/download/' + user + '/' + board + '/' + seed + '/'+ template;
	var collage = $('#collage');
	var loading = $(this).parent().find('#loading-message').html("Loading ...");
	$.getJSON(verify_url, function(data) {
	    collage.html("");
	    loading.html("");
	    if (data['status'] == "failure") {
		$('#form-alert').show().attr('class', 'alert alert-error').find('span').html(data['message']);
	    }
	    else {
		if (data['message'] != "") {
		    $('#form-alert').show().attr('class', 'alert').find('span').html(data['message']);
		}
		else {
		    $('#form-alert').hide().find('span').html("");
		}
		var image_div = $('<div>').attr({'id': 'image-result', 'class': 'well'}).appendTo(collage);
		var image_img = $('<img>').attr({'src': show_url}).appendTo(image_div);
		image_div.append('<hr>')
		var refresh_button = $('<button>').attr({'id': 'refresh', 'class': 'btn'}).html('Refresh').appendTo(image_div);
		var save_button = $('<button>').attr({'id': 'save', 'class': 'btn'}).html('Save').appendTo(image_div);
		refresh_button.click(function() {
		    $('#submit').trigger('click');
		});
		save_button.click(function() {
		    window.location = download_url
		});
  	    }
	});
	
	return false;
    });
});
