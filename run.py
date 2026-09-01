"""Multi-Agent ITS — 基于CrewAI的多智能体交互教学系统"""
import uvicorn
from config.settings import API_HOST, API_PORT

if __name__ == "__main__":
    print(f"Starting Multi-Agent ITS (CrewAI) on http://{API_HOST}:{API_PORT}")
    uvicorn.run("api.server:app", host=API_HOST, port=API_PORT, reload=False)
