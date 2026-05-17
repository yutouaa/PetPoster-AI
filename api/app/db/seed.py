"""数据库初始化种子数据。

用法：uv run python -m app.db.seed
"""

import json

from app.core.config import get_settings
from app.core.password import hash_password
from app.db.session import SessionLocal
from app.models.admin_user import AdminUser
from app.models.template import Template


DEFAULT_TEMPLATES = [
    {
        "name": "古典油画",
        "category": "classic",
        "description": "博物馆肖像感宠物海报，适合主图和纪念照。",
        "cover_url": "",
        "preview_url": "",
        "prompt_template": "为用户上传的宠物照片生成一张古典油画风格海报，强调厚涂笔触、暖色布光、端庄构图和高级画框质感。",
        "negative_prompt": "低清晰度、畸形五官、过度卡通、文字乱码、水印、脏污背景",
        "config": {"slug": "oil", "no": "01", "en": "Oil Painting", "cat": "经典", "localImage": "/assets/images/style-oil.png"},
        "sort_order": 10,
    },
    {
        "name": "东方水墨",
        "category": "classic",
        "description": "留白、墨色层次和东方构图的宠物艺术海报。",
        "cover_url": "",
        "preview_url": "",
        "prompt_template": "基于宠物照片生成东方水墨风格海报，保留宠物神态，使用宣纸肌理、淡墨晕染和克制题字空间。",
        "negative_prompt": "霓虹色、赛博朋克、油腻反光、复杂杂乱背景、水印",
        "config": {"slug": "anime", "no": "02", "en": "Ink Wash", "cat": "经典", "localImage": "/assets/images/style-ink-wash.png"},
        "sort_order": 20,
    },
    {
        "name": "水彩写意",
        "category": "classic",
        "description": "轻盈水彩和柔和纸张质感，适合日常分享。",
        "cover_url": "",
        "preview_url": "",
        "prompt_template": "把宠物照片转化为水彩写意海报，画面柔和、边缘自然晕染、保留宠物毛发层次和明亮眼神。",
        "negative_prompt": "暗沉、硬边塑料感、错乱肢体、文字乱码、水印",
        "config": {"slug": "watercolor", "no": "03", "en": "Watercolor", "cat": "经典", "localImage": "/assets/images/style-watercolor.png"},
        "sort_order": 30,
    },
    {
        "name": "时尚封面",
        "category": "editorial",
        "description": "杂志封面式排版和棚拍质感。",
        "cover_url": "",
        "preview_url": "",
        "prompt_template": "为宠物生成时尚杂志封面海报，使用专业棚拍光线、强构图、留出标题排版空间，整体高级且干净。",
        "negative_prompt": "廉价滤镜、背景混乱、文字乱码、宠物变形、水印",
        "config": {"slug": "magazine", "no": "04", "en": "Editorial", "cat": "潮流", "localImage": "/assets/images/style-editorial.png"},
        "sort_order": 40,
    },
    {
        "name": "复古胶片",
        "category": "vintage",
        "description": "胶片颗粒、暖调和生活感宠物海报。",
        "cover_url": "",
        "preview_url": "",
        "prompt_template": "将宠物照片生成复古胶片风格海报，加入温暖颗粒、自然光、老照片色调和真实生活氛围。",
        "negative_prompt": "过曝、过度锐化、赛博朋克、文字乱码、水印",
        "config": {"slug": "polaroid", "no": "05", "en": "Vintage Film", "cat": "复古", "localImage": "/assets/images/style-vintage-film.png"},
        "sort_order": 50,
    },
    {
        "name": "极简肖像",
        "category": "editorial",
        "description": "极简背景和高端宠物肖像摄影感。",
        "cover_url": "",
        "preview_url": "",
        "prompt_template": "生成极简宠物肖像海报，使用纯净背景、柔和棚拍光、清晰眼神和克制高级的版式。",
        "negative_prompt": "复杂背景、低清晰度、夸张卡通、文字乱码、水印",
        "config": {"slug": "studio", "no": "06", "en": "Minimal Portrait", "cat": "潮流", "localImage": "/assets/images/style-minimal-portrait.png"},
        "sort_order": 60,
    },
    {
        "name": "梦境插画",
        "category": "fun",
        "description": "童话感场景和柔和梦境色彩。",
        "cover_url": "",
        "preview_url": "",
        "prompt_template": "把宠物生成梦境插画海报，加入柔光、奇幻花园、细腻手绘质感和温暖故事氛围。",
        "negative_prompt": "恐怖、阴暗、肢体错乱、文字乱码、水印",
        "config": {"slug": "fairy", "no": "07", "en": "Dreamscape", "cat": "趣味", "localImage": "/assets/images/style-dreamscape.png"},
        "sort_order": 70,
    },
    {
        "name": "炭笔素描",
        "category": "classic",
        "description": "黑白炭笔线条和艺术练习稿质感。",
        "cover_url": "",
        "preview_url": "",
        "prompt_template": "基于宠物照片生成炭笔素描海报，突出轮廓、毛发排线、纸张肌理和艺术工作室氛围。",
        "negative_prompt": "彩色涂鸦、过度卡通、低清晰度、文字乱码、水印",
        "config": {"slug": "ink", "no": "08", "en": "Charcoal", "cat": "经典", "localImage": "/assets/images/style-charcoal.png"},
        "sort_order": 80,
    },
]


def seed_admin() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        existing = db.query(AdminUser).filter_by(username=settings.admin_username).first()
        if existing:
            print(f"管理员 '{settings.admin_username}' 已存在，跳过")
            return

        admin = AdminUser(
            username=settings.admin_username,
            nickname="PetPoster 管理员",
            hashed_password=hash_password(settings.admin_password),
            roles="R_ADMIN,R_SUPER",
        )
        db.add(admin)
        db.commit()
        print(f"管理员 '{settings.admin_username}' 创建成功")
    finally:
        db.close()


def seed_templates() -> None:
    db = SessionLocal()
    try:
        existing_names = {
            item.name for item in db.query(Template.name).all()
        }
        created_count = 0
        for item in DEFAULT_TEMPLATES:
            if item["name"] in existing_names:
                continue
            payload = dict(item)
            payload["config"] = json.dumps(payload["config"], ensure_ascii=False)
            db.add(Template(**payload))
            created_count += 1
        db.commit()
        if created_count:
            print(f"默认模板补齐成功: {created_count} 个")
        else:
            print("默认模板已完整，跳过")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
    seed_templates()
