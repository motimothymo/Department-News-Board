from nameko.rpc import rpc
from dependencies.database_news import DatabaseProvider

class NewsService:
    
    name="news_service"
    database = DatabaseProvider()
    
    @rpc
    def get_all_news(self):
        return self.database.get_all_news()
    
    @rpc
    def get_news_by_id(self, news_id):
        try:
            result = self.database.get_news_by_id(news_id)
        except Exception as e:
            return False, e
        
        return True, result
    
    @rpc
    def get_news_reporter_by_id(self, news_id):
        try:
            result = self.database.get_news_reporter_by_id(news_id)
        except Exception as e:
            return False, e
        
        return True, result
    
    @rpc
    def add_news(self, news_title, news_content, news_date, news_reporter):
        try:
            result = self.database.add_news(news_title, news_content, news_date, news_reporter)
        except Exception as e:
            return False, e
        
        return True, result
    
    @rpc
    def edit_news(self, news_id, news_title, news_content, news_date, news_reporter):
        try:
            result = self.database.edit_news(news_id, news_title, news_content, news_date, news_reporter)
        except Exception as e:
            return False, e
        
        return True, result
    
    @rpc
    def delete_news(self, news_id):
        try:
            result = self.database.delete_news(news_id)
        except Exception as e:
            return False, e
        
        return True, result
            