from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from admissions_cache import ADMISSIONS_CACHE, BKZS_SECTIONS, BKZS_CONTACT

INSTITUTE_URLS = {
    "主网站": "https://www.sxist.edu.cn/",
    "学院概况": "https://www.sxist.edu.cn/xygk/",
    "光机电工程学院": "https://gjdxy.sxist.edu.cn/",
    "能源工程学院": "https://nyxy.sxist.edu.cn/",
    "智能制造工程学院": "https://znzzxy.sxist.edu.cn/",
    "材料科学与工程学院": "https://clxy.sxist.edu.cn/",
    "大数据与计算机科学学院": "https://dsjxy.sxist.edu.cn/",
    "环境科学与工程学院": "https://hjxy.sxist.edu.cn/",
    "化学工程学院": "https://hgxy.sxist.edu.cn/",
    "设计学院": "https://sjxy.sxist.edu.cn/",
    "经济管理学院": "https://jjglxy.sxist.edu.cn/",
    "文旅康养学院": "https://wlkyxy.sxist.edu.cn/",
    "马克思主义学院": "https://mkszyxy.sxist.edu.cn/",
    "通识教育学院": "https://www.sxist.edu.cn/yxsz/tsjyxy_ggjcjxb_.htm",
}

ADMISSIONS_URL = "http://bkzs.sxist.edu.cn"

KEYWORD_MAP = {
    "光机电": "光机电工程学院",
    "能源": "能源工程学院",
    "智能制造": "智能制造工程学院",
    "材料": "材料科学与工程学院",
    "大数据": "大数据与计算机科学学院",
    "计算机": "大数据与计算机科学学院",
    "环境": "环境科学与工程学院",
    "化学": "化学工程学院",
    "设计": "设计学院",
    "经济管理": "经济管理学院",
    "经管": "经济管理学院",
    "文旅": "文旅康养学院",
    "康养": "文旅康养学院",
    "马克思": "马克思主义学院",
    "思政": "马克思主义学院",
    "通识": "通识教育学院",
    "概况": "学院概况",
    "简介": "学院概况",
    "招生": "主网站",
    "专业": "主网站",
    "章程": "主网站",
    "学校": "主网站",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

SUBLINK_KEYWORDS = [
    "专业设置", "专业介绍", "专业简介", "培养方案", "培养计划",
    "课程设置", "学院简介", "学院介绍", "专业教师", "教学动态",
    "教育教学", "科学研究", "学科建设", "师资队伍", "师资力量",
    "专业方向", "本科专业", "专业详情", "专业列表", "科研项目",
]

TEACHER_KEYWORDS = ["教师", "老师", "师资", "教授", "讲师", "研究", "方向"]

CONTENT_SELECTORS = [
    ".ywc_listR", ".ywc_list",
    ".article_con", ".article", ".article-content",
    ".main_con", ".main-content", ".content",
    "[class*=content]", "[class*=article]",
    ".main", ".container", ".wrapper",
]

MAX_SUB_PAGES = 6
MAX_TEACHER_DETAILS = 20
MAX_TOTAL_CHARS = 15000

def _match_url(query: str) -> str:
    for name, url in INSTITUTE_URLS.items():
        if name in query:
            return url
    for kw, name in KEYWORD_MAP.items():
        if kw in query:
            return INSTITUTE_URLS[name]
    return INSTITUTE_URLS["主网站"]

def _is_admissions_query(query: str) -> bool:
    kw = ["招生", "录取", "分数", "计划", "简章", "历年", "志愿", "批次"]
    return any(k in query for k in kw)

def _is_teacher_query(query: str) -> bool:
    return any(k in query for k in TEACHER_KEYWORDS)

def _fetch_soup(url: str):
    try:
        resp = requests.get(url, timeout=15, headers=HEADERS)
        resp.encoding = resp.apparent_encoding or "utf-8"
    except Exception:
        return None
    return BeautifulSoup(resp.text, "html.parser")

def _extract_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "img", "input", "textarea"]):
        tag.decompose()

    for sel in CONTENT_SELECTORS:
        el = soup.select_one(sel)
        if el and len(el.get_text(strip=True)) > 50:
            for nav in el.find_all(["nav", "footer", "header"]):
                nav.decompose()
            return el.get_text(separator="\n", strip=True)

    if soup.body:
        for nav in soup.body.find_all(["nav", "footer", "header"]):
            nav.decompose()
        return soup.body.get_text(separator="\n", strip=True)
    return ""

