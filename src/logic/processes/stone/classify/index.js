var express = require('express');
var router = express.Router();
var path = require('path');

const child_process = require('child_process');

router.route('/stone/classify').post(
    function(req, res) {
        child_process.exec('python3 ' + path.join(__dirname, '../../../../script/image-validation.py') + ' ' + req.files.document.path + ' ' + req.files.document.path + '.out.jpg', { timeout : 60000 }, (err, stdout, stderr) => {  
            if (err) {  
                res.send(err);  
                return;  
            }  

            res.sendFile(req.files.document.path + '.out.jpg');
        });                          
    }
);

module.exports = (app) => router; 