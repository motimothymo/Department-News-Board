import pickle
import uuid
import redis
from nameko.extensions import DependencyProvider
from werkzeug import Response


class SessionWrapper:
    def __init__(self, connection) -> None:
        self.redis = connection
        self.default_expiration = 60 * 60
        
    def check_session_id(self, session_id):
        return self.redis.exists(session_id)
    
    def create_session_id(self):
        key = str(uuid.uuid4())
        while self.check_session_id(key):
            key = str(uuid.uuid4())
        self.redis.set(key, pickle.dumps({}))
        return key
    
    def get_session_data(self, session_id):
        return pickle.loads(self.redis.get(session_id))
    
    def set_session_data(self, session_id, data):
        self.redis.set(session_id, pickle.dumps(data))
        
    def reset_session_data(self, session_id):
        self.redis.set(session_id, pickle.dumps({}))
        
    def destroy_session_data(self, session_id):
        self.redis.delete(session_id)
        
        
class SessionProvider(DependencyProvider):
    def __init__(self):
        self.client = redis.Redis(host="127.0.0.1", port=6379, db=0)

    def get_dependency(self, worker_ctx):
        return SessionWrapper(self.client)
    
    
class Session:
    def __init__(self, provider, session_id, response):
        self.available = True
        self.provider = provider
        assert self.provider != None
        if session_id is None:
            self.session_id = self.provider.generate_session_id()
        else:
            if self.provider.check_session_id(session_id):
                self.session_id = session_id
            else:
                self.session_id = self.provider.generate_session_id()
        self.response = response
        self.response.set_cookie("SESS_ID", self.session_id, max_age=self.provider.default_expiration)
        
    def __getitem__(self, key):
        assert self.available, "Session timed out"
        data = self.provider.get_session_data(self.session_id)
        if key is None:
            return data
        if key not in data:
            return None
        return data[key]
    
    def __setitem__(self, key, value):
        assert self.available, "Session timed out"
        data = self.provider.get_session_data(self.session_id)
        data[key] = value
        self.provider.set_session_data(self.session_id, data)

    def __delitem__(self, key):
        data = self.provider.get_session_data(self.session_id)
        if key in data:
            del data[key]
        self.provider.set_session_data(self.session_id, data)

    def __contains__(self, key):
        assert self.available, "Session timed out"
        data = self.provider.get_session_data(self.session_id)
        return key in data

    def __call__(self):
        assert self.available, "Session timed out"
        return self[None]

    def reset(self):
        assert self.available, "Session timed out"
        self.provider.reset_session_data(self.session_id)

    def destroy(self):
        assert self.available, "Session timed out"
        self.available = False
        self.provider.destroy_session_data(self.session_id)
        self.response.set_cookie("SESS_ID", "", expires=0)


def session_start(fn):
    def wrapper(*args, **kwargs):
        response = Response()
        session = Session(args[0].session_provider, args[1].cookies.get("SESS_ID"), response)
        return fn(*args, session, response)
    return wrapper