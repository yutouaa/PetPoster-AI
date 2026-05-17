"""本地 OpenAI 兼容图像生成接口的冒烟测试

默认目标地址:
    http://127.0.0.1:4754/v1/images/generations

使用方法:
    uv run python test_gpt_images_2_generation.py
    uv run python test_gpt_images_2_generation.py --api-key sk-xxx
    uv run python test_gpt_images_2_generation.py --api-key sk-xxx --auth-header x-api-key
"""

from __future__ import annotations

import argparse
import base64
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

# 默认配置
DEFAULT_BASE_URL = "http://127.0.0.1:4754/v1"  # 本地 API 服务地址
DEFAULT_MODEL = "gpt-image-2-vip"  # 默认使用的图像生成模型
DEFAULT_API_KEY = ""  # 通过 --api-key 或环境变量 OPENAI_API_KEY 提供


DEFAULT_PROMPT = (
    "一个被解剖并陈列的鲍鱼标本，像博物馆自然学家的珍贵发现物。一半保留鲍鱼外壳和自然表面，呈现虹彩般的珍珠层、粗糙的贝壳纹理和自然的有机色彩变化；另一半被切至核心，清晰细致地展示内部肉质、肌肉结构、外套膜、消化组织和层次分明的解剖结构。"
    "背景为纯黑色天鹅绒。鲍鱼悬浮在画面中央，像某种珍贵而危险的生物标本。"
    "标注文字紧贴各个结构边缘，采用手写感衬线字体，绝不漂浮在空中。每条标注包含三行：结构名称、成分数据，以及通俗易懂的解释。主标题位于左上角，文字为“鲍鱼标本”，使用暖象牙色大写风格字体。"
    "整体美学风格：奥杜邦式自然主义插画、卡拉瓦乔式戏剧性光影，以及极致美丽的科学摄影相结合。4K 精度，标本级布光，极端细致的内部细节。真实主义风格，不是示意图，不是卡通。每一种材质都具有真实的物理质感：粗糙的贝壳、光滑的珍珠层、湿润的肉质、致密的肌肉、柔软的外套膜、多孔的有机组织。"
)


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="测试本地 OpenAI 兼容的图像生成接口")
    parser.add_argument(
        "--base-url", default=os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL)
    )
    parser.add_argument(
        "--api-key",
        default=(
            os.getenv("OPENAI_API_KEY")
            or os.getenv("X_API_KEY")
            or os.getenv("LOCAL_API_KEY")
            or DEFAULT_API_KEY
        ),
    )
    parser.add_argument(
        "--auth-header",
        choices=("authorization", "x-api-key", "both"),
        default="both",
        help="How to send --api-key. Default sends both common OpenAI-compatible headers.",
    )
    parser.add_argument(
        "--model", default=os.getenv("OPENAI_IMAGE_MODEL", DEFAULT_MODEL)
    )
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--output-dir", default="generated_images")
    return parser.parse_args()


def build_headers(api_key: str | None, auth_header: str) -> dict[str, str]:
    """构建 HTTP 请求头，根据配置添加认证信息"""
    headers = {"Content-Type": "application/json"}
    if api_key:
        # 根据 auth_header 参数决定使用哪种认证方式
        if auth_header in {"authorization", "both"}:
            headers["Authorization"] = f"Bearer {api_key}"
        if auth_header in {"x-api-key", "both"}:
            headers["X-API-Key"] = api_key
    return headers


def save_image_from_item(
    client: httpx.Client,
    item: dict[str, Any],
    output_path: Path,
) -> None:
    """从响应数据中保存图片到本地文件

    支持两种格式：
    1. base64 编码的图片数据 (b64_json 或 b64 字段)
    2. 图片 URL (url 字段)
    """
    # 优先尝试 base64 格式
    b64_json = item.get("b64_json") or item.get("b64")
    if isinstance(b64_json, str) and b64_json.strip():
        output_path.write_bytes(base64.b64decode(b64_json))
        return

    # 其次尝试 URL 格式
    image_url = item.get("url")
    if isinstance(image_url, str) and image_url.strip():
        response = client.get(image_url)
        response.raise_for_status()
        output_path.write_bytes(response.content)
        return

    # 如果两种格式都不存在，抛出错误
    raise RuntimeError(
        "图片响应数据中既没有 b64_json 也没有 url 字段:\n"
        f"{json.dumps(item, ensure_ascii=False, indent=2)}"
    )


def main() -> None:
    """主函数：调用图像生成 API 并保存结果"""
    args = parse_args()
    base_url = args.base_url.rstrip("/")
    endpoint = f"{base_url}/images/generations"

    # 构建请求负载
    payload = {
        "model": args.model,
        "prompt": args.prompt,
        "size": args.size,
        "n": 1,  # 生成 1 张图片
    }

    # 准备输出目录和文件名
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"{args.model}_test_{timestamp}.png"

    print(f"POST {endpoint}")
    print(f"model={args.model} size={args.size}")

    # 记录开始生成时间
    start_time = datetime.now()
    print(f"开始生成图片: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    with httpx.Client(
        timeout=None,  # 不设置超时限制，因为图像生成时间较长
        headers=build_headers(args.api_key, args.auth_header),
    ) as client:
        # 发送图像生成请求
        response = client.post(endpoint, json=payload)

        # 记录结束时间并计算耗时
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        print(f"生成完成: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"耗时: {elapsed:.2f} 秒")
        print(f"status={response.status_code}")

        # 处理错误响应
        if response.status_code >= 400:
            print(response.text)
            if response.status_code == 401 and not args.api_key:
                print(
                    "缺少 API 密钥 (missing_api_key=true)\n"
                    "请使用 --api-key 参数，或设置环境变量 OPENAI_API_KEY / X_API_KEY / LOCAL_API_KEY"
                )
            raise SystemExit(1)

        # 解析响应数据
        data = response.json()
        items = data.get("data")
        if not isinstance(items, list) or not items:
            raise RuntimeError(
                "响应中没有包含非空的 data 数组:\n"
                f"{json.dumps(data, ensure_ascii=False, indent=2)}"
            )

        # 保存图片
        save_image_from_item(client, items[0], output_path)

    print(f"图片已保存: {output_path.resolve()}")


if __name__ == "__main__":
    main()
