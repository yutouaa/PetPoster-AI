"""一次性脚本：根据 generation_tasks 历史数据回填 template.usage_count / success_count。

使用方法：
    cd api
    uv run python scripts/backfill_template_stats.py --dry-run   # 预览
    uv run python scripts/backfill_template_stats.py             # 实际写入

注意：
- 幂等运行：每次都先清零再按当前 generation_tasks 全量聚合，可重复执行。
- 仅统计 status in (success, failed) 的终态任务（pending/processing 不计入）。
- success_count 仅累计 status=success；usage_count 累计 success + failed。
"""
import argparse
import sys
from pathlib import Path

# 让脚本能直接 import app.*
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import case, func  # noqa: E402

from app.db.session import SessionLocal  # noqa: E402
from app.models.generation_task import GenerationTask  # noqa: E402
from app.models.template import Template  # noqa: E402


def backfill(dry_run: bool = False) -> dict:
    db = SessionLocal()
    try:
        rows = (
            db.query(
                GenerationTask.template_id,
                func.count(GenerationTask.id).label("total"),
                func.sum(case((GenerationTask.status == "success", 1), else_=0)).label("success"),
                func.sum(case((GenerationTask.status == "failed", 1), else_=0)).label("failed"),
            )
            .filter(GenerationTask.status.in_(["success", "failed"]))
            .group_by(GenerationTask.template_id)
            .all()
        )

        stats = {
            r.template_id: {
                "total": int(r.total or 0),
                "success": int(r.success or 0),
                "failed": int(r.failed or 0),
            }
            for r in rows
        }

        templates = db.query(Template).all()
        updates = 0
        for t in templates:
            new_usage = stats.get(t.id, {}).get("success", 0) + stats.get(t.id, {}).get("failed", 0)
            new_success = stats.get(t.id, {}).get("success", 0)
            if (t.usage_count or 0) == new_usage and (t.success_count or 0) == new_success:
                continue
            print(
                f"  template {t.id} ({t.name}): "
                f"usage {t.usage_count or 0} -> {new_usage}, "
                f"success {t.success_count or 0} -> {new_success}"
            )
            if not dry_run:
                t.usage_count = new_usage
                t.success_count = new_success
            updates += 1

        if not dry_run and updates:
            db.commit()
            print(f"\n已更新 {updates} 个模板的统计")
        elif dry_run:
            print(f"\n[DRY-RUN] 将更新 {updates} 个模板（未实际写入）")
        else:
            print("\n所有模板统计已是最新，无需更新")

        return {"updates": updates, "templates_total": len(templates), "tasks_aggregated": sum(s["total"] for s in stats.values())}
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="回填 template 使用统计")
    parser.add_argument("--dry-run", action="store_true", help="只预览，不写入")
    args = parser.parse_args()
    result = backfill(dry_run=args.dry_run)
    print(f"\n汇总: {result}")
