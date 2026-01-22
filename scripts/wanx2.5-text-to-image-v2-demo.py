from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis
import os
import dashscope
import argparse
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


# 创建同步任务
def create_sync_task(prompt, size='1024*1024', negative_prompt=""):
    print('----sync call, please wait a moment----')
    rsp = ImageSynthesis.call(api_key=api_key,
                            model="wan2.5-t2i-preview", # wan2.2-t2i-flash, wan2.5-t2i-preview
                            prompt=prompt,
                            negative_prompt=negative_prompt,
                            n=1,
                            size=size,
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
    

def async_call(prompt, size, negative_prompt=""):
    print('----create task----')
    task_info = create_async_task(prompt, size, negative_prompt)
    print('----wait task done then save image----')
    wait_async_task(task_info)


# 创建异步任务
def create_async_task(prompt, size='1024*1024', negative_prompt=""):
    rsp = ImageSynthesis.async_call(api_key=api_key,
                                    model="wan2.5-t2i-preview", # wan2.2-t2i-flash, wan2.5-t2i-preview
                                    prompt="近景镜头，18岁的中国女孩，古代服饰，圆脸，正面看着镜头，民族优雅的服装，商业摄影，室外，电影级光照，半身特写，精致的淡妆，锐利的边缘。",
                                    negative_prompt=negative_prompt,
                                    n=1,
                                    style='<auto>',
                                    ref_mode='repaint',
                                    ref_strength=1.0,
                                    ref_img="",
                                    sketch_image_url=None, #参考图方式：url链接和本地路径二选一，若两者存在，ref_img参数优先级高于sketch_image_url
                                    size=size,
                                    prompt_extend=True,
                                    watermark=False,
                                    seed=12345)    
    # rsp = ImageSynthesis.async_call(api_key=api_key,
    #                                 model="wan2.5-t2i-preview",  
    #                                 prompt=prompt,
    #                                 negative_prompt="",
    #                                 n=1,
    #                                 size=size,
    #                                 prompt_extend=True,
    #                                 watermark=False,
    #                                 seed=12345)
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
    # 默认提示词（用户选中的文本）
    DEFAULT_PROMPT = '一间有着精致窗户的花店，漂亮的木质门，摆放着花朵'
    DEFAULT_SIZE = '1024*1024'

    # 解析命令行参数
    parser = argparse.ArgumentParser(description='WanX 2.5 Text to Image Generator')
    parser.add_argument(
        '-p', '--prompt',
        type=str,
        default=DEFAULT_PROMPT,
        help=f'Input prompt for image generation (default: "{DEFAULT_PROMPT}")'
    )
    parser.add_argument(
        '--negative-prompt', '-n',
        type=str,
        default="",
        help='Negative prompt for image generation'
    )    
    parser.add_argument(
         '-z', '--size',
        type=str,
        default=DEFAULT_SIZE,
        help=f'Input size for image generation (default: "{DEFAULT_SIZE}"). Either width or height should be between 512 and 1440.'
    )
    parser.add_argument(
         '-s', '--sync',
        action='store_true',
        help='Use synchronous call instead of async'
    )

    args = parser.parse_args()

    # 根据参数选择同步或异步调用
    if args.sync:
        create_sync_task(args.prompt, args.size, args.negative_prompt)
    else:
        async_call(args.prompt, args.size, args.negative_prompt)