def _discover_sub_links(soup: BeautifulSoup, base_url: str) -> list:
    results = []
    seen = set()
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = a["href"].strip()
        if not text or not href or text in seen:
            continue
        seen.add(text)
        if any(kw in text for kw in SUBLINK_KEYWORDS):
            full_url = urljoin(base_url, href)
            if full_url not in {r[1] for r in results}:
                results.append((text, full_url))
    return results[:MAX_SUB_PAGES]

def _discover_teacher_links(soup: BeautifulSoup, base_url: str) -> list:
    results = []
    seen_text = set()
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = a["href"].strip()
        if not text or not href or text in seen_text:
            continue
        is_info = "/info/" in href
        if not is_info:
            continue
        is_teacher_text = any(k in text for k in ["教师", "讲师", "教授", "博士", "硕士", "研究"])
        is_chinese_name = 2 <= len(text) <= 4 and all('\u4e00' <= c <= '\u9fff' for c in text.replace('·', '').replace(' ', ''))
        if not (is_teacher_text or is_chinese_name):
            continue
        if text in ("首页", "学校首页", "本站首页", "加为收藏", "通知公告", "更多", ""):
            continue
        full_url = urljoin(base_url, href)
        if full_url.startswith(base_url):
            seen_text.add(text)
            results.append((text, full_url))
    return results[:MAX_TEACHER_DETAILS]

def _fetch_admissions_content(query: str) -> str:
    parts = []

    # 第1层：bkzs 首页全文提取
    soup = _fetch_soup(ADMISSIONS_URL)
    if soup:
        parts.append(f"【来源】{ADMISSIONS_URL}（本科招生网首页）")
        homepage_text = _extract_text(soup)
        if homepage_text:
            parts.append(homepage_text[:1500])

    # 第2层：主站 www.sxist.edu.cn 上的招生相关文章
    main_soup = _fetch_soup(INSTITUTE_URLS["主网站"])
    if main_soup:
        found_articles = []
        for a in main_soup.find_all("a", href=True):
            t = a.get_text(strip=True)
            h = a["href"].strip()
            if not t or not h or len(t) < 8:
                continue
            if any(k in t for k in ["招生", "录取", "分数", "计划", "简章", "章程"]):
                full_url = urljoin("https://www.sxist.edu.cn", h)
                if "/info/" in full_url:
                    found_articles.append((t, full_url))

        if found_articles:
            parts.append("\n--- 主站招生相关文章 ---")
            articles_collected = 0
            for title, art_url in found_articles:
                if articles_collected >= 3:
                    break
                art_soup = _fetch_soup(art_url)
                if not art_soup:
                    continue
                content = _extract_text(art_soup)
                if content and len(content) > 80:
                    parts.append(f"\n【{title}】")
                    parts.append(content[:1500])
                    articles_collected += 1

    # 第3层：预抓取缓存数据 —— bkzs子页面为JS SPA，requests无法获取，此处为预渲染数据
    matched_cache_keys = []
    for key in ADMISSIONS_CACHE:
        if any(kw in query for kw in ["章程", "规则"]) and "章程" in key:
            matched_cache_keys.append(key)
        elif any(kw in query for kw in ["简章"]) and "简章" in key:
            matched_cache_keys.append(key)
        elif any(kw in query for kw in ["计划"]) and "计划" in key:
            matched_cache_keys.append(key)
        elif any(kw in query for kw in ["政策"]) and "政策" in key and "章程" not in key:
            matched_cache_keys.append(key)
        elif any(kw in query for kw in ["历年", "分数", "平均分", "录取分"]) and ("历年" in key or "录取分数" in key):
            matched_cache_keys.append(key)
        elif any(kw in query for kw in ["专业", "介绍"]) and "专业" in key and "分数" not in key:
            matched_cache_keys.append(key)

    # 省份精确匹配
    provinces = ["山东", "山西", "河南", "河北", "江苏", "浙江", "广东", "安徽", "湖北",
                 "湖南", "四川", "陕西", "甘肃", "辽宁", "吉林", "黑龙江", "江西", "福建",
                 "海南", "新疆", "天津", "北京", "上海", "重庆"]
    for province in provinces:
        if province in query:
            for key in ADMISSIONS_CACHE:
                if province in key and "录取分数" in key:
                    matched_cache_keys.append(key)

    matched_cache_keys = list(dict.fromkeys(matched_cache_keys))[:5]

    if matched_cache_keys:
        parts.append("\n--- 招生网缓存数据 ---")
        for key in matched_cache_keys:
            parts.append(f"\n【{key}】")
            parts.append(ADMISSIONS_CACHE[key][:2000])

    # 第4层：联系信息
    parts.append(f"\n--- 招生办联系方式 ---\n"
                 f"电话：{BKZS_CONTACT['电话']}\n"
                 f"邮箱：{BKZS_CONTACT['邮箱']}\n"
                 f"地址：{BKZS_CONTACT['地址']}\n"
                 f"招生网址：{BKZS_CONTACT['网址']}")

    result = "\n".join(parts)
    return result if len(result) > 100 else ""

