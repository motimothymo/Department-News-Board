import json

from nameko.rpc import RpcProxy
from nameko.web.handlers import http

from dependencies.session import SessionProvider, session_start


class GatewayService:
    name = "gateway_service"
    session_provider = SessionProvider()
    user_rpc = RpcProxy("user_service")
    news_rpc = RpcProxy("news_service")
    files_rpc = RpcProxy("files_service")

#==================================USER========================================

    @http("POST", "/signup")
    @session_start
    def signup(self, request, session, response):
        request_body = [
            ("username", str),
            ("password", str)
        ]

        response.mimetype = "application/json"
        response.status_code = 400

        try:
            data = json.loads(request.get_data().decode("utf-8"))

        except Exception as e:
            response.set_data(json.dumps(
                {
                    "action": "signup",
                    "action_status": "error",
                    "message": "Bad request: invalid data"
                }
            ))
            return response

        for key in request_body:
            if key[0] not in data:
                response.set_data(json.dumps(
                    {
                        "action": "signup",
                        "action_status": "error",
                        "message": f"Bad request: missing '{key}' parameter"
                    }
                ))
                return response
            else:
                if not isinstance(data[key[0]], key[1]):
                    response.set_data(json.dumps(
                        {
                            "action": "signup",
                            "action_status": "error",
                            "message": f"Bad request: '{key[0]}' parameter is not of type '{key[1]}'"
                        }
                    ))
                    return response

        if data["username"] == None or data["username"] == "" or data["password"] == None or data["password"] == "":
            response.set_data(json.dumps(
                {
                    "action": "signup",
                    "action_status": "error",
                    "message": "Bad request: username or password is empty"
                }
            ))
            return response

        response.status_code = 200

        if len(data["username"]) > 50 or len(data["username"]) > 50:
            response.set_data(json.dumps(
                {
                    "action": "signup",
                    "action_status": "success",
                    "signup_status": "too_long",
                    "message": "Username or password is too long"
                }
            ))
            return response

        if session["username"]:
            response.set_data(json.dumps(
                {
                    "action": "signup",
                    "action_status": "success",
                    "signup_status": "already_logged_in",
                    "message": "Already logged in, please logout first before signup"
                }
            ))
            return response

        if self.user_rpc.check_username_exist(data["username"]):
            response.set_data(json.dumps(
                {
                    "action": "signup",
                    "action_status": "success",
                    "signup_status": "username_signed_up",
                    "message": "Username already signed up"
                }
            ))
            return response

        if not self.user_rpc.create_user(data["username"], data["password"]):
            response.status_code = 500
            response.set_data(json.dumps(
                {
                    "action": "signup",
                    "action_status": "error",
                    "message": "Failed to create user"
                }
            ))
            return response

        response.status_code = 201
        response.set_data(json.dumps(
            {
                "action": "signup",
                "action_status": "success",
                "signup_status": "success",
                "username": data["username"],
                "message": "Successfully signed up"
            }
        ))
        return response

    @http("POST", "/login")
    @session_start
    def login(self, request, session, response):
        request_body = [
            ("username", str),
            ("password", str)
        ]

        response.mimetype = "application/json"
        response.status_code = 400

        try:
            data = json.loads(request.get_data().decode("utf-8"))

        except Exception as e:
            response.set_data(json.dumps(
                {
                    "action": "login",
                    "action_status": "error",
                    "message": "Bad request: invalid data"
                }
            ))
            return response

        for key in request_body:
            if key[0] not in data:
                response.set_data(json.dumps(
                    {
                        "action": "login",
                        "action_status": "error",
                        "message": f"Bad request: missing '{key}' parameter"
                    }
                ))
                return response
            else:
                if not isinstance(data[key[0]], key[1]):
                    response.set_data(json.dumps(
                        {
                            "action": "login",
                            "action_status": "error",
                            "message": f"Bad request: '{key[0]}' parameter is not of type '{key[1]}'"
                        }
                    ))
                    return response

        if data["username"] == None or data["username"] == "" or data["password"] == None or data["password"] == "":
            response.set_data(json.dumps(
                {
                    "action": "login",
                    "action_status": "error",
                    "message": "Bad request: username or password is empty"
                }
            ))
            return response

        response.status_code = 200

        if session["username"]:
            response.set_data(json.dumps(
                {
                    "action": "login",
                    "action_status": "success",
                    "login_status": "already_logged_in",
                    "message": "Already logged in, please logout first before logging back in"
                }
            ))
            return response

        if not self.user_rpc.check_username_exist(data["username"]):
            response.set_data(json.dumps(
                {
                    "action": "login",
                    "action_status": "success",
                    "login_status": "username_not_exist",
                    "message": "Username does not exist"
                }
            ))
            return response

        if not self.user_rpc.check_password_match(data["username"], data["password"]):
            response.set_data(json.dumps(
                {
                    "action": "login",
                    "action_status": "success",
                    "login_status": "password_not_match",
                    "message": "Password does not match"
                }
            ))
            return response

        session["username"] = data["username"]
        response.set_data(json.dumps(
            {
                "action": "login",
                "action_status": "success",
                "login_status": "success",
                "username": data["username"],
                "message": "Login successful"
            }
        ))
        return response

    @http("GET", "/logout")
    @session_start
    def logout(self, request, session, response):
        session.destroy()
        response.mimetype = "application/json"
        response.status_code = 200
        response.set_data(json.dumps(
            {
                "action": "logout",
                "action_status": "success",
                "message": "Logged out successfully"
            }
        ))
        return response    
    
