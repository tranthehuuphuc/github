import smtplib
import os
import pandas as pd
import re
from email.message import EmailMessage

# ===== Configuration =====
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

CERT_FOLDER = './data/certs-temp'   ######## Change this to certs folder path ########
CSV_FILE = './data/student_list.csv'

# ===== Email Content =====
SUBJECT = '*Lưu ý: Đây là kiểm thử* [LCH-MMT&TT] NETSEC RUN 2025 - Giấy Chứng Nhận Tiêu Chí Thể Lực Tốt - Danh Hiệu Sinh Viên 5 Tốt'
BODY_TEMPLATE = """\
<html>
  <body style="font-family: 'Times New Roman', Georgia, Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #000;">
    <p>Thân gửi bạn,</p>
    <p>Trước tiên, Ban Tổ chức xin gửi lời cảm ơn chân thành đến bạn đã dành thời gian tham gia chương trình <strong>NETSEC RUN 2025</strong>, do <em>Liên Chi hội khoa Mạng máy tính và Truyền thông – Trường Đại học Công nghệ Thông tin, ĐHQG-HCM</em> tổ chức.</p>
    <p>Ban Tổ chức trân trọng ghi nhận bạn là một trong những thí sinh đã hoàn thành mốc chạy được đề ra, và theo đó bạn đã đáp ứng tiêu chí <strong>“Thể lực tốt”</strong> của danh hiệu <strong>“Sinh viên 5 tốt”</strong>. Ban Tổ chức xin gửi đến bạn <strong>Giấy chứng nhận</strong> đính kèm trong email này.</p>
    <p>Bạn vui lòng kiểm tra lại các thông tin trên Giấy chứng nhận. Trong trường hợp có bất kỳ sai sót nào, xin vui lòng phản hồi lại email này để Ban Tổ chức kịp thời điều chỉnh.</p>
    <p>Một lần nữa, xin chân thành cảm ơn bạn đã đồng hành cùng chương trình. Kính chúc bạn một năm học tràn đầy thuận lợi và gặt hái được nhiều thành công.</p>
    <p>Trân trọng,<br/><strong>Ban Tổ chức NETSEC RUN 2025</strong></p>
  </body>
</html>
"""

# ===== Read CSV =====
df = pd.read_csv(CSV_FILE, encoding='utf-8')

# ===== Send email =====
with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
    smtp.starttls()
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    for _, row in df.iterrows():
        student_name = re.sub(r'[^\w\-_. ]', '', row['Họ và tên'].strip()).strip().replace(' ', '_')
        student_email = row['Email'].strip()
        cert_number = row['Số GCN']
        
        cert_filename = f"GCN_{cert_number}_{student_name}.pdf"
        cert_path = os.path.join(CERT_FOLDER, cert_filename)

        msg = EmailMessage()
        msg['Subject'] = SUBJECT
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = student_email
        msg['Cc'] = 'lch-bch-mmttt@suctremmt.com'

        msg.set_content(BODY_TEMPLATE, subtype='html')

        if os.path.isfile(cert_path):
            with open(cert_path, 'rb') as f:
                msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=cert_filename)
        else:
            print(f"❌ Not found: {cert_path}")
            continue

        try:
            smtp.send_message(msg)
            print(f"✅ Sent: {student_name} ({student_email})")
        except Exception as e:
            print(f"❌ Error sending {student_email}: {e}")
