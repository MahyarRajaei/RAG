import logging
import sys

from rq import SimpleWorker, Worker

import config

logger = logging.getLogger("adan.worker")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger.info("Starting RQ worker on queue '%s'...", config.ingestion_queue.name)
    # SimpleWorker is safer on macOS to avoid fork issues with system frameworks; Worker is standard on Linux
    worker_class = SimpleWorker if sys.platform == "darwin" else Worker
    worker = worker_class([config.ingestion_queue], connection=config.redis_conn)
    worker.work(with_scheduler=False)


if __name__ == "__main__":
    main()
