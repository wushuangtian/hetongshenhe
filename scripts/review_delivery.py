"""发送本次合同与审查报告，不负责生成审查内容。"""
import argparse
import sys
from pathlib import Path
from send_email import send_email, SENDER, TO


def main():
    parser = argparse.ArgumentParser(description="合同审查后，将结果和原合同发到用户邮箱")
    parser.add_argument("--contract", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--body", default="合同审查已完成，原合同与审查报告见附件。")
    parser.add_argument("--dry-run", action="store_true", help="仅验证，不发送")
    args = parser.parse_args()
    contract = Path(args.contract).expanduser().resolve(strict=True)
    report = Path(args.report).expanduser().resolve(strict=True)
    if contract == report:
        parser.error("原合同和报告不能是同一文件")
    if contract.suffix.lower() not in {".pdf", ".docx", ".doc", ".txt", ".md"}:
        parser.error("不支持此合同格式")
    if report.suffix.lower() not in {".md", ".pdf", ".docx", ".txt"}:
        parser.error("不支持此报告格式")
    for path in (contract, report):
        if not path.is_file() or path.stat().st_size == 0:
            parser.error(f"附件不是非空文件：{path}")
    # 为 MIME 编码及不同邮箱限制预留空间。
    if sum(p.stat().st_size for p in (contract, report)) > 15 * 1024 * 1024:
        parser.error("附件总大小超过15MiB，请先调整附件大小")
    if args.dry_run:
        print(f"发件人：{SENDER}；收件人：{', '.join(TO)}")
        print(f"原合同：{contract.name}；报告：{report.name}")
        print("检查通过，未发送。")
        return 0
    refused = send_email(body=args.body, attachments=[str(contract), str(report)],
                         subject=f"合同审查结果：{contract.stem}")
    if refused:
        print("部分收件人被拒绝，请检查投递结果，不自动重发。")
        return 2
    print("SMTP服务器已接受邮件，请关注收件箱或退信。")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"交付未确认成功（{type(exc).__name__}），文件已保留。请检查收件箱，不自动重发。", file=sys.stderr)
        sys.exit(1)
