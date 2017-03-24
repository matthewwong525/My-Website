// Initialize Firebase
var config = {
    apiKey: "AIzaSyDi1uj0-1YBfxpNF6L-NFOaFyfzEQo323w",
    authDomain: "mywebapp-123.firebaseapp.com",
    databaseURL: "https://mywebapp-123.firebaseio.com",
    storageBucket: "mywebapp-123.appspot.com",
    messagingSenderId: "808569769768"
};
firebase.initializeApp(config);

(function(){

    var app = angular.module("authentication-service",["firebase"]);

    app.service("AuthService",["$firebaseAuth","$http","$window", function($firebaseAuth,$http,$window){
        var Auth = $firebaseAuth();

        //TODO: FRONT END VALIDATION!!!!
        this.createUser = function(theScope,email,password){
            parameters = JSON.stringify({ email: email, password: password, verify: verify });
            $http.post("/signup/",parameters)
                .then(function(response){
                    if(response.data.success){
                        //REDIRECT TO MAIN PAGE AND LOGIN USING FIREBASE AUTH
                        Auth.$createUserWithEmailAndPassword(response.data.email,response.data.password)
                            .then(function(firebaseUser){
                                //Update display name as well
                                firebaseUser.updateProfile({
                                    displayName : response.data.username
                                });
                                console.log("User created with uid: " +firebaseUser.uid);
                                $window.location.href="/";
                            })
                            .catch(function(error){
                                //TODO: delete user from database on server
                                console.log(error);
                            });
                        
                    }else{
                        theScope.err_email = response.data.err_email;
                        theScope.err_pass = response.data.err_pass;
                        theScope.err_verify = response.data.err_verify;
                    }
                })
                .catch(function(response){
                    console.log(response);
                    //TODO: ERROR MESSAGES
                });

        };

        this.signInUser = function(theScope,email,password){
            parameters = JSON.stringify({ email: email, password: password});
            console.log(parameters)
            //REDIRECT TO MAIN PAGE AND LOGIN USING FIREBASE AUTH
            Auth.$signInWithEmailAndPassword(email,password)
                .then(function(firebaseUser){
                    console.log("User logged in with uid: " +firebaseUser.uid);
                })
                .catch(function(error){
                    console.log(error);
                    theScope.invalidCred = "Invalid Email or Pass"
                });
            //$window.location.href="/";
        };
        

    }]);

})();