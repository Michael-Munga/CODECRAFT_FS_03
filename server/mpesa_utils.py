import requests
import base64
import json
import os
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import uuid

class MpesaService:
    def __init__(self):
        self.consumer_key = os.getenv("MPESA_CONSUMER_KEY")
        self.consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")
        self.business_shortcode = os.getenv("MPESA_BUSINESS_SHORTCODE")
        self.passkey = os.getenv("MPESA_PASSKEY")
        self.callback_url = os.getenv("MPESA_CALLBACK_URL")
        self.base_url = "https://sandbox.safaricom.co.ke" if os.getenv("MPESA_ENVIRONMENT") == "sandbox" else "https://api.safaricom.co.ke"
        
    def get_access_token(self):
        """Generate access token for M-Pesa API calls"""
        try:
            auth_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            credentials = f"{self.consumer_key}:{self.consumer_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(auth_url, headers=headers)
            response.raise_for_status()
            return response.json()["access_token"]
        except Exception as e:
            print(f"Error getting access token: {str(e)}")
            return None
    
    def generate_password(self):
        """Generate password for STK push"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        data_to_encode = f"{self.business_shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(data_to_encode.encode()).decode(), timestamp
    
    def initiate_stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate M-Pesa STK Push"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {"error": "Failed to get access token"}
            
            password, timestamp = self.generate_password()
            
            stk_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone_number,
                "PartyB": self.business_shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": self.callback_url,
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }
            
            response = requests.post(stk_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error initiating STK push: {str(e)}")
            return {"error": str(e)}
    
    def verify_transaction(self, checkout_request_id):
        """Verify transaction status"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {"error": "Failed to get access token"}
            
            password, timestamp = self.generate_password()
            
            query_url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            response = requests.post(query_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error verifying transaction: {str(e)}")
            return {"error": str(e)}

# Global instance
mpesa_service = MpesaService()