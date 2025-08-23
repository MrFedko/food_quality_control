import dropbox
import os


class DropboxClient:
    def __init__(self, app_key: str, app_secret: str, refresh_token: str):
        """
        token: Dropbox API access token
        """
        self.dbx = dropbox.Dropbox(
            oauth2_refresh_token=refresh_token,
            app_key=app_key,
            app_secret=app_secret
        )

    def upload_file(self, local_path: str, dropbox_path: str):
        # Добавляем "/" в начало, если его нет
        if not dropbox_path.startswith("/"):
            dropbox_path = "/" + dropbox_path

        with open(local_path, "rb") as f:
            self.dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)

    def get_shared_link(self, dropbox_path: str):
        """
        Получает публичную ссылку для файла
        """
        # Создаем ссылку, если её ещё нет
        try:
            link = self.dbx.sharing_create_shared_link_with_settings(dropbox_path)
        except dropbox.exceptions.ApiError as e:
            # Если ссылка уже есть, используем существующую
            links = self.dbx.sharing_list_shared_links(path=dropbox_path, direct_only=True).links
            if links:
                link = links[0]
            else:
                raise e

        # Преобразуем в прямую ссылку для =IMAGE()
        url = link.url.replace("?dl=0", "?raw=1")
        return url

    def upload_and_get_url(self, local_path: str, dropbox_path: str):
        """
        Загружает файл и возвращает прямую ссылку для вставки в Google Sheets
        """
        self.upload_file(local_path, dropbox_path)
        return self.get_shared_link(dropbox_path)
