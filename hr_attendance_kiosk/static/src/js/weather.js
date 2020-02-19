odoo.define('hr_attendance_kiosk.weather', function(require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var Session = require('web.session');

var QWeb = core.qweb;

var WeatherKioskMode = require('hr_attendance.kiosk_mode');

WeatherKioskMode.include({

	// Starting the function the same time as the clock
    start_clock: function() {
        this._super();
        this.weather();
    },
	weather: function() {
		// Forecast API info
		var self = this;
		var apiKey = "";
		var url = "https://api.darksky.net/forecast/";
		var latitude = '58.41086';
		var longitude = '15.62157';
		
		
		// Retrieves information from the requested API url, extracts the information wanted and outputs it on the webpage
		function update_weather(jsonRequest){
			$.getJSON(
				jsonRequest,
				function(data) {
					// Array with days and months to be used in the render
					var today = new Date(),
						dd = today.getDate(),
						mm = ['Januari', "Februari", "Mars", "April", "Maj", "Juni", "Juli", "Augusti", "September", "Oktober", "November", "December"],
						weekday = ['Söndag', 'Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lördag'],
						dayOfWeek = weekday[today.getDay()],
						month = mm[today.getMonth()];
					
					// Render day of week & current date.
					self.$("#date").html(dayOfWeek + ' ' + dd + ' ' + month);
					
					var temperature = Math.floor(data.currently.temperature);
					self.$("#temp").html(temperature + "° C");
					var icon = data.currently.icon;
					self.$("#daily").html(data.daily.summary);
					var src = self.$("#icon");

					// Different cases depending on the weather, each weather has its own icon and outputs that icon as an img tag 
					switch (icon) {
						case "clear-day":
							var image = $('<img/>');
							image.attr('src', '/hr_attendance_kiosk/static/src/img/sunny.svg');
							image.addClass('weather-icon');
							src.html(image);
							break;
						case "clear-night":
							var image = $('<img/>');
							image.attr('src', '/hr_attendance_kiosk/static/src/img/moon.svg');
							image.addClass('weather-icon');
							src.html(image);
							break;
						case "partly-cloudy-day":
							var image = $('<img/>');
							image.attr('src', '/hr_attendance_kiosk/static/src/img/icon.svg');
							image.addClass('weather-icon');
							src.html(image);
							break;
						case "partly-cloudy-night":
							var image = $('<img/>');
							image.attr('src', '/hr_attendance_kiosk/static/src/img/night.svg');
							image.addClass('weather-icon');
							src.html(image);
							break;
						case "cloudy":
							var image = $('<img/>');
							image.attr('src', '/hr_attendance_kiosk/static/src/img/cloud.svg');
							image.addClass('weather-icon');
							src.html(image);
							break;
						case "rain":
							var image = $('<img/>');
							image.attr('src', '/hr_attendance_kiosk/static/src/img/drop.svg');
							image.addClass('weather-icon');
							src.html(image);
							break;
						case "sleet":
							var image = $('<img/>');
							image.attr('src', '/hr_attendance_kiosk/static/src/img/sleet.svg');
							image.addClass('weather-icon');
							src.html(image);
							break;
						case "snow":
							var image = $('<img/>');
							image.attr('src', '/hr_attendance_kiosk/static/src/img/snowflake.svg');
							image.addClass('weather-icon');
							src.html(image);
							break;
						case "wind":
							var image = $('<img/>');
							image.attr('src', '/hr_attendance_kiosk/static/src/img/wind.svg');
							image.addClass('weather-icon');
							src.html(image);
							break;
						default:
							var image = $('<img/>');
							image.attr('src', '/hr_attendance_kiosk/static/src/img/fog.svg');
							image.addClass('weather-icon');
							src.html(image);
					}
				}
			)
		}
		// Get the api key from system parameter in odoo
		this._rpc({
			model: 'ir.config_parameter',
			method: 'get_param',
			args: ['hr_attendance_kiosk.apiKey'],
		})
		.then(function (result) {
			apiKey = result;
			
			// The information needed for the function below
			var jsonRequest = url + apiKey + "/" + latitude + "," + longitude + "?callback=?&" + "units=si&" + "lang=sv";
			
			// Runs the update_weather function every 30 minutes, 1.8 million milliseconds = 30 minutes
			setInterval(update_weather, 1800000, jsonRequest);
			update_weather(jsonRequest);
		},
		function(){
			console.log("test");
			});
	}
});

return WeatherKioskMode;

});
