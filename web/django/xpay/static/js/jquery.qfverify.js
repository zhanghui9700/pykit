function verify_mobile(obj) {
	if (obj.val().match(/^0{0,1}(13[0-9]|14[0-9]|15[0-9]|18[0-9])[0-9]{8}$/)) {
		return true;
    } 
	else {
        return false;
    }
}

