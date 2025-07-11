import os

from Tea.exceptions import TeaException
from alibabacloud_iqs20241111 import models
from alibabacloud_iqs20241111.client import Client
from alibabacloud_tea_openapi import models as open_api_models


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client() -> Client:
        config = open_api_models.Config(
            # 从环境变量加载AK/SK
            access_key_id=os.getenv('ALIYUN_ACCESS_KEY_ID'),
            access_key_secret=os.getenv('ALIYUN_ACCESS_KEY_SECRET')
        )
        config.endpoint = f'iqs.cn-zhangjiakou.aliyuncs.com'
        return Client(config)

    @staticmethod
    def main() -> None:
        client = Sample.create_client()
        run_instances_request = models.UnifiedSearchRequest(
            body=models.UnifiedSearchInput(
                query='杭州美食',
                time_range='NoLimit',
                contents=models.RequestContents(
                    summary=True,
                    main_text=True,
                )
            )
        )
        try:
            response = client.unified_search(run_instances_request)
            print(
                f"api success, request_id:{response.body.request_id}, size:{len(response.body.page_items)}, server_cost:{response.body.search_information.search_time}")
            if len(response.body.scene_items) > 0:
                print(f"scene_items:{response.body.scene_items[0]}")
            for index, item in enumerate(response.body.page_items):
                print(f"{index}. {'-' * 20}")
                print(f"title:{item.title}")
                print(f"snippet:{item.snippet}")
                print(f"summary:{item.summary}")
                print(f"published_time:{item.published_time}")
                print(f"link:{item.link}")
                print(f"rerank_score:{item.rerank_score}")

        except TeaException as e:
            code = e.code
            request_id = e.data.get("requestId")
            message = e.data.get("message")
            print(f"api exception, requestId:{request_id}, code:{code}, message:{message}")


if __name__ == '__main__':
    Sample.main()