#=================================NEWS=====================================
    
    @http("GET", "/get_all_news")
    def get_all_news(self, request, response):
        response.mimetype = "application/json"
        
        result = self.news_rpc.get_all_news()
        
        if result is None:
            response.status_code = 404
            response.set_data(json.dumps(
                {
                    "action": "get_all_news",
                    "action_status": "error",
                    "message": "Error: no news found"
                }
            ))
        else:
            response.status_code = 200
            response.set_data(json.dumps(
                {
                    "action": "get_all_news",
                    "action_status": "success",
                    "message": "News retrieved successfully",
                    "result": list(result)
                }
            ))
            
        return response
    
    @http("GET", "/get_news/<int:news_id>")
    def get_news_by_id(self, request, response, news_id):
        response.mimetype = "application/json"
        
        response.status_code = 400
        if news_id is None:
            response.set_data(json.dumps(
                {
                    "action": "get_news_by_id",
                    "action_status": "error",
                    "message": "Bad request: news_id is empty"
                }
            ))
            return response

        response.status_code = 404
        if not self.news_rpc.check_news_id_exist(news_id):
            response.set_data(json.dumps(
                {
                    "action": "get_news_by_id",
                    "action_status": "error",
                    "message": "News with given id does not exist"
                }
            ))
            return response
        
        
        response.status_code = 200
        response.set_data(json.dumps(
            {
                "action": "get_news_by_id",
                "action_status": "success",
                "message": "News retrieved successfully",
                "result": self.news_rpc.get_news_by_id(news_id)
            }
        ))
        
        return response
    
    @http("POST", "/add_news")
    @session_start
    def add_news(self, session, request, response):
        request_body = [
            ("title", str),
            ("content", str),
            ("date", str),
            ("author", str)
        ]
        
        request_body_files = [
            ("file_name", str),
            ("base64_data", str)
        ]
        
        response.mimetype = "application/json"
        
        if not session["username"]:
            response.status_code = 401
            response.set_data(json.dumps(
                {
                    "action": "add_news",
                    "action_status": "error",
                    "message": "Unauthorized: please login first"
                }
            ))
            return response
        
        response.status_code = 400
        try:
            data = json.loads(request.get_data().decode("utf-8"))
        except Exception as e:
            response.set_data(json.dumps(
                {
                    "action": "add_news",
                    "action_status": "error",
                    "message": "Bad request: invalid data"
                }
            ))
            return response
        
        for key in request_body:
            if key[0] not in data:
                response.set_data(json.dumps(
                    {
                        "action": "add_news",
                        "action_status": "error",
                        "message": f"Bad request: missing '{key}' parameter"
                    }
                ))
                return response
            else:
                if not isinstance(data[key[0]], key[1]):
                    response.set_data(json.dumps(
                        {
                            "action": "add_news",
                            "action_status": "error",
                            "message": f"Bad request: '{key[0]}' parameter is not of type '{key[1]}'"
                        }
                    ))
                    return response

        for index, file_body in enumerate(data["files"]):
            for key in request_body_files:
                if key[0] not in file_body:
                    response.set_data(json.dumps(
                        {
                            "action": "post_new_news",
                            "action_status": "error",
                            "message": f"Bad request: missing '{key}' parameter at file index {index}"
                        }
                    ))
                    return response
                else:
                    if not isinstance(file_body[key[0]], key[1]):
                        response.set_data(json.dumps(
                            {
                                "action": "post_new_news",
                                "action_status": "error",
                                "message": f"Bad request: '{key[0]}' parameter is not of type '{key[1]}' at file index {index}"
                            }
                        ))
                        return response
                
        new_id = self.news_rpc.add_news(data["title"], data["content"], data["date"], session["username"])
        
        self.files_rpc.post_file(new_id, data["base64_data"])
        
        response.status_code = 201
        response.set_data(json.dumps(
            {
                "action": "add_news",
                "action_status": "success",
                "message": f"News added successfully, Your new news id is: {str(new_id)}"
            }
        ))
        
        return response
    
    @http ("PUT", "/edit_news/<int:news_id>")
    @session_start
    def update_news(self, session, request, response, news_id):
        request_body = [
            ("title", str),
            ("content", str),
            ("date", str),
            ("files", list)
        ]
        
        request_body_dict = {
            "title": str,
            "content": str,
            "datetime": str,
            "files": list
        }

        request_body_set = set([x[0] for x in request_body])

        request_body_files = [
            ("file_name", str),
            ("base64_data", str)
        ]

        request_body_files_set = set([x[0] for x in request_body_files])
        
        response.mimetype = "application/json"
        
        if not session["username"]:
            response.status_code = 401
            response.set_data(json.dumps(
                {
                    "action": "update_news",
                    "action_status": "error",
                    "message": "Unauthorized: please login first"
                }
            ))
            return response
        
        response.status_code = 400
        try:
            data = json.loads(request.get_data().decode("utf-8"))
        except Exception as e:
            response.set_data(json.dumps(
                {
                    "action": "update_news",
                    "action_status": "error",
                    "message": "Bad request: invalid data"
                }
            ))
            return response
        
        unknown_keys = set(data.keys()) - request_body_set
        if len(unknown_keys) > 0:
            response.set_data(json.dumps(
                {
                    "action": "edit_news",
                    "action_status": "error",
                    "message": f"Bad request: unknown parameters: {', '.join(list(unknown_keys))}"
                }
            ))
            return response

        for key in data.keys():
            if not isinstance(data[key], request_body_dict[key]):
                response.set_data(json.dumps(
                    {
                        "action": "edit_news",
                        "action_status": "error",
                        "message": f"Bad request: '{key}' parameter is not of type '{request_body_dict[key]}'"
                    }
                ))
                return response

            if data[key] == "" or data[key] == None:
                response.set_data(json.dumps(
                    {
                        "action": "edit_news",
                        "action_status": "error",
                        "message": f"Bad request: '{key}' parameter cannot be empty'"
                    }
                ))
                return response

        if "files" in data.keys():
            for index, file_body in enumerate(data["files"]):
                unknown_keys_files = set(file_body.keys()) - request_body_files_set
                if len(unknown_keys_files) > 0:
                    response.set_data(json.dumps(
                        {
                            "action": "edit_news",
                            "action_status": "error",
                            "message": f"Bad request: unknown parameters: {', '.join(list(unknown_keys_files))} at file index {index}"
                        }
                    ))

                    return response

                for key in request_body_files:
                    if key[0] not in file_body:
                        response.set_data(json.dumps(
                            {
                                "action": "edit_news",
                                "action_status": "error",
                                "message": f"Bad request: missing '{key}' parameter at file index {index}"
                            }
                        ))
                        return response
                    else:
                        if not isinstance(file_body[key[0]], key[1]):
                            response.set_data(json.dumps(
                                {
                                    "action": "edit_news",
                                    "action_status": "error",
                                    "message": f"Bad request: '{key[0]}' parameter is not of type '{key[1]}' at file index {index}"
                                }
                            ))
                            return response

                
        if not self.news_rpc.check_news_id_exist(data["news_id"]):
            response.status_code = 404
            response.set_data(json.dumps(
                {
                    "action": "update_news",
                    "action_status": "error",
                    "message": "News with given id does not exist"
                }
            ))
            return response
        
        publisher = self.news_rpc.get_news_reporter(news_id)
        response.status_code = 403

        if str(publisher) != str(session["username"]):
            response.set_data(json.dumps(
                {
                    "action": "update_news",
                    "action_status": "error",
                    "message": "Forbidden: you are not the publisher of this news"
                }
            ))
            return response
                
        self.news_rpc.edit_news(news_id,data["title"], data["content"], data["date"], data["author"])
        if "files" in data.keys():
            self.file_rpc.edit_files(news_id, data["files"])
        
        response.status_code = 200
        response.set_data(json.dumps(
            {
                "action": "update_news",
                "action_status": "success",
                "message": "News updated successfully",
            }
        ))
        
        return response
    
    
    @http ("DELETE", "/delete_news/<int:news_id>")
    @session_start
    def delete_news(self, session, request, response, news_id):
        response.mimetype = "application/json"
        
        if not session["username"]:
            response.status_code = 401
            response.set_data(json.dumps(
                {
                    "action": "delete_news",
                    "action_status": "error",
                    "message": "Unauthorized: please login first"
                }
            ))
            return response
        
        if news_id is None:
            response.status_code = 400
            response.set_data(json.dumps(
                {
                    "action": "delete_news",
                    "action_status": "error",
                    "message": "Bad request: missing news id"
                }
            ))
            return response
                
        if not self.news_rpc.delete_news(news_id):
            response.status_code = 404
            response.set_data(json.dumps(
                {
                    "action": "delete_news",
                    "action_status": "error",
                    "message": "News not found"
                }
            ))
            return response
        
        publisher = self.news_rpc.get_news_reporter(news_id)
        response.status_code = 403

        if str(publisher) != str(session["username"]):
            response.set_data(json.dumps(
                {
                    "action": "delete_news",
                    "action_status": "error",
                    "message": "Forbidden: you are not the publisher of this news"
                }
            ))
            return response
        
        self.news_rpc.delete_news(news_id)
        
        response.status_code = 200
        response.set_data(json.dumps(
            {
                "action": "delete_news",
                "action_status": "success",
                "message": "News deleted successfully",
            }  
        ))
        
        return response        