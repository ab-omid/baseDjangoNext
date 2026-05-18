from typing import List, Optional, Union
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Cc, Bcc, Content

from app.config.sendgrid import SendGridConfig
from app.utils.log_util import LogUtil


class SendGridProvider:
    """
    This class provides an interface to the SendGrid API for sending emails.
    """

    def __init__(self):
        self._client: Optional[SendGridAPIClient] = None

    def client(self) -> SendGridAPIClient:
        """Get the existing SendGrid client or create a new one if it does not exist.

        Returns:
            SendGridAPIClient: The SendGrid API client.
        """
        if self._client is None:
            try:
                self._client = SendGridAPIClient(api_key=SendGridConfig.API_KEY)
            except Exception as e:
                logger = LogUtil.get_logger()
                logger.error(
                    "Exception in SendGridProvider.client(): %s", e, extra={"code": 2909}
                )
        return self._client

    def send_email(
        self,
        subject: str,
        body: str,
        to: Union[str, List[str]],
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        html_content: Optional[str] = None
    ) -> bool:
        """
        Send an email using SendGrid API.

        Args:
            subject (str): The subject of the email.
            body (str): The plain text body of the email.
            to (Union[str, List[str]]): Email address(es) to send to.
            from_email (Optional[str]): The sender's email address. Defaults to configured default.
            from_name (Optional[str]): The sender's name. Defaults to configured default.
            cc (Optional[Union[str, List[str]]]): CC email address(es).
            bcc (Optional[Union[str, List[str]]]): BCC email address(es).
            html_content (Optional[str]): HTML content of the email.

        Returns:
            bool: True if email was sent successfully, False otherwise.

        Raises:
            Exception: If there is an error sending the email.
        """
        logger = LogUtil.get_logger()
        
        try:
            # Use default values if not provided
            from_email = from_email or SendGridConfig.DEFAULT_FROM_EMAIL
            from_name = from_name or SendGridConfig.DEFAULT_FROM_NAME

            # Convert single email to list for consistency
            if isinstance(to, str):
                to = [to]
            if isinstance(cc, str):
                cc = [cc]
            if isinstance(bcc, str):
                bcc = [bcc]

            # Create the mail object
            mail = Mail(
                from_email=Email(from_email, from_name),
                to_emails=[To(email) for email in to],
                subject=subject,
                plain_text_content=body
            )

            # Add HTML content if provided
            if html_content:
                mail.add_content(Content("text/html", html_content))

            # Add CC recipients
            if cc:
                for email in cc:
                    mail.add_cc(Cc(email))

            # Add BCC recipients
            if bcc:
                for email in bcc:
                    mail.add_bcc(Bcc(email))

            # Send the email
            client = self.client()
            response = client.send(mail)

            if response.status_code in [200, 201, 202]:
                logger.info(
                    "Email sent successfully",
                    extra={
                        "code": 10885,
                        "to": to,
                        "subject": subject,
                        "status_code": response.status_code
                    }
                )
                return True
            else:
                logger.error(
                    "Failed to send email",
                    extra={
                        "code": 11985,
                        "to": to,
                        "subject": subject,
                        "status_code": response.status_code,
                        "response_body": response.body
                    }
                )
                return False

        except Exception as e:
            logger.error(
                "Exception in SendGridProvider.send_email(): %s",
                e,
                extra={
                    "code": 13385,
                    "to": to,
                    "subject": subject
                }
            )
            raise Exception(f"Failed to send email: {str(e)}")