def _fetch_web_content(query: str) -> str:
    results = []

    # 学院站爬取
    url = _match_url(query)
    soup = _fetch_soup(url)
    if soup is None:
        results.append(f"请求失败，无法访问 {url}")
    else:
        results.append(f"【来源】{url}")
        home_text = _extract_text(soup)
        if home_text:
            results.append(home_text)

        # 发现并爬取子页面
        sub_links = _discover_sub_links(soup, url)
        for text, sub_url in sub_links:
            sub_soup = _fetch_soup(sub_url)
            if not sub_soup:
                continue
            content = _extract_text(sub_soup)
            if content and len(content) > 50:
                results.append(f"\n--- {text} ---")
                results.append(content[:1500])
            if len("\n".join(results)) > MAX_TOTAL_CHARS // 2:
                break

        # 教师深度爬取
        if _is_teacher_query(query) or any(k in query for k in ["老师", "研究"]):
            teacher_page_url = urljoin(url, "jyjx/zyjs.htm")
            teacher_soup = _fetch_soup(teacher_page_url)
            if teacher_soup:
                teacher_links = _discover_teacher_links(teacher_soup, url)
                results.append(f"\n--- 师资力量（共{len(teacher_links)}位教师）---")
                for tname, turl in teacher_links[:MAX_TEACHER_DETAILS]:
                    t_soup = _fetch_soup(turl)
                    if not t_soup:
                        continue
                    t_content = _extract_text(t_soup)
                    if t_content and len(t_content) > 40:
                        # 限制每位教师内容长度
                        detail = t_content[:600]
                        results.append(f"【{tname}】{detail}")
                    if len("\n".join(results)) > MAX_TOTAL_CHARS:
                        break

    # 招生站爬取
    if _is_admissions_query(query):
        admissions_content = _fetch_admissions_content(query)
        if admissions_content:
            results.append("\n\n" + admissions_content)

    result = "\n".join(results)
    if len(result) > MAX_TOTAL_CHARS:
        result = result[:MAX_TOTAL_CHARS] + "\n...(内容已截断)..."
    return result if len(result) > 50 else "未获取到有效内容"

@tool("search_institute_message",
      description="""
      **工具定义**
      根据用户查询的关键词，自动匹配山西科技学院官网、各二级学院官网及本科招生网，
      抓取首页并自动发现"专业设置""学院简介""专业教师""培养方案""招生计划""历年招生"
      等子页面供智能体分析总结。

      **查询范围**
      主网站、13个二级学院官网、本科招生网 (bkzs.sxist.edu.cn)

      **使用方式**
      传入用户的完整问题（如"大数据与计算机科学学院有哪些专业？"
      "山西科技学院2025年在山东省的招生计划？"等），工具会自动匹配网站
      并抓取相关内容。

      **输出要求**
      完全根据获取到的网页事实内容回答，禁止胡编乱造。
      """)
def tool_sim(query: str) -> str:
    return _fetch_web_content(query)
