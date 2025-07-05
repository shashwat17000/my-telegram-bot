# === अंतिम टेस्टिंग कोड (सिर्फ कनेक्शन चेक करने के लिए) ===

import os
import json
from http.server import BaseHTTPRequestHandler

# Vercel इसी 'handler' क्लास को ढूंढेगा
class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        # रिक्वेस्ट बॉडी से डेटा पढ़ें
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        
        # इसे एक डिक्शनरी में बदलें
        update = json.loads(body.decode('utf-8'))
        
        # चैट आईडी और मैसेज टेक्स्ट निकालें
        try:
            chat_id = update['message']['chat']['id']
            message_text = update['message'].get('text', 'No text')
            
            # जवाब का मैसेज तैयार करें
            response_message = f"मुझे आपका मैसेज मिला: '{message_text}'. कनेक्शन काम कर रहा है!"
            
            # टेलीग्राम को जवाब भेजें
            # (यह हिस्सा हम अभी नहीं जोड़ रहे हैं, सिर्फ कनेक्शन चेक कर रहे हैं)
            
            # Vercel को बताएं कि सब ठीक है
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
            
        except Exception as e:
            # अगर कोई एरर आए, तो उसे लॉग करें
            self.send_response(500)
            self.end_headers()
            # आप चाहें तो एरर भी प्रिंट कर सकते हैं
            # self.wfile.write(str(e).encode())

    def do_GET(self):
        # GET रिक्वेस्ट के लिए एक सीधा-सादा जवाब
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is online and waiting for POST requests from Telegram.")
