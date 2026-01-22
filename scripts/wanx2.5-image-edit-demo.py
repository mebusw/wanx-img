import os
import argparse
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import dashscope
import requests
from dashscope import ImageSynthesis
from dotenv import load_dotenv

# 以下代码仅适合wan2.5及以下版本模型。
# 请确保 DashScope Python SDK 版本不低于 1.25.2，再运行以下代码。
# 若版本过低，可能会触发 “url error, please check url!” 等错误。

# 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：https://dashscope-intl.aliyuncs.com/api/v1
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

load_dotenv()
# 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
# 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
api_key = os.getenv("DASHSCOPE_API_KEY")

# 使用公网图片 URL
image_url_1 = "https://img.alicdn.com/imgextra/i3/O1CN0157XGE51l6iL9441yX_!!6000000004770-49-tps-1104-1472.webp"
image_url_2 = "https://img.alicdn.com/imgextra/i3/O1CN01SfG4J41UYn9WNt4X1_!!6000000002530-49-tps-1696-960.webp"
mask_image_url = "http://wanx.alicdn.com/material/20250318/description_edit_with_mask_3_mask.png"
base_image_url = "http://wanx.alicdn.com/material/20250318/description_edit_with_mask_3.jpeg"
# 或使用本地文件
# image_url_1 = "file://" + "/path/to/your/image_1.png"     # Linux/macOS
# image_url_2 = "file://" + "C:/path/to/your/image_2.png"  # Windows

# 创建同步任务
def create_sync_task(prompt, image_urls, negative_prompt="", mask_image_url=None, base_image_url=None):
    print('----sync call, please wait a moment----')
    rsp = ImageSynthesis.call(api_key=api_key,
                            model="wan2.5-i2i-preview",
                            prompt=prompt,
                            images=image_urls,
                            negative_prompt=negative_prompt,
                            mask_image_url=mask_image_url,
                            base_image_url=base_image_url,
                            n=1,
                            size="1280*1280",
                            prompt_extend=True,
                            watermark=False,
                            seed=12345)
    print('response: %s' % rsp)
    if rsp.status_code == HTTPStatus.OK:
        # 在当前目录下保存图片
        for result in rsp.output.results:
            file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
            with open('./%s' % file_name, 'wb+') as f:
                f.write(requests.get(result.url).content)
    else:
        print('sync_call Failed, status_code: %s, code: %s, message: %s' %
            (rsp.status_code, rsp.code, rsp.message))


def async_call(prompt, image_urls, negative_prompt="", mask_image_url=None, base_image_url=None):
    print('----create task----')
    task_info = create_async_task(prompt, image_urls, negative_prompt, mask_image_url, base_image_url)
    print('----wait task----')
    wait_async_task(task_info)


# 创建异步任务
def create_async_task(prompt, image_urls, negative_prompt="", mask_image_url=None, base_image_url=None):
    # rsp = ImageSynthesis.async_call(api_key=api_key,
    #                           model="wanx2.1-imageedit",
    #                           function="description_edit_with_mask",
    #                           prompt="陶瓷兔子拿着陶瓷小花",
    #                           mask_image_url=mask_image_url,
    #                           base_image_url=base_image_url,
    #                           n=1)
    # rsp = ImageSynthesis.async_call(api_key=api_key,
    #                             model="wanx2.1-imageedit",
    #                             function="description_edit",
    #                             prompt="图中的闹钟放在餐桌的花瓶旁边",
    #                             mask_image_url=None,
    #                             base_image_url=image_url_1,
    #                             n=1)   
    rsp = ImageSynthesis.async_call(api_key=api_key,
                                model="wan2.5-i2i-preview", 
                                prompt=prompt,
                                images=image_urls,
                                negative_prompt=negative_prompt,
                                mask_image_url=mask_image_url,
                                base_image_url=base_image_url,
                                n=1,
                                # size="1280*1280",
                                prompt_extend=True,
                                watermark=False,
                                seed=12345) 
    print(rsp)
    if rsp.status_code == HTTPStatus.OK:
        print(rsp.output)
    else:
        print('Failed, status_code: %s, code: %s, message: %s' %
              (rsp.status_code, rsp.code, rsp.message))
    return rsp


# 等待异步任务结束
def wait_async_task(task):
    rsp = ImageSynthesis.wait(task=task, api_key=api_key)
    print(rsp)
    if rsp.status_code == HTTPStatus.OK:
        print(rsp.output)
        # save file to current directory
        for result in rsp.output.results:
            file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
            with open('./output/%s' % file_name, 'wb+') as f:
                f.write(requests.get(result.url).content)
    else:
        print('Failed, status_code: %s, code: %s, message: %s' %
              (rsp.status_code, rsp.code, rsp.message))


# 获取异步任务信息
def fetch_task_status(task):
    status = ImageSynthesis.fetch(task=task, api_key=api_key)
    print(status)
    if status.status_code == HTTPStatus.OK:
        print(status.output.task_status)
    else:
        print('Failed, status_code: %s, code: %s, message: %s' %
              (status.status_code, status.code, status.message))


# 取消异步任务，只有处于PENDING状态的任务才可以取消
def cancel_task(task):
    rsp = ImageSynthesis.cancel(task=task, api_key=api_key)
    print(rsp)
    if rsp.status_code == HTTPStatus.OK:
        print(rsp.output.task_status)
    else:
        print('Failed, status_code: %s, code: %s, message: %s' %
              (rsp.status_code, rsp.code, rsp.message))


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
    parser = argparse.ArgumentParser(description='WanX 2.5- Image Edit Generator')
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
    parser.add_argument(
        '--negative-prompt', '-n',
        type=str,
        default="",
        help='Negative prompt for image generation'
    )
    parser.add_argument(
        '--mask-image-url', '-m',
        type=str,
        default=None,
        help='Mask image URL for editing (optional)'
    )
    parser.add_argument(
        '--base-image-url', '-b',
        type=str,
        default=None,
        help='Base image URL for editing (optional)'
    )

    args = parser.parse_args()

    # 根据参数选择同步或异步调用
    if args.sync:
        create_sync_task(args.prompt, args.images, args.negative_prompt, args.mask_image_url, args.base_image_url)
    else:
        async_call(args.prompt, args.images, args.negative_prompt, args.mask_image_url, args.base_image_url)
