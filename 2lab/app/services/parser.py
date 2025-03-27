import requests
from bs4 import BeautifulSoup
import networkx as nx
from urllib.parse import urljoin
from sqlalchemy.orm import Session
import logging
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from app.db.session import SessionLocal
from app.cruds.task import update_task
from app.models.task import Task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_session_with_retries():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


def parse_website_task(task_id: int, url: str, max_depth: int, format: str):
    db = SessionLocal()
    session = create_session_with_retries()
    try:
        logger.info(f"Starting task {task_id} for URL: {url}")
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found")
            raise ValueError(f"Task with ID {task_id} not found")

        # Prevent parsing NASA to avoid rate limits
        if "nasa.gov" in url.lower():
            logger.warning(f"Task {task_id} rejected: NASA URL not allowed")
            update_task(db, task, "failed", 0, "NASA URL is not allowed")
            return {"status": "failed", "message": "NASA URL is not allowed"}

        G = nx.DiGraph()
        visited = set()
        queue = [(url, 0)]

        while queue:
            current_url, depth = queue.pop(0)
            if depth > max_depth or current_url in visited:
                continue

            visited.add(current_url)
            G.add_node(current_url)
            logger.debug(f"Processing URL: {current_url} at depth {depth}")

            try:
                response = session.get(current_url, timeout=5)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                links = soup.find_all("a", href=True)
                total_links = len(links)
                processed_links = 0

                for link in links:
                    absolute_url = urljoin(current_url, link.get("href", ""))
                    if absolute_url.startswith(url):
                        G.add_edge(current_url, absolute_url)
                        if absolute_url not in visited:
                            queue.append((absolute_url, depth + 1))

                    processed_links += 1
                    if total_links > 0:
                        progress = int((processed_links / total_links) * 100)
                        update_task(db, task, "in_progress", progress)
                        logger.debug(f"Progress: {progress}% for task {task_id}")

                time.sleep(1)  # Задержка для предотвращения перегрузки сервера

            except requests.RequestException as e:
                logger.error(f"Request failed for {current_url}: {str(e)}")
                update_task(db, task, "failed", 0, f"Request error: {str(e)}")
                return {"status": "failed", "message": str(e)}

        output_file = f"graph_{task_id}.graphml"
        logger.info(f"Saving graph to {output_file}")
        nx.write_graphml(G, output_file)
        with open(output_file, "r", encoding="utf-8") as f:
            graphml_content = f.read()

        logger.info(f"Task {task_id} completed")
        update_task(db, task, "completed", 100, graphml_content)
        return {"status": "completed", "task_id": task_id, "result": graphml_content}

    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        update_task(db, task, "failed", 0, f"Unexpected error: {str(e)}")
        return {"status": "failed", "message": str(e)}
    finally:
        db.close()
        session.close()
        logger.debug(f"Resources closed for task {task_id}")
