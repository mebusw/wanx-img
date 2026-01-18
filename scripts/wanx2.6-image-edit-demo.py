import os
import argparse
import dashscope
from dashscope.aigc.image_generation import ImageGeneration
from dashscope.api_entities.dashscope_response import Message
from dotenv import load_dotenv
from http import HTTPStatus

# 以下代码仅适合wan2.6版本模型。
# 请确保 DashScope Python SDK 版本不低于 1.25.8，再运行以下代码。
# 若版本过低，可能会触发 “url error, please check url!” 等错误。

# 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：https://dashscope-intl.aliyuncs.com/api/v1
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

load_dotenv()
# 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
# 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
api_key = os.getenv("DASHSCOPE_API_KEY")


# 创建同步任务
def create_sync_task(prompt, image_urls):
    message = Message(
        role="user",
        # 支持本地文件 如 "image": "file://umbrella1.png"
        content=[{"text": prompt}] + [{"image": url} for url in image_urls]
    )
    print("----sync call, please wait a moment----")
    rsp = ImageGeneration.call(
            model='wan2.6-image',
            api_key=api_key,
            messages=[message],
            negative_prompt="",
            prompt_extend=True,
            watermark=False,
            n=1,
            enable_interleave=False,
            size="1280*1280"
        )

    print(rsp)
    return rsp


def async_call(prompt, image_urls):
    print('----create task----')
    task = create_async_task(prompt, image_urls)
    print('----wait task done then save image----')
    wait_for_completion(task)

# 创建异步任务
def create_async_task(prompt, image_urls):
    print("Creating async task...")
    message = Message(
        role="user",
        content=[{'text': prompt}] + [{'image': url} for url in image_urls]
    )
    response = ImageGeneration.async_call(
        model="wan2.6-image",
        api_key=api_key,
        messages=[message],
        negative_prompt="",
        prompt_extend=True,
        watermark=False,
        n=1,
        enable_interleave=False,
        size="1280*1280"
    )

    if response.status_code == 200:
        print("Task created successfully:", response)
        return response  # 返回任务ID
    else:
        raise Exception(f"Failed to create task: {response.code} - {response.message}")

# 等待任务完成
def wait_for_completion(task_response):
    print("Waiting for task completion...")
    status = ImageGeneration.wait(task=task_response, api_key=api_key)
    
    if status.output.task_status == "SUCCEEDED":
        print("Task succeeded!")
        print("Response:", status)
    else:
        raise Exception(f"Task failed with status: {status.output.task_status}")

# 获取异步任务信息
def fetch_task_status(task):
    print("Fetching task status...")
    status = ImageGeneration.fetch(task=task, api_key=api_key)
    
    if status.status_code == HTTPStatus.OK:
        print("Task status:", status.output.task_status)
        print("Response details:", status)
    else:
        print(f"Failed to fetch status: {status.code} - {status.message}")

# 取消异步任务
def cancel_task(task):
    print("Canceling task...")
    response = ImageGeneration.cancel(task=task, api_key=api_key)
    
    if response.status_code == HTTPStatus.OK:
        print("Task canceled successfully:", response.output.task_status)
    else:
        print(f"Failed to cancel task: {response.code} - {response.message}")

# 主执行流程
if __name__ == "__main__":
    # 默认提示词
    DEFAULT_PROMPT = '参考图1的风格和图2的背景，生成番茄炒蛋'

    # 默认图片URL列表
    DEFAULT_IMAGES = [
        'https://cdn.wanx.aliyuncs.com/tmp/pressure/umbrella1.png',
        'https://img.alicdn.com/imgextra/i3/O1CN01SfG4J41UYn9WNt4X1_!!6000000002530-49-tps-1696-960.webp'
    ]

    # 解析命令行参数
    parser = argparse.ArgumentParser(description='WanX 2.6 Image Edit Generator')
    parser.add_argument(
        '--prompt', '-p',
        type=str,
        default=DEFAULT_PROMPT,
        help=f'Input prompt for image generation (default: "{DEFAULT_PROMPT}")'
    )
    parser.add_argument(
        '--images', '-i',
        type=str,
        nargs='+',
        default=DEFAULT_IMAGES,
        help=f'Input image URLs for reference (default: {DEFAULT_IMAGES})'
    )
    parser.add_argument(
        '--sync', '-s',
        action='store_true',
        help='Use synchronous call instead of async'
    )

    args = parser.parse_args()

    # 根据参数选择同步或异步调用
    if args.sync:
        create_sync_task(args.prompt, args.images)
    else:
        async_call(args.prompt, args.images)
