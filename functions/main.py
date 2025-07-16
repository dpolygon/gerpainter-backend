# Dependencies for task queue functions.
from google.cloud import tasks_v2
import requests, os, json
from firebase_admin import functions, initialize_app
from firebase_functions import https_fn, options, tasks_fn, params
from firebase_functions.options import RetryConfig, RateLimits, SupportedRegion, set_global_options
import google.auth
from google.auth.transport.requests import AuthorizedSession

# For cost control, you can set the maximum number of containers that can be
# running at the same time. This helps mitigate the impact of unexpected
# traffic spikes by instead downgrading performance. This limit is a per-function
# limit. You can override the limit for each function using the max_instances
# parameter in the decorator, e.g. @https_fn.on_request(max_instances=5).
set_global_options(max_instances=5)

app = initialize_app()

@https_fn.on_request(cors=options.CorsOptions(
    cors_origins="https://gepainter.com",
    cors_methods=["get", "post"]
))
def enqueue_message_task(request: https_fn.Request) -> https_fn.Response:
    try:
        request_json = request.get_json(silent=True)
        if not request_json:
            return "Request body must be valid JSON.", 400

        task_queue = functions.task_queue("sendMessage")
        print("📤 Queue found")

        payload = {"data": {
            "name": request_json.get("name"),
            "phoneNumber": request_json.get("phoneNumber"),
            "address": request_json.get("address"),
            "memo": request_json.get("memo")
        }}
        print("✅ Payload created", payload)

        enqueued_task_name = task_queue.enqueue(payload)
        print("✅ Enqueued task")

        return json.dumps({"message": "Order processing enqueued", "taskName": enqueued_task_name}), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        print(f"Error enqueuing task: {e}")
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}



@tasks_fn.on_task_dispatched(retry_config=RetryConfig(max_attempts=1, min_backoff_seconds=60), rate_limits=RateLimits(max_concurrent_dispatches=10))
def sendMessage(user_data: tasks_fn.CallableRequest) -> str:
        bot_token = os.environ.get('RS_BOT_TOKEN')
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        print("sending to...", url)
        
        user_id = os.environ.get('RS_BOT_ID')
        message = {
            "chat_id": user_id,
            "text": (
                "Name: " + user_data.data['name'] + "\n"
                + "Phone Number: " + user_data.data['phoneNumber'] + "\n"
                + "Address: " + user_data.data['address'] + "\n"
                + "Memo: " + user_data.data['memo']
            )
        }
        
        print("memo says...", message)
        
        response = requests.post(url, data=message)
        print(f"Text Task completed")
        return json.dumps({"status_code": response.status_code})
