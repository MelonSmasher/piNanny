let createError = require('http-errors');
const express = require('express');
const auth = require('basic-auth');
let path = require('path');
let cookieParser = require('cookie-parser');
let logger = require('morgan');
let indexRouter = require('./routes/index');

const app = express();

// If we have a username and password from env vars
if (process.env.HTTP_AUTH_USERNAME && process.env.HTTP_AUTH_PASSWORD) {
// Ensure this is before any other middleware or routes
    app.use((req, res, next) => {
        let user = auth(req);
        if (user === undefined || user['name'] !== process.env.HTTP_AUTH_USERNAME || user['pass'] !== process.env.HTTP_AUTH_PASSWORD) {
            res.statusCode = 401;
            res.setHeader('WWW-Authenticate', 'Basic realm="Node"');
            res.end('Unauthorized');
        } else {
            next();
        }
    });
}

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'hbs');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({extended: false}));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use(function (req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    next();
});

app.use('/', indexRouter);

// catch 404 and forward to error handler
app.use(function (req, res, next) {
    next(createError(404));
});

// error handler
app.use(function (err, req, res, next) {
    // set locals, only providing error in development
    res.locals.message = err.message;
    res.locals.error = req.app.get('env') === 'development' ? err : {};

    // render the error page
    res.status(err.status || 500);
    res.render('error');
});

module.exports = app;
