import time
import json
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from requests import get
from math import ceil
from urllib.parse import unquote, urlparse


class Fetcher():
    def __init__(self, blog_id, download_dir, header):
        self.blog_id = blog_id
        self.download_dir = Path(download_dir).joinpath(f"{self.blog_id}")
        self.header = header
        self.fetch_time = None
        self.post_count = None
        self.post_data = dict()
        self._check_dir()

    def _check_dir(self):
        if not Path(self.download_dir).exists(): Path(self.download_dir).mkdir(parents=False, exist_ok=True)

    def _get_thumbnail(self, img_src, quality, width):
        thumbnail_url = f"https://search.pstatic.net/common/?autoRotate=true&quality={quality}&type=w{width}&src={img_src}"
        return thumbnail_url

    def _convert_original_source(self, img_src):
        if urlparse(img_src).netloc != ("storep-phinf.pstatic.net" or "https://dthumb-phinf.pstatic.net"):
            split_query = img_src.split("?")
            original_image_source = split_query[0].replace("postfiles", "blogfiles")
            return original_image_source
        else:
            pass

    def _fetch_post_count(self):
        blog_url = f"https://blog.naver.com/WidgetListAsync.naver?blogId={self.blog_id}&enableWidgetKeys=menu%2Cprofile%2Ccounter%2Ccategory%2Csearch%2Crss%2Ccontent%2Cgnb%2Cexternalwidget"
        tmp_header = self.header
        tmp_header["Referer"] = f"https://blog.naver.com/PostList.naver?blogId={self.blog_id}&widgetTypeCall=true&directAccess=true"

        response = get(blog_url, headers=tmp_header)

        if not(response.status_code == 200):
            # Response Error
            print(f"Error Occurred! -> HTTP Response Status Codes: {response.status_code}")
        else:
            widget_html = response.content
            parsed_widget_html = BeautifulSoup(widget_html, 'html.parser')
            self.post_count = int(parsed_widget_html.select_one("span.num").text[1:-1])

    def fetch_blog_data(self):
        start_time = time.time()
        self._fetch_post_count()
        request_count = ceil(self.post_count / 30)

        for page_number in range(1, request_count + 1):
            fetch_url = f"https://blog.naver.com/PostTitleListAsync.naver?blogId={self.blog_id}&viewdate=&currentPage={page_number}&categoryNo=&parentCategoryNo=&countPerPage=30"
            response = get(fetch_url, headers=self.header)

            if not(response.status_code == 200):
                # Response Error
                print(f"Error Occurred! -> HTTP Response Status Codes: {response.status_code}")
            else:
                data = json.loads(response.text.replace("'", '"').replace('\\0xa', ' '))

                for post in data["postList"]:
                    post_id = post["logNo"]
                    title = unquote(post["title"]).replace('+', ' ')
                    publish_date = post["addDate"]

                    self.post_data[post_id] = {
                        "POST_URL": f"https://blog.naver.com/{self.blog_id}/{post_id}",
                        "TITLE" : title,
                        "PUBLISH_DATE": publish_date, 
                        "IMAGES": dict()
                    }
                    
        self.fetch_time = f"{time.time() - start_time:.3f} sec"

    def fetch_post_images_list(self, post_id):
        post_url = f"https://blog.naver.com/PostView.naver?blogId={self.blog_id}&logNo={post_id}"
        response = get(post_url, headers=self.header)
        image_list = list()
        
        if not(response.status_code == 200):
            # Response Error
            print(f"Error Occurred! -> HTTP Response Status Codes: {response.status_code}")
        else:
            post_html = response.content
            parsed_post_html = BeautifulSoup(post_html, "html.parser")
            post = parsed_post_html.select_one("div.se-main-container")
            try:
                html_image_sources = post.select("img")

                for edited_image_source in html_image_sources:
                    original_image = self._convert_original_source(edited_image_source["src"])
                    if original_image != None:
                        image_list.append(original_image)

                self.post_data[post_id]["IMAGES"] = {"IMAGE_COUNT": f"{len(image_list)}", "IMAGE_SOURCE": image_list}

            except Exception as e:
                # Post without Image
                pass