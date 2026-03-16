from typing import Optional
import logging

from app.core.config import settings
from app.models.user import NotificationPreference

logger = logging.getLogger(__name__)


class NotificationService:
    @classmethod
    async def send_subscription_notification(
        cls,
        email: str,
        phone: Optional[str],
        preference: NotificationPreference,
        fund_name: str,
        amount: float,
        transaction_id: str
    ) -> tuple[bool, Optional[str]]:
        notification_sent = False
        notification_type = None
        
        message = (
            f"¡Felicitaciones! Se ha suscrito exitosamente al fondo {fund_name} "
            f"por un monto de COP ${amount:,.2f}. "
            f"ID de transacción: {transaction_id}"
        )
        
        if preference in [NotificationPreference.EMAIL, NotificationPreference.BOTH]:
            sent = await cls._send_email(email, "Suscripción Exitosa - BTG Pactual", message)
            if sent:
                notification_sent = True
                notification_type = "email"
        
        if preference in [NotificationPreference.SMS, NotificationPreference.BOTH] and phone:
            sent = await cls._send_sms(phone, message)
            if sent:
                notification_sent = True
                notification_type = "sms" if notification_type is None else "both"
        
        return notification_sent, notification_type
    
    @classmethod
    async def send_cancellation_notification(
        cls,
        email: str,
        phone: Optional[str],
        preference: NotificationPreference,
        fund_name: str,
        amount: float,
        transaction_id: str
    ) -> tuple[bool, Optional[str]]:
        notification_sent = False
        notification_type = None
        
        message = (
            f"Su suscripción al fondo {fund_name} ha sido cancelada. "
            f"Se ha devuelto COP ${amount:,.2f} a su saldo. "
            f"ID de transacción: {transaction_id}"
        )
        
        if preference in [NotificationPreference.EMAIL, NotificationPreference.BOTH]:
            sent = await cls._send_email(email, "Cancelación de Suscripción - BTG Pactual", message)
            if sent:
                notification_sent = True
                notification_type = "email"
        
        if preference in [NotificationPreference.SMS, NotificationPreference.BOTH] and phone:
            sent = await cls._send_sms(phone, message)
            if sent:
                notification_sent = True
                notification_type = "sms" if notification_type is None else "both"
        
        return notification_sent, notification_type
    
    @classmethod
    async def _send_email(cls, to_email: str, subject: str, body: str) -> bool:
        if not settings.NOTIFICATION_EMAIL_ENABLED:
            logger.info(f"[EMAIL DISABLED] To: {to_email}, Subject: {subject}")
            return False
        
        # En desarrollo, simulamos el envío
        logger.info(f"[EMAIL SENT] To: {to_email}, Subject: {subject}, Body: {body[:100]}...")
        
        # TODO: Integración con AWS SES para producción
        # import boto3
        # ses_client = boto3.client('ses', region_name=settings.AWS_REGION)
        # response = ses_client.send_email(
        #     Source=settings.AWS_SES_SENDER_EMAIL,
        #     Destination={'ToAddresses': [to_email]},
        #     Message={
        #         'Subject': {'Data': subject},
        #         'Body': {'Text': {'Data': body}}
        #     }
        # )
        
        return True
    
    @classmethod
    async def _send_sms(cls, phone_number: str, message: str) -> bool:
        if not settings.NOTIFICATION_SMS_ENABLED:
            logger.info(f"[SMS DISABLED] To: {phone_number}")
            return False
        
        # En desarrollo, simulamos el envío
        logger.info(f"[SMS SENT] To: {phone_number}, Message: {message[:50]}...")
        
        # TODO: Integración con AWS SNS para producción
        # import boto3
        # sns_client = boto3.client('sns', region_name=settings.AWS_REGION)
        # response = sns_client.publish(
        #     PhoneNumber=phone_number,
        #     Message=message
        # )
        
        return True
