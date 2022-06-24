from nameko.rpc import rpc
import uuid
from dependencies.database_files import DatabaseProvider
import os


class FileService:

    name = 'files_service'
    database = DatabaseProvider()

    @rpc
    def get_all_files_by_news_id(self, news_id):
        files_meta = self.database.get_files_by_news_id(news_id)
        files = []
        for file_meta in files_meta:
            file_base64 = open(f"/files/{file_meta['filepath']}").read()
            files.append(
                {
                    'file_name': file_meta['filename'],
                    'base64_data': file_base64
                }
            )
        return files

    @rpc
    def post_files(self, news_id, file_name_datastring_list):
        for file_name_datastring in file_name_datastring_list:
            generated_file_uuid = uuid.uuid1()
            open(f"/files/{generated_file_uuid}", "w").write(file_name_datastring["base64_data"])
            self.database.add_new_file(news_id, file_name_datastring["file_name"], generated_file_uuid)

    @rpc
    def edit_files(self, news_id, file_name_datastring_list):
        self.delete_all_files_from_news_id(news_id)
        self.post_files(news_id, file_name_datastring_list)

    @rpc
    def delete_all_files_from_news_id(self, news_id):
        all_files = self.database.get_files_by_news_id(news_id)

        for file in all_files:
            try:
                os.remove(f"/files/{file['filepath']}")
            except:
                continue

        self.database.delete_all_files_from_news_id(news_id)