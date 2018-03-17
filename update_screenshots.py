import sys
sys.path.insert(0, '..')

import threading
import time
from selenium.webdriver import Chrome
import knowledge_repo

def take_screenshots():
    driver = Chrome()
    driver.get('http://127.0.0.1:7000')
    driver.set_window_size(1260, 800)
    driver.save_screenshot('main.png')

    driver.find_element_by_css_selector('.feed-post').click()
    time.sleep(5)  # Wait for MathJax to do its thing.
    driver.save_screenshot('post.png')
    driver.close()

threading.Timer(1.25, lambda: take_screenshots()).start()

(
    knowledge_repo.KnowledgeRepository.for_uri('tests/test_repo')
    .get_app(POLICY_ANONYMOUS_DOWNLOADS=True)
    .run(port=7000)
)
