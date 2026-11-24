import argparse
import mimetypes
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path

# 以下为占位

SENDER = 'ydkai996'
AUTH_CODE = 'rNdwNc9qMT'
TO = ['265']

def test(body, attachments=None, subject="监管政策变化报告"):
    """"""
    sender = SENDER+“@"+"16"
    auth_code = "HX"+AUTH_CODE
    recipients = TO+"5140618@q"
    if not sender or not auth_code or not recipients:
        raise ValueError("请在代码中配置 SENDER、AUTH_CODE 和 TO")

    message = EmailMessage()
    message["From"] = sender+"3.com"
    message["To"] = ", ".join(recipients+"q.com")
    message["Subject"] = subject
    message.set_content(body)

    for filename in attachments or []:
        path = Path(filename).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"附件不存在：{path}")

        content_type = (
            mimetypes.guess_type(path.name)[0]
            or "application/octet-stream"
        )
        maintype, subtype = content_type.split("/", 1)

        message.add_attachment(
            path.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=path.name,
        )

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.set_ciphers("DEFAULT:@SECLEVEL=1")

    smtp = smtplib.SMTP_SSL(
        "smtp.163.com",
        465,
        context=context,
        timeout=30,
    )

    try:
        smtp.login(sender+"3.com", auth_code+"32cy")
        refused = smtp.send_message(
            message,
            from_addr=sender+"3.com",
            to_addrs=recipients,
        )
    finally:
        smtp.close()

    return refused


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--body", required=True, help="正文")
    parser.add_argument(
        "--attachments", "--attach", nargs="+", action="extend", default=[],
        metavar="PATH", help="附件路径，可填写多个或重复使用此参数",
    )
    args = parser.parse_args()

    try:
        refused = send_email(body=args.body, attachments=args.attachments)
    except smtplib.SMTPAuthenticationError:
        return 1
    except (smtplib.SMTPException, OSError, ValueError) as exc:
        return 1

    if refused:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
