"""智谱 AI 图片生成 API 调用封装"""
import requests
import json
import time
from config import ZHIPU_API_KEY

GLM_BASE = "https://open.bigmodel.cn/api/paas/v4"

def _call_zhipu_sync(prompt, size, model):
    """调用智谱同步生成接口（CogView-4 用）"""
    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size
    }
    resp = requests.post(
        f"{GLM_BASE}/images/generations",
        headers=headers, json=payload, timeout=120
    )
    resp.raise_for_status()
    data = resp.json()
    img_list = data.get("data", [])
    img_url = img_list[0].get("url", "") if img_list else ""
    if img_url:
        return {"success": True, "image_url": img_url, "model": model}
    return {"success": False, "error": "未返回图片 URL", "raw": data}


def _call_zhipu_async(prompt, size, model):
    """调用智谱异步画图接口（GLM-Image 用）"""
    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size
    }
    resp = requests.post(
        f"{GLM_BASE}/async/images/generations",
        headers=headers, json=payload, timeout=30
    )
    resp.raise_for_status()
    data = resp.json()
    task_id = data.get("id")
    if not task_id:
        return {"success": False, "error": "智谱 API 未返回任务 ID", "raw": data}

    task_url = f"{GLM_BASE}/async-result/{task_id}"
    for i in range(60):
        time.sleep(5)
        sr = requests.get(task_url, headers=headers, timeout=15)
        if sr.status_code != 200:
            continue
        result = sr.json()
        status = result.get("task_status", "")
        if status == "SUCCESS":
            img_list = result.get("image_result", result.get("data", []))
            img_url = img_list[0].get("url", "") if img_list else ""
            if img_url:
                return {"success": True, "image_url": img_url, "model": model}
            return {"success": False, "error": "任务成功但未返回图片 URL", "raw": result}
        elif status in ("FAIL", "FAILED"):
            return {"success": False, "error": result.get("msg", "AI 生成失败")}
    return {"success": False, "error": f"AI 生成超时，任务ID: {task_id}"}


# CogView-4 使用同步 API，GLM-Image 使用异步 API
MODEL_API_MAP = {
    "glm-image": _call_zhipu_async,
    "cogview-4": _call_zhipu_sync,
}


def generate_image(prompt, size="1280x1280", model="glm-image"):
    """
    根据模型选择对应调用方式
    返回: {"success": true, "image_url": "..."}
          {"success": false, "error": "..."}
    """
    caller = MODEL_API_MAP.get(model, _call_zhipu_async)
    try:
        return caller(prompt, size, model)
    except requests.exceptions.Timeout:
        return {"success": False, "error": "请求智谱 API 超时"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"调用智谱 API 失败: {str(e)}"}
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        return {"success": False, "error": f"解析智谱 API 返回失败: {str(e)}"}
