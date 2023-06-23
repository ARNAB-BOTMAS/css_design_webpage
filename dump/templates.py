from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


def create_mail_template(user_id, name, password):
    message = MIMEMultipart()

    mail_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }}
		.container {{
			position: relative;
			max-width: 600px;
			margin: 0 auto;
			padding: 20px;
		}}
        .header {{
            background-color: #f2f2f2;
            text-align: center;
        }}
		.header img{{
			border-radius: 8px;
            text-align: center;
			max-width:1000px;
			width:100%
        }}
        .content {{
            padding: 20px;
        }}
        .banner {{
            display: block;
            margin: 0 auto;
            max-width: 1000px;
			width: 100%
        }}
    </style>
</head>
<body>
	<div class="container">
		<div class="header">
			<img src="https://i.pinimg.com/originals/11/e5/97/11e597d6c6d04d13d6fb975a7b32d1ae.png" alt="Header Image" class="header-image">
		</div>
		<div class="content">
			<p>
				Dear {name}(FaceID: {user_id}, Password: {password}),
			</p>
			<p>
				We are delighted to introduce you to Srishti, our state-of-the-art speech recognition internal system host with advanced technical intelligence. Srishti revolutionizes the way we interact with voice-enabled technologies and brings a new level of efficiency and convenience to various industries.
			</p>
			<p>
				With its cutting-edge artificial intelligence algorithms and robust machine learning capabilities, Srishti provides unparalleled accuracy and performance in speech recognition tasks. It is specifically designed to handle complex voice commands, adapt to different accents and languages, and continually improve its understanding through continuous learning.
			</p>
			<p>
				Key features of Srishti include:
			</p>
			<ul>
				<li>Real-time transcription of spoken language into text</li>
				<li>Seamless integration with existing systems and applications</li>
				<li>Multi-language support, accommodating diverse global user bases</li>
				<li>Customization options to fit specific industry needs</li>
				<li>Advanced security measures to protect sensitive information</li>
			</ul>
			<p>
				Srishti is the ideal solution for organizations seeking to enhance their voice recognition capabilities, streamline workflows, and improve overall operational efficiency. Whether you're in the healthcare sector, customer service industry, or any other field that relies on voice-enabled technologies, Srishti is here to transform the way you interact and communicate.
			</p>
			<p>
				To learn more about Srishti and how it can benefit your organization, please visit our website or contact our team directly. We would be thrilled to provide you with a personalized demonstration and answer any questions you may have.
			</p>
			<p>
				Thank you for your time and consideration.
			</p>
			<p>
				Sincerely,
				<br>
				Team 🤖SRISHTI
			</p>
		</div>
		<div class="header">
			<img src="https://i.pinimg.com/originals/23/6d/f9/236df99eb09521dcceab0d710c26000f.gif" alt="Banner" class="banner">
		</div>
	</div>
</body>
</html>
"""

    message.attach(MIMEText(mail_content, 'html'))

    return message
