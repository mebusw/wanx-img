---
name: gen-img
description: generate images with LLM 
allowed-tools: Read, Bash
---

## Overview

1. run scripts to generate images with user input prompt,   synchronously by default
3. output refined prompts and url of generated images

## Additional resources

N/A

## Usage Examples

**Use custom prompt:**
```bash
/Users/jacky/.pyenv/versions/py312-ai-rag/bin/python "/Users/jacky/work/08 大模型编程原型机AI-RAG/demo/wanx2.6-text-to-image-v2-demo.py" --prompt "一只可爱的猫咪在花园里玩耍"
```

**Use synchronous call with custom prompt:**
```bash
/Users/jacky/.pyenv/versions/py312-ai-rag/bin/python "/Users/jacky/work/08 大模型编程原型机AI-RAG/demo/wanx2.6-text-to-image-v2-demo.py" -p "美丽的日落风景" --sync
```
