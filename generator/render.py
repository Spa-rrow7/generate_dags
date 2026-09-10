"""Рендер DagSpec в текст DAG-файла через Jinja2."""

from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .parsers import DagSpec

TEMPLATES_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    undefined=StrictUndefined,
    trim_blocks=False,
    lstrip_blocks=False,
    keep_trailing_newline=True,
)


def render(template_name: str, **ctx) -> str:
    tpl = _env.get_template(template_name)
    return tpl.render(**ctx)


def render_dag(spec: DagSpec, source_rel: str) -> str:
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    parts: list[str] = [
        render(
            "dag_header.py.j2",
            name=spec.name,
            description=spec.description,
            schedule=spec.schedule,
            start_time=spec.start_time,
            tags=["generated", spec.kind],
            source_rel=source_rel,
            generated_at=generated_at,
        ),
        "\n",
    ]

    for t in spec.tasks:
        var = f"t_{t['id']}"
        if spec.kind == "python":
            parts.append(render(
                "python_task.py.j2",
                task_var=var,
                task_id=t["id"],
                module=spec.module,
                func=t["func"],
                conn_id=spec.conn_id,
            ))
        elif spec.kind == "sql":
            parts.append(render(
                "sql_task.py.j2",
                task_var=var,
                task_id=t["id"],
                conn_id=spec.conn_id,
                sql=t["sql"],
            ))
        else:
            raise ValueError(f"Unknown spec.kind: {spec.kind}")
        parts.append("\n")

    for child_id, parent_ids in spec.depends_on.items():
        for parent_id in parent_ids:
            parts.append(render(
                "dependency.py.j2",
                child_var=f"t_{child_id}",
                parent_var=f"t_{parent_id}",
            ))
            parts.append("\n")

    return "".join(parts)