import Hls from "hls.js";
import io from 'socket.io-client';

var temp = new RadialGauge({
    renderTo: 'temp',
    width: 250,
    height: 250,
    units: "°F",
    minValue: 0,
    maxValue: 120,
    majorTicks: [
        "0",
        "20",
        "40",
        "60",
        "80",
        "100",
        "120"
    ],
    minorTicks: 5,
    exactTicks: true,
    strokeTicks: true,
    highlights: [
        {
            "from": 0,
            "to": 55,
            "color": "rgba(0, 153, 255, .75)"
        },
        {
            "from": 55,
            "to": 85,
            "color": "rgba(102, 204, 102, .75)"
        },
        {
            "from": 85,
            "to": 120,
            "color": "rgba(255, 51, 51, .75)"
        }
    ],
    borderShadowWidth: 0,
    borders: false,
    needleType: "arrow",
    needleWidth: 2,
    needleCircleSize: 7,
    needleCircleOuter: true,
    needleCircleInner: false,
    animationDuration: 1500,
    animationRule: "linear"
}).draw();

var pressure = new RadialGauge({
    renderTo: 'pressure',
    width: 250,
    height: 250,
    units: "hpa/mbar",
    minValue: 960,
    maxValue: 1070,
    highlights: [
        {
            "from": 960,
            "to": 990,
            "color": "rgba(188, 189, 189, .75)"
        },
        {
            "from": 990,
            "to": 1040,
            "color": "rgba(163, 198, 214, .75)"
        },
        {
            "from": 1040,
            "to": 1070,
            "color": "rgba(137, 207, 240, .75)"
        },
    ],
    majorTicks: [
        "960",
        "970",
        "980",
        "990",
        "1000",
        "1010",
        "1020",
        "1030",
        "1040",
        "1050",
        "1060",
        "1070"
    ],
    minorTicks: 5,
    exactTicks: true,
    strokeTicks: true,
    borderShadowWidth: 0,
    borders: false,
    needleType: "arrow",
    needleWidth: 2,
    needleCircleSize: 7,
    needleCircleOuter: true,
    needleCircleInner: false,
    animationDuration: 1500,
    animationRule: "linear"
}).draw();

var iaq = new RadialGauge({
    renderTo: 'iaq',
    width: 250,
    height: 250,
    units: "iaq index",
    minValue: 0,
    maxValue: 500,
    highlights: [
        {
            "from": 0,
            "to": 50,
            "color": "rgba(102, 204, 102, .75)"
        },
        {
            "from": 51,
            "to": 100,
            "color": "rgba(255, 255, 102, .75)"
        },
        {
            "from": 100,
            "to": 150,
            "color": "rgba(255, 153, 51, .75)"
        },
        {
            "from": 150,
            "to": 200,
            "color": "rgba(255, 51, 51, .75)"
        },
        {
            "from": 200,
            "to": 300,
            "color": "rgba(153, 102, 255, .75)"
        },
        {
            "from": 300,
            "to": 500,
            "color": "rgba(153, 0, 51, .75)"
        }
    ],
    majorTicks: [
        "0",
        "50",
        "100",
        "150",
        "200",
        "300",
        "500"
    ],
    minorTicks: 10,
    exactTicks: true,
    strokeTicks: true,
    borderShadowWidth: 0,
    borders: false,
    needleType: "arrow",
    needleWidth: 2,
    needleCircleSize: 7,
    needleCircleOuter: true,
    needleCircleInner: false,
    animationDuration: 1500,
    animationRule: "linear"
}).draw();

var humidity = new RadialGauge({
    renderTo: 'humidity',
    width: 250,
    height: 250,
    units: "%RH",
    minValue: 0,
    maxValue: 100,
    majorTicks: [
        "0",
        "10",
        "20",
        "30",
        "40",
        "50",
        "60",
        "70",
        "80",
        "90",
        "100"
    ],
    minorTicks: 5,
    exactTicks: true,
    strokeTicks: true,
    highlights: [
        {
            "from": 0,
            "to": 35,
            "color": "rgba(255, 153, 51, .75)"
        },
        {
            "from": 35,
            "to": 65,
            "color": "rgba(102, 204, 102, .75)"
        },
        {
            "from": 65,
            "to": 100,
            "color": "rgba(0, 153, 255, .75)"
        }
    ],
    borderShadowWidth: 0,
    borders: false,
    needleType: "arrow",
    needleWidth: 2,
    needleCircleSize: 7,
    needleCircleOuter: true,
    needleCircleInner: false,
    animationDuration: 1500,
    animationRule: "linear"
}).draw();

if (Hls.isSupported()) {
    let video = document.getElementById('stream');
    let hls = new Hls();
    hls.loadSource('/images/stream/live.m3u8');
    hls.attachMedia(video);
    hls.on(Hls.Events.MANIFEST_PARSED, function () {
        video.play();
    });
} else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = '/images/stream/live.m3u8';
    video.addEventListener('canplay', function () {
        video.play();
    });
}

let socket = io();
socket.on('SensorData', function (data) {
    temp.update({value: data.temperature_f});
    pressure.update({value: data.pressure});
    iaq.update({value: data.iaq});
    humidity.update({value: data.humidity});
    console.log(data);
});