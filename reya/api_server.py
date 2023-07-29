import json
import uvicorn
from fastapi import FastAPI, status, Body, BackgroundTasks
from utils.logger import MyLogging

from control_proc import ReYaControl

logger = MyLogging("APILog", file="../logs/api.log")
app = FastAPI()


# 新的热压计划
@app.post("/reya/newTaskPlan", status_code=status.HTTP_200_OK)
async def new_task(data: dict, background_tasks: BackgroundTasks):
    try:
        request_log = json.dumps(data)
        logger.info(request_log)
        plan_id = data.get("production_plan")
        background_tasks.add_task(ReYaControl().plan, plan_id)
        return {"message": "Notification sent in the background"}
    except Exception as e:
        logger.error(f"srm_task_clear:{data}, error:{str(e)}")
        return {"code": 500, "msg": f"接口异常{str(e)}"}


@app.post("/reya/test", status_code=status.HTTP_200_OK)
async def new_task(data: dict):
    try:
        request_log = json.dumps(data)
        logger.info(request_log)
        plan_id = data.get("production_plan")
        print(plan_id)
        ReYaControl().plan(plan_id)
        # background_tasks.add_task(ReYaControl().plan, plan_id)
        return {"message": "Notification sent in the background"}
    except Exception as e:
        logger.error(f"srm_task_clear:{data}, error:{str(e)}")
        return {"code": 500, "msg": f"接口异常{str(e)}"}


@app.post("/reya/device_control", status_code=status.HTTP_200_OK)
async def device_control(data: dict):
    try:
        request_log = json.dumps(data)
        logger.info(request_log)
        device_name = data.get("device_name")
        value = data.get('value')
        print(plan_id)
        ReYaControl().plan(plan_id)
        # background_tasks.add_task(ReYaControl().plan, plan_id)
        return {"message": "Notification sent in the background"}
    except Exception as e:
        logger.error(f"srm_task_clear:{data}, error:{str(e)}")
        return {"code": 500, "msg": f"接口异常{str(e)}"}


if __name__ == '__main__':
    uvicorn.run(app='api_server:app', host="127.0.0.1", port=8000, reload=True)
