from curl_cffi import requests as c_requests

class BaconBypassClient:
    def __init__(self, cf_clearance: str):
        self.cf_clearance = cf_clearance
        self.base_url = "https://baconbypass.xyz/api"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Mobile Safari/537.36 EdgA/153.0.0.0",
            "Origin": "https://baconbypass.xyz",
            "Referer": "https://baconbypass.xyz/",
            "Content-Type": "application/json",
            "Cookie": f"cf_clearance={self.cf_clearance}"
        }

    def run(self, target_url: str, token: str) -> dict:
        try:
            # 第一步：请求 challenge 接口获取 token2
            challenge_res = c_requests.post(
                f"{self.base_url}/token2/challenge",
                json={"token": token},
                headers=self.headers,
                impersonate="chrome",  # 核心：底层伪装 Chrome 指纹，过 Cloudflare
                timeout=15
            )
            
            if challenge_res.status_code != 200:
                return {
                    "status": "error", 
                    "message": f"Challenge 阶段失败 (HTTP {challenge_res.status_code})"
                }
                
            token2 = challenge_res.json().get("data")
            if not token2:
                return {"status": "error", "message": "未从 Challenge 响应中解析到 token2"}

            # 第二步：正式请求 bypass 接口
            bypass_res = c_requests.post(
                f"{self.base_url}/bypass",
                json={"url": target_url, "token2": token2},
                headers=self.headers,
                impersonate="chrome",  # 保持指纹一致
                timeout=15
            )
            
            if bypass_res.status_code != 200:
                return {
                    "status": "error", 
                    "message": f"Bypass 阶段失败 (HTTP {bypass_res.status_code})"
                }
                
            result_url = bypass_res.json().get("result")
            if not result_url:
                return {"status": "error", "message": "Bypass 成功但未返回结果链接", "raw": bypass_res.json()}

            return {
                "status": "success",
                "result": result_url
            }

        except Exception as e:
            return {"status": "error", "message": f"客户端请求异常: {str(e)}"}
