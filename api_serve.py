from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from agent.tools import WebTools
from pools import BrowserPool, CrawlerPool

browser_pool = BrowserPool(pool_size=1)
crawler_pool = CrawlerPool(pool_size=1)
webtool = WebTools(browser_pool, crawler_pool, engine="sougou")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup：可选预热
    await browser_pool._create_browser_instance(headless=True)
    await crawler_pool._get_instance()
    print("✅ Browser pool initialized.")

    yield  # 应用运行中，等待请求

    # shutdown：清理资源
    await browser_pool.cleanup()
    await crawler_pool.cleanup()
    print("✅ Browser pool cleaned up.")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str


@app.post("/search")
async def search(query: QueryRequest):
    input = query.question
    if not isinstance(input, list):
        input = [input]
    results = await webtool.web_search_function(input)
    contents = {}
    for k in results:
        urls = [v["url"] for v in results[k]]
        print(urls)
        contents[k] = await webtool.link_parser_function(urls)
        if contents[k]:
            results[k] = {"search": results[k], "crawl":contents[k]}
    return {"data": results}

if __name__ == "__main__":
    import uvicorn
    port = 8000
    uvicorn.run(app, host="0.0.0.0", port=port, workers=1)
