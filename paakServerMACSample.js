var MongoClient = require('mongodb').MongoClient;
var express = require('express');
var url = "mongodb://localhost:27017/";
var app = express();
var router = express.Router();
var bodyParser = require('body-parser')
var serverDb, dbHandle, collectionNameGlobal;
const util = require('util');

MongoClient.connect(url, function(err, database) {
    if (err) throw err;
    serverDb = database.db("appiumDatabaseServerMAC");
    dbHandle = database
    var todayDate = new Date()
    todayDate = "-"+todayDate.getFullYear()+"-"+(todayDate.getMonth()+1)+"-"+todayDate.getDate()
    collectionName = "testAppiumServerMACDatabase"+todayDate;
    console.log("Today Date Format "+todayDate)
    collectionNameGlobal = collectionName
    //check if database exists
    serverDb.createCollection(collectionNameGlobal, function(err, res) {
        if (err) throw err;
        console.log("Collection created!"+collectionNameGlobal);
        });
    });


router.use(bodyParser.json())

router.use("/appiumRequest", function (req, res, next){
	var timeNow = new Date()
	console.log("Handling Appium Request "+timeNow);
	next()
});

router.get("/", function (req, res, next){
	console.log("Get Request Handled")
	res.send("Get Received")
})

router.get("/appiumRequest", function (req, res, next){
	console.log("Handling GET Request")
	var reqObjectGet = util.inspect(req.body, false, null)
	var imagePath
	query = {'_id' : req.query._id}
	console.log("_id : "+req.query._id)
	serverDb.collection(collectionNameGlobal).findOne(query, function(err, docResult){
		if (err){
			console.log("Error Error")
			res.send("Error Error");
		}
		else{
			if(docResult) {
				var options = { dotfiles: 'deny'}
				if (docResult.screenShot) {
					console.log('Sending Picture')
					res.sendFile(docResult.screenShot, options, function(sendErr){
						if (sendErr) {
							next()
						}
					})
					console.log("Picture Sent ")
				}
				else{
					console.log('docResult.screenShot empty')
					var options = {
						root : __dirname,
						dotfiles: 'deny'
					}
					res.sendFile('errorImage.png', options, function (imageError){
						if (imageError) {
							console.log("Error Sending ErrorImage ")
							next()
						}
						else console.log("Error Image Sent")
					})
				}
			}
			else{
				res.send("No Doc Found "+req.query._id)
			}
		}
	})
},	function (req, res, next){
		console.log("Screenshot Path Not Specified ")
		var options = { 
			root : __dirname, 
			dotfiles: 'deny'
		}
		res.sendFile('errorImage.png', options, function (imageError){
			if (imageError) next()
			else console.log("Error Image Sent")
		})
	},
	function (req, res, next){
		res.send("Issue With Sending File")
	}
);

router.post('/appiumRequest', function (req, res, next) {
	console.log("Handling POST Request")
	//Need tyepe INT to search for string
	var testCaseNumJS = parseInt(req.body.testCaseNumber)
	var testCaseAction = req.body.actionStatus
	var testCaseActiveReq = req.body.activeRequest
	objectID = 'ObjectId("e0c1f4kjhhkjh;k642582e")'
	var query = {'testCaseNumber': testCaseNumJS}
	var handledQuery = {"testCaseNumber": testCaseNumJS, "activeRequest" :  "Active"}
	var docId = req.body._id
	console.log("_id " + objectID)
	console.log("testCaseActiveReq "+req.body.activeRequest)

	if (testCaseActiveReq == "Active"){
		serverDb.collection(collectionNameGlobal).findOne(query, function(error, docResult){
			try {
				if(error) {
					console.log("Error Searching For Document")
					console.log("Search Criteria: _id "+req.body._id)
					throw error
				}
				else{
					if (docResult){
						console.log("Search Result "+docResult)
						res.json({"_id" : docResult._id, "ErrorLocation" : docResult.ErrorLocation, "connectCommand" : docResult.connectCommand, "vin" : docResult.vin,
									"actionResult" : docResult.actionResult, "phone" : docResult.phone, "Error" : docResult.Error, "activeRequest" : docResult.activeRequest,
									"ErrorDescription" : docResult.ErrorDescription, "timeStamp" : docResult.timeStamp, "testCaseNumber" : docResult.testCaseNumber,
									"actionStatus" : docResult.actionStatus, "currentCommand" : docResult.currentCommand, "action" : docResult.action})
					}
					else {
						console.log("No Matching Document Found, No Error")
						var errorObject = ({'actionRequest':'dbActionSearchEmpty', 'actionStatus' : 'noMatchingDocError', 'testCaseNumber' : '0'})
						console.log("Search Result "+docResult)
						//What do if no result match is found
						res.json(errorObject)
					}
				}
			}
			catch(error){
				console.log("Error Searching For Document")
				var errorObject = ({'actionRequest':'dbActionSearchError', 'actionStatus' : 'docNotFoundError', 'testCaseNumber' : '0'})
				res.json(errorObject)
			}
		})
	}
	else if (testCaseActiveReq == "Not Active"){
		try {
			serverDb.collection(collectionNameGlobal).findOneAndUpdate(query,{$set: {"activeRequest" :  "Not Active"}}, {returnNewDocument : true})
		}
		catch (error)
		{
			console.log("Error Updating activeRequest Status for "+req.body._id)
		}
		res.json(req.body)
	}
	/*if (testCaseAction == 'Handled' && testCaseActiveReq == 'Active'){
		serverDb.collection(collectionNameGlobal).findOneAndUpdate(handledQuery,{$set: {"activeRequest" :  "NotActive"}}, {new:true}).then(function(docHandle){
			try {
				if(!docHandle) throw new Error("No Record Found")
				console.log("Search Result"+docHandle)
				res.json(docHandle)
			}
			catch(Error)
			{
				console.log("Error Searching For Document")
				var errorObject = ({'actionRequest':'dbActionSearchFalse'})
				res.json(errorObject)
			}
		})
	}
	else{
		serverDb.collection(collectionNameGlobal).findOne(query).then(function(doc){
			try {
				if(!doc) throw new Error("No Record Found")
				console.log("Search Result"+doc)
				res.json(doc)
			}
			catch(Error)
			{
				console.log("Error Searching For Document")
				var errorObject = ({'actionStatus':'dbSearchFalse'})
				res.json(errorObject)
			}
		})
	}*/
    console.log("POST Request Handled")
})

router.put('/appiumRequest', function (req, res, next) {
	console.log("Handling PUT request")
	//Store testCaseNumber as an Int and not String
	var testCaseNumJS = parseInt(req.body.testCaseNumber)
	req.body.testCaseNumber = testCaseNumJS
	
	//Change actionStatus to "Received" from "Sent"
	req.body.actionStatus = "Received"
	var appiumAction = req.body.action
	var reqObject = util.inspect(req.body, false, null)
	console.log("Handling Action: "+appiumAction)
           
    //Store in database
    serverDb.collection(collectionNameGlobal).insertOne(req.body)
           
    //if (req.body.action == "KILL-SERVER"){
        
		//console.log("Closing DBConnection")
		//dbHandle.close();
	//}
	res.json(req.body)
	console.log("PUT Request Handled")
})

app.use("/", router);
app.use("*",function(req,res){
	res.status(404).send('404');
});

app.listen(8000, function () {
  console.log('Example app listening on port 8000!')
});
