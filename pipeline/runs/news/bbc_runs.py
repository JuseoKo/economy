from pipeline.tasks.news.bbc_rss import BBCNewsRSS

# BBC RSS 실행 스크립트
# - 데이터 수집 → 변환/저장까지 일괄 실행


def run_bbc_news():
    task = BBCNewsRSS()
    fetched, saved = task.run_all()
    print(f"BBC RSS fetched: {fetched}, saved: {saved}")


if __name__ == "__main__":
    run_bbc_news()
