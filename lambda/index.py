# lambda/index.py
import json
import urllib.request
import re

def lambda_handler(event, context):
    try:
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])
        
        print("Processing message:", message)
        
        # ユーザーメッセージを追加
        messages = conversation_history.copy()
        messages.append({
            "role": "user",
            "content": message
        })

        prompt_parts = []
        for msg in messages:
            if msg["role"] == "user":
                prompt_parts.append(f"[User]\n{msg['content']}")
            elif msg["role"] == "assistant":
                prompt_parts.append(f"[Assistant]\n{msg['content']}")
        prompt = "Please reply briefly as Assistant.\n\n" + "\n\n".join(prompt_parts)

        request_data = {
            "prompt": prompt,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }

        req = urllib.request.Request(
            url="https://875b-34-125-25-18.ngrok-free.app/generate",
            data=json.dumps(request_data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req) as res:
            res_body = json.loads(res.read().decode('utf-8'))
            print("API response:", res_body)

        assistant_response = res_body.get("generated_text", "").strip()
        assistant_response = re.sub(r'\[(Assistant|User)\]', '', assistant_response)

        # アシスタントの応答を会話履歴に追加
        messages.append({
            "role": "assistant",
            "content": assistant_response
        })

        # 成功レスポンスの返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": messages
            })
        }

    except Exception as error:
        print("Error:", str(error))

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
