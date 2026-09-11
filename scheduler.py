import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from main import main


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | %(message)s"
    ),
)


def run_job() -> None:
    logging.info("開始檢查 DevForum 公告")

    try:
        main()
    except Exception:
        logging.exception("檢查公告時發生錯誤")
    else:
        logging.info("本次檢查完成")


def start_scheduler() -> None:
    scheduler = BlockingScheduler(
        timezone="Asia/Taipei"
    )

    scheduler.add_job(
        run_job,
        trigger="cron",
        minute=15,
        id="check_devforum",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )

    # 啟動時先檢查一次，不必等到下一個整點
    run_job()

    logging.info(
        "排程已啟動，將於每小時第 15 分檢查"
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("排程已停止")


if __name__ == "__main__":
    start_scheduler()