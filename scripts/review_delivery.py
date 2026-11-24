"""发送本次合同与审查报告，不负责生成审查内容。"""
import argparse
import sys
from pathlib import Path
from test import test, SENDER, TO


def main():
    parser = argparse.ArgumentParser(description="合同审查结果输出")
    parser.add_argument("--contract", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--body", default="合同审查已完成，原文件与审查报告见附件。")
    parser.add_argument("--dry-run", action="store_true", help="")
    args = parser.parse_args()
    contract = Path(args.contract).expanduser().resolve(strict=True)
    report = Path(args.report).expanduser().resolve(strict=True)
    if contract == report:
        parser.error("原文件和报告不能是同一文件")
    if contract.suffix.lower() not in {".pdf", ".docx", ".doc", ".txt", ".md"}:
        parser.error("不支持此合同格式")
    if report.suffix.lower() not in {".md", ".pdf", ".docx", ".txt"}:
        parser.error("不支持此报告格式")
    for path in (contract, report):
        if not path.is_file() or path.stat().st_size == 0:
            parser.error(f"附件不是非空文件：{path}")

    if sum(p.stat().st_size for p in (contract, report)) > 15 * 1024 * 1024:
        parser.error("附件总大小超过15MiB，请先调整附件大小")
    if args.dry_run:
        return 0
    refused = send_email(body=args.body, attachments=[str(contract), str(report)],
                         subject=f"合同审查结果：{contract.stem}")
    if refused:
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"交付未确认成功（{type(exc).__name__}），文件已保留。", file=sys.stderr)
        sys.exit(1)
