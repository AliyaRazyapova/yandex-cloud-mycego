import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.http import HttpRequest, HttpResponseBase
from typing import Optional, Dict, Any

import yandex_cloud_mycego.settings


def index(request: HttpRequest) -> HttpResponseBase:
    """
    Обрабатывает запрос к главной странице, возвращает форму для ввода публичной ссылки на Яндекс.Диск.

    :param request: Объект запроса от клиента.
    :return: HttpResponse с рендером шаблона index.html.
    """
    return render(request, "diskapp/index.html")


def files_list(request: HttpRequest) -> HttpResponseBase:
    """
    Обрабатывает запрос для получения списка файлов на Яндекс.Диске по публичной ссылке.

    :param request: Объект запроса от клиента.
    :return: HttpResponse с рендером шаблона file_list.html или редирект на главную страницу.
    """
    public_key: Optional[str] = request.GET.get("public_key")
    if not public_key:
        return redirect("index")

    response = requests.get(yandex_cloud_mycego.settings.YANDEX_DISK_API_URL, params={"public_key": public_key})

    if response.status_code == 200:
        files: Dict[str, Any] = response.json()["_embedded"]["items"]
        return render(request, "diskapp/file_list.html", {"files": files, "public_key": public_key})
    else:
        return HttpResponse("Не удалось получить список файлов.", status=400)


def download_file(request: HttpRequest) -> HttpResponseBase:
    """
    Обрабатывает запрос для скачивания файла с Яндекс.Диска по указанному пути и публичной ссылке.

    :param request: Объект запроса от клиента.
    :return: HttpResponse с содержимым файла для скачивания или ошибка.
    """
    path: Optional[str] = request.GET.get("path")
    public_key: Optional[str] = request.GET.get("public_key")

    if not path or not public_key:
        return redirect("index")

    download_url: str = f"{yandex_cloud_mycego.settings.YANDEX_DISK_API_URL}/download"
    response = requests.get(download_url, params={"public_key": public_key, "path": path})

    if response.status_code == 200:
        file_url: str = response.json()["href"]
        file_response = requests.get(file_url)

        if file_response.status_code == 200:
            file_name: str = path.split("/")[-1]
            response = HttpResponse(file_response.content, content_type="application/octet-stream")
            response["Content-Disposition"] = f"attachment; filename={file_name}"
            return response
        else:
            return HttpResponse("Не удалось скачать файл.", status=400)
    else:
        return HttpResponse("Не удалось получить ссылку на скачивание.", status=400)
