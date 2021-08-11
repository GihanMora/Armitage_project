
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
def send_dump(file_name,file_path):
    print('sending the mail')
    emailfrom = "johnborn9517@gmail.com"
    emailto = ["gihangamage2015@gmail.com", "gihangamage.15@cse.mrt.ac.lk"]
    fileToSend = file_path
    username = "johnborn9517"
    password = "zzrolzjgiedyvyca"

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = ", ".join(emailto)
    msg["Subject"] = "Project Dumps are ready!"
    msg.preamble = "Project Dumps are ready!"

    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)

    if maintype == "text":
        fp = open(fileToSend,encoding='utf-8')
        # Note: we should handle calculating the charset
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()

    elif maintype == "image":
        fp = open(fileToSend, "rb",encoding='utf-8')
        attachment = MIMEImage(fp.read(),encoding='cp437', _subtype=subtype)
        fp.close()

    elif maintype == "audio":
        fp = open(fileToSend, "rb",encoding='utf-8')
        attachment = MIMEAudio(fp.read(),encoding='cp437', _subtype=subtype)
        fp.close()
    else:
        fp = open(fileToSend, "rb")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=file_name)
    msg.attach(attachment)

    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(username,password)
    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()


# send_dump('test',r'C:\Project_files\armitage\armitage_worker\Armitage_project_v1\crawl_n_depth\Simplified_System\end_to_end\dumps\6094f13c09f4bbe84fdec9c0_simplified_dump_with_sources_and_confidence.csv')