---
name: wanx-img
description: Generate or edit images using WanX (Alibaba's text-to-image model)
allowed-tools: Read, Bash
---

## Overview

This skill provides commands for generating and editing images using the WanX 2.6 model from Alibaba.

## Workflow

1. decide user's intent: whether to generate a new image, or edit given images
2. if user provides images urls/paths, you don't need to read the files but only pass them to scripts
3. run a proper script to generate or edit images with user input prompt, synchronously by default
4. output original prompts, extended prompts and url of generated images


## Available Scripts

- `wanx2.6-text-to-image-v2-demo.py` - Generate images from text prompts
- `wanx2.6-image-edit-demo.py` - Edit images with text prompts, optionally with reference/mask images


## Usage Examples

- **Use custom prompt to generate image**
```bash
/Users/jacky/.pyenv/versions/py312-ai-rag/bin/python "/Users/jacky/work/08 大模型编程原型机AI-RAG/demo/wanx2.6-text-to-image-v2-demo.py" --prompt "一只可爱的猫咪在花园里玩耍"
```

- **Use synchronous call with custom prompt to generate image**
```bash
/Users/jacky/.pyenv/versions/py312-ai-rag/bin/python "/Users/jacky/work/08 大模型编程原型机AI-RAG/demo/wanx2.6-text-to-image-v2-demo.py" -p "美丽的日落风景" --sync
```

- **Use custom prompt and referencing images to edit image**
```bash
/Users/jacky/.pyenv/versions/py312-ai-rag/bin/python "/Users/jacky/work/08 大模型编程原型机AI-RAG/demo/wanx2.6-image-edit-demo.py" --prompt "参考图1的风格和图2的背景，生成番茄炒蛋" --images http://1.img http://2.img
```

- **Use synchronous call with custom prompt to edit iamge**
```bash
/Users/jacky/.pyenv/versions/py312-ai-rag/bin/python "/Users/jacky/work/08 大模型编程原型机AI-RAG/demo/wanx2.6-image-edit-demo.py" -p "参考图1的风格和图2的背景，生成番茄炒蛋" --sync
```


## Requirements

- Python 3.12+
- LLM API credentials configured in demo scripts
- DashScope Python SDK 1.25.8+

