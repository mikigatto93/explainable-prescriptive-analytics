window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        slider_value_display_csc_percent: function(value) {
            let perc = Math.floor(value * 100);
            return perc.toString() + " %";
        },

        slider_value_display_csc: function(value) {
        	return value;
        },


//        set_client_id: function(value) {
//        	//return 'assfnargavn4lasnoew';
//        	console.log("Set client id: " + CLIENT_ID);
//        	return CLIENT_ID;
//        },
    }
});