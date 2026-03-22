#!/usr/bin/env python3
"""
网站文件爬取工具
能够爬取目标网站的所有可访问文件（HTML、CSS、JS、图片、文档等）
这个工具是开源的，要如何使用它都与开发者无关，毕竟这很简单
"""

import os
import sys
import time
import re
import urllib.parse
import urllib.robotparser
from pathlib import Path
from typing import Set, List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
import tqdm

# 全局配置
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 可下载文件扩展名（包含400+种文件类型，可自行拓展）
DOWNLOADABLE_EXTENSIONS = {
    # 图片格式（30+种）
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp', '.tiff', '.tif',
    '.psd', '.ai', '.eps', '.raw', '.cr2', '.nef', '.orf', '.sr2', '.heic', '.heif',
    '.avif', '.jxl', '.jp2', '.j2k', '.pbm', '.pgm', '.ppm', '.pnm', '.hdr', '.exr',
    
    # 文档格式（50+种）
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf',
    '.odt', '.ods', '.odp', '.odg', '.odf', '.md', '.markdown', '.tex', '.latex',
    '.csv', '.tsv', '.xml', '.yaml', '.yml', '.json', '.ini', '.cfg', '.conf',
    '.log', '.sql', '.db', '.sqlite', '.sqlite3', '.mdb', '.accdb', '.dbf',
    '.epub', '.mobi', '.azw', '.azw3', '.fb2', '.ibooks', '.chm', '.djvu',
    '.pages', '.numbers', '.key', '.vsd', '.vsdx', '.vsdm', '.vsdx',
    
    # 压缩文件格式（20+种）
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.lz', '.lzma',
    '.lzo', '.z', '.lzh', '.arj', '.cab', '.iso', '.img', '.dmg', '.vhd',
    '.vmdk', '.vhdx', '.wim', '.swm',
    
    # 媒体文件格式（50+种）
    '.mp3', '.mp4', '.avi', '.mkv', '.mov', '.wav', '.flac', '.aac', '.ogg',
    '.oga', '.opus', '.m4a', '.m4b', '.wma', '.alac', '.aiff', '.au', '.voc',
    '.ra', '.rm', '.ram', '.mid', '.midi', '.mod', '.xm', '.it', '.s3m',
    '.mpg', '.mpeg', '.wmv', '.flv', '.swf', '.webm', '.3gp', '.3g2', '.m2ts',
    '.mts', '.ts', '.mxf', '.ogv', '.divx', '.xvid', '.vob', '.asf', '.dv',
    '.f4v', '.m4v', '.mpv', '.nsv', '.roq', '.yuv',
    
    # 代码文件格式（100+种）
    '.js', '.css', '.html', '.htm', '.xhtml', '.php', '.py', '.java', '.cpp',
    '.c', '.h', '.hpp', '.cs', '.vb', '.swift', '.go', '.rs', '.rb', '.pl',
    '.pm', '.t', '.lua', '.scala', '.kt', '.kts', '.groovy', '.dart', '.elm',
    '.erl', '.ex', '.exs', '.fs', '.fsharp', '.hs', '.lhs', '.jl', '.clj',
    '.cljs', '.cljc', '.edn', '.r', '.m', '.matlab', '.f', '.for', '.f90',
    '.ada', '.asm', '.s', '.inc', '.pas', '.pp', '.lpr', '.d', '.coffee',
    '.litcoffee', '.iced', '.ts', '.tsx', '.jsx', '.vue', '.svelte', '.elm',
    '.pug', '.jade', '.haml', '.slim', '.scss', '.sass', '.less', '.styl',
    '.stylus', '.wasm', '.wat', '.bf', '.bfs', '.bas', '.vbs', '.bat', '.cmd',
    '.ps1', '.sh', '.bash', '.zsh', '.fish', '.csh', '.ksh', '.tcsh', '.awk',
    '.sed', '.tcl', '.tk', '.expect', '.nim', '.zig', '.v', '.vhdl', '.sv',
    '.svh', '.uc', '.txx', '.cxx', '.cc', '.hh', '.hxx', '.ixx', '.mxx',
    '.inl', '.ipp',
    
    # 字体文件格式（10+种）
    '.ttf', '.otf', '.woff', '.woff2', '.eot', '.fon', '.fnt', '.pfa', '.pfb',
    '.sfd', '.dfont',
    
    # 数据库文件格式（10+种）
    '.db', '.sqlite', '.sqlite3', '.mdb', '.accdb', '.fdb', '.mdf', '.ldf',
    '.ndf', '.dbf',
    
    # 可执行文件格式（20+种）
    '.exe', '.msi', '.dll', '.so', '.dylib', '.bundle', '.sys', '.drv',
    '.ocx', '.cab', '.apk', '.ipa', '.app', '.appx', '.appxbundle', '.msix',
    '.msixbundle', '.deb', '.rpm', '.pkg', '.run',
    
    # 配置文件格式（20+种）
    '.ini', '.cfg', '.conf', '.config', '.properties', '.toml', '.xml',
    '.yaml', '.yml', '.json', '.json5', '.hjson', '.edn', '.env', '.dotenv',
    '.gitignore', '.dockerignore', '.npmignore', '.editorconfig',
    
    # 其他格式（30+种）
    '.torrent', '.magnet', '.webloc', '.url', '.lnk', '.desktop', '.appref-ms',
    '.scr', '.com', '.pif', '.bat', '.cmd', '.vbs', '.wsf', '.ps1', '.psm1',
    '.psd1', '.psc1', '.reg', '.inf', '.cat', '.cer', '.crt', '.der', '.p7b',
    '.p7c', '.p12', '.pfx', '.pem', '.key',
}

class WebCrawler:
    def __init__(self, 
                 base_url: str, 
                 output_dir: str = "downloads",
                 max_depth: int = 10,  # 默认深度10
                 max_workers: int = 10,  # 默认并发10
                 delay: float = 0.3,  # 默认延迟0.3秒
                 respect_robots: bool = True,
                 crawl_strategy: str = "breadth_first",  # 爬取策略：breadth_first 或 depth_first
                 follow_redirects: bool = True,  # 是否跟踪重定向
                 parse_css_files: bool = True,  # 是否解析CSS文件中的链接
                 parse_js_files: bool = True,  # 是否解析JS文件中的链接
                 max_urls: int = 10000,  # 最大爬取URL数量限制
                 timeout: int = 30):  # 请求超时时间
        """
        初始化爬虫
        
        Args:
            base_url: 起始URL
            output_dir: 下载文件保存目录
            max_depth: 最大爬取深度（默认10）
            max_workers: 最大并发线程数（默认10）
            delay: 请求延迟（秒）（默认0.3）
            respect_robots: 是否遵守robots.txt
            crawl_strategy: 爬取策略，'breadth_first'（广度优先）或 'depth_first'（深度优先）
            follow_redirects: 是否跟踪重定向
            parse_css_files: 是否解析CSS文件中的链接
            parse_js_files: 是否解析JS文件中的链接
            max_urls: 最大爬取URL数量限制（防止无限循环）
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.base_domain = urllib.parse.urlparse(base_url).netloc
        self.output_dir = Path(output_dir)
        self.max_depth = max_depth
        self.max_workers = max_workers
        self.delay = delay
        self.respect_robots = respect_robots
        self.crawl_strategy = crawl_strategy
        self.follow_redirects = follow_redirects
        self.parse_css_files = parse_css_files
        self.parse_js_files = parse_js_files
        self.max_urls = max_urls
        self.timeout = timeout
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 已访问URL集合
        self.visited_urls: Set[str] = set()
        # 待爬取URL队列（URL, 深度）
        self.url_queue: List[Tuple[str, int]] = [(self.base_url, 0)]
        # robots.txt解析器
        self.robot_parser = urllib.robotparser.RobotFileParser()
        
        # 统计信息
        self.stats = {
            'pages_crawled': 0,
            'files_downloaded': 0,
            'total_size': 0,
            'errors': 0,
            'css_files_parsed': 0,
            'js_files_parsed': 0,
            'redirects_followed': 0
        }
        
        # 初始化session
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.session.max_redirects = 10 if follow_redirects else 0
        
        # URL优先级队列（用于深度优先）
        self.priority_queue = []
        
        # 加载robots.txt
        if self.respect_robots:
            self._load_robots_txt()
    
    def _load_robots_txt(self):
        """加载并解析robots.txt"""
        try:
            robots_url = f"{self.base_url}/robots.txt"
            self.robot_parser.set_url(robots_url)
            self.robot_parser.read()
        except Exception as e:
            print(f"警告: 无法加载robots.txt: {e}")
    
    def _can_fetch(self, url: str) -> bool:
        """检查是否允许爬取该URL"""
        if not self.respect_robots:
            return True
        return self.robot_parser.can_fetch(DEFAULT_HEADERS['User-Agent'], url)
    
    def _is_same_domain(self, url: str) -> bool:
        """检查URL是否属于同一域名"""
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc == self.base_domain or not parsed.netloc
        except:
            return False
    
    def _normalize_url(self, url: str, base: str = None) -> str:
        """标准化URL"""
        if base is None:
            base = self.base_url
        
        # 如果是相对路径，转换为绝对路径
        if not url.startswith(('http://', 'https://', '//')):
            if url.startswith('/'):
                # 相对于根目录
                parsed_base = urllib.parse.urlparse(base)
                url = f"{parsed_base.scheme}://{parsed_base.netloc}{url}"
            else:
                # 相对于当前页面
                if not base.endswith('/'):
                    base += '/'
                url = urllib.parse.urljoin(base, url)
        
        # 处理协议相对URL
        if url.startswith('//'):
            url = f"https:{url}"
        
        # 移除片段标识符
        url = urllib.parse.urldefrag(url)[0]
        
        # 确保URL以/结尾（如果是目录）
        parsed = urllib.parse.urlparse(url)
        if not parsed.path:
            url = url.rstrip('/') + '/'
        
        return url
    
    def _get_file_extension(self, url: str) -> str:
        """从URL获取文件扩展名"""
        path = urllib.parse.urlparse(url).path
        ext = Path(path).suffix.lower()
        return ext
    
    def _is_downloadable_file(self, url: str) -> bool:
        """检查URL是否指向可下载文件"""
        ext = self._get_file_extension(url)
        return ext in DOWNLOADABLE_EXTENSIONS
    
    def _should_crawl(self, url: str, current_depth: int) -> bool:
        """判断是否应该爬取该URL"""
        # 检查深度限制
        if current_depth >= self.max_depth:
            return False
        
        # 检查是否已访问
        if url in self.visited_urls:
            return False
        
        # 检查域名
        if not self._is_same_domain(url):
            return False
        
        # 检查robots.txt
        if not self._can_fetch(url):
            return False
        
        # 对于文件下载，不进行进一步爬取
        if self._is_downloadable_file(url):
            return False
        
        return True
    
    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """从HTML中提取所有链接（增强版）"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        # 提取HTML标签中的链接
        html_links = self._extract_html_links(soup, base_url)
        links.extend(html_links)
        
        # 提取CSS中的链接
        css_links = self._extract_css_links(html, base_url)
        links.extend(css_links)
        
        # 提取JavaScript中的链接（基础正则匹配）
        js_links = self._extract_js_links(html, base_url)
        links.extend(js_links)
        
        # 提取meta refresh重定向
        meta_links = self._extract_meta_refresh_links(soup, base_url)
        links.extend(meta_links)
        
        # 去重
        unique_links = []
        seen = set()
        for link in links:
            if link and link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        return unique_links
    
    def _extract_html_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """提取HTML标签中的链接"""
        links = []
        
        # 定义所有可能包含URL的标签和属性
        url_attributes = {
            'a': ['href'],
            'link': ['href'],
            'script': ['src'],
            'img': ['src', 'srcset', 'data-src', 'data-original'],
            'source': ['src', 'srcset'],
            'iframe': ['src'],
            'frame': ['src'],
            'embed': ['src'],
            'object': ['data'],
            'video': ['src', 'poster'],
            'audio': ['src'],
            'track': ['src'],
            'area': ['href'],
            'base': ['href'],
            'form': ['action'],
            'button': ['formaction'],
            'input': ['src', 'formaction'],
            'meta': ['content'],  # 用于og:image等
            'applet': ['code', 'archive'],
            'bgsound': ['src'],
            'body': ['background'],
            'table': ['background'],
            'td': ['background'],
            'th': ['background'],
        }
        
        for tag_name, attrs in url_attributes.items():
            for tag in soup.find_all(tag_name):
                for attr in attrs:
                    if tag.get(attr):
                        urls = self._parse_attribute_value(tag[attr], base_url)
                        links.extend(urls)
        
        # 处理style属性中的URL
        for tag in soup.find_all(style=True):
            style_links = self._extract_css_urls(tag['style'], base_url)
            links.extend(style_links)
        
        return links
    
    def _extract_css_links(self, html: str, base_url: str) -> List[str]:
        """提取CSS中的链接"""
        links = []
        
        # 提取<style>标签中的CSS
        soup = BeautifulSoup(html, 'html.parser')
        for style_tag in soup.find_all('style'):
            css_content = style_tag.string
            if css_content:
                css_links = self._extract_css_urls(css_content, base_url)
                links.extend(css_links)
        
        # 提取link标签中的CSS文件（后续会下载并解析）
        for link_tag in soup.find_all('link', rel='stylesheet'):
            if link_tag.get('href'):
                url = self._normalize_url(link_tag['href'], base_url)
                links.append(url)
        
        return links
    
    def _extract_js_links(self, html: str, base_url: str) -> List[str]:
        """提取JavaScript中的链接（基础正则匹配）"""
        links = []
        
        # 常见URL模式的正则表达式
        url_patterns = [
            r'["\'](https?://[^"\'\s]+)["\']',  # 带引号的完整URL
            r'["\'](/[^"\'\s]+)["\']',  # 带引号的绝对路径
            r'["\'](\.{1,2}/[^"\'\s]+)["\']',  # 带引号的相对路径
            r'url\(["\']?([^"\'\)]+)["\']?\)',  # CSS url()
            r'src=["\']([^"\']+)["\']',  # src属性
            r'href=["\']([^"\']+)["\']',  # href属性
            r'action=["\']([^"\']+)["\']',  # form action
            r'["\']([a-zA-Z0-9_\-]+\.(?:js|css|jpg|png|gif|pdf|docx?|xlsx?|pptx?|zip|rar|7z|mp[34]|avi|mkv))["\']',  # 常见文件
        ]
        
        for pattern in url_patterns:
            matches = re.finditer(pattern, html, re.IGNORECASE)
            for match in matches:
                url = match.group(1)
                try:
                    normalized_url = self._normalize_url(url, base_url)
                    links.append(normalized_url)
                except:
                    pass
        
        # 提取<script src>标签
        soup = BeautifulSoup(html, 'html.parser')
        for script_tag in soup.find_all('script', src=True):
            url = self._normalize_url(script_tag['src'], base_url)
            links.append(url)
        
        return links
    
    def _extract_meta_refresh_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """提取meta refresh重定向链接"""
        links = []
        
        for meta_tag in soup.find_all('meta'):
            http_equiv = meta_tag.get('http-equiv', '').lower()
            content = meta_tag.get('content', '')
            
            if http_equiv == 'refresh':
                # 解析格式如: 5;url=http://example.com
                match = re.search(r'url=(.+)', content, re.IGNORECASE)
                if match:
                    url = match.group(1)
                    normalized_url = self._normalize_url(url, base_url)
                    links.append(normalized_url)
        
        return links
    
    def _extract_css_urls(self, css_content: str, base_url: str) -> List[str]:
        """从CSS内容中提取URL"""
        links = []
        
        # 匹配CSS中的url()
        url_pattern = r'url\(["\']?([^"\'\)]+)["\']?\)'
        matches = re.finditer(url_pattern, css_content, re.IGNORECASE)
        
        for match in matches:
            url = match.group(1)
            # 跳过data:URI和内联数据
            if not url.startswith(('data:', '#')):
                try:
                    normalized_url = self._normalize_url(url, base_url)
                    links.append(normalized_url)
                except:
                    pass
        
        # 匹配@import规则
        import_pattern = r'@import\s+["\']([^"\']+)["\']'
        matches = re.finditer(import_pattern, css_content, re.IGNORECASE)
        
        for match in matches:
            url = match.group(1)
            if not url.startswith(('data:', '#')):
                try:
                    normalized_url = self._normalize_url(url, base_url)
                    links.append(normalized_url)
                except:
                    pass
        
        return links
    
    def _parse_attribute_value(self, value: str, base_url: str) -> List[str]:
        """解析属性值中的URL（处理srcset等）"""
        urls = []
        
        # 处理srcset属性（包含多个URL和描述符）
        if ',' in value and any(x in value.lower() for x in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            # 可能是srcset
            for part in value.split(','):
                part = part.strip()
                # 提取URL部分（忽略描述符如 2x, 100w等）
                url_part = part.split()[0] if ' ' in part else part
                if url_part:
                    try:
                        normalized_url = self._normalize_url(url_part, base_url)
                        urls.append(normalized_url)
                    except:
                        pass
        else:
            # 单个URL
            try:
                normalized_url = self._normalize_url(value, base_url)
                urls.append(normalized_url)
            except:
                pass
        
        return urls
    
    def _download_file(self, url: str) -> bool:
        """下载文件"""
        try:
            # 获取文件名
            path = urllib.parse.urlparse(url).path
            filename = Path(path).name
            
            # 如果没有文件名，生成一个
            if not filename:
                filename = f"file_{int(time.time())}"
                ext = self._get_file_extension(url)
                if ext:
                    filename += ext
            
            # 创建目录结构
            relative_path = urllib.parse.urlparse(url).path.lstrip('/')
            file_path = self.output_dir / relative_path
            
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 下载文件
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # 保存文件
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 更新统计
            file_size = os.path.getsize(file_path)
            self.stats['files_downloaded'] += 1
            self.stats['total_size'] += file_size
            
            print(f"✓ 下载: {filename} ({file_size:,} bytes)")
            return True
            
        except Exception as e:
            print(f"✗ 下载失败 {url}: {e}")
            self.stats['errors'] += 1
            return False
    
    def _crawl_page(self, url: str, depth: int):
        """爬取单个页面（增强版）"""
        try:
            # 检查URL数量限制
            if len(self.visited_urls) >= self.max_urls:
                print(f"⚠️ 达到最大URL数量限制 ({self.max_urls})，停止爬取")
                return
            
            # 延迟以避免被封
            time.sleep(self.delay)
            
            print(f"[深度 {depth}] 爬取: {url}")
            
            # 发送请求
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # 检查重定向
            if response.history:
                self.stats['redirects_followed'] += len(response.history)
                final_url = response.url
                if final_url != url:
                    print(f"  ↳ 重定向到: {final_url}")
                    url = final_url
            
            # 更新统计
            self.stats['pages_crawled'] += 1
            self.visited_urls.add(url)
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '').lower()
            
            # 处理HTML内容
            if 'text/html' in content_type:
                html = response.text
                
                # 保存HTML文件
                self._save_html_file(url, html)
                
                # 提取链接（增强版）
                links = self._extract_links_enhanced(html, url, content_type)
                
                # 处理提取到的链接
                self._process_extracted_links(links, depth, url)
            
            # 处理CSS文件
            elif 'text/css' in content_type and self.parse_css_files:
                css_content = response.text
                
                # 保存CSS文件
                self._save_css_file(url, css_content)
                
                # 解析CSS中的链接
                css_links = self._extract_css_urls(css_content, url)
                self.stats['css_files_parsed'] += 1
                
                # 处理CSS链接
                self._process_extracted_links(css_links, depth, url)
                
                # 如果CSS文件较大，提示解析
                if len(css_content) > 10000:
                    print(f"  ↳ 解析了大型CSS文件 ({len(css_content):,} 字节)")
            
            # 处理JavaScript文件
            elif any(js_type in content_type for js_type in ['javascript', 'application/javascript', 'text/javascript']) and self.parse_js_files:
                js_content = response.text
                
                # 保存JS文件
                self._save_js_file(url, js_content)
                
                # 解析JS中的链接
                js_links = self._extract_js_links_enhanced(js_content, url)
                self.stats['js_files_parsed'] += 1
                
                # 处理JS链接
                self._process_extracted_links(js_links, depth, url)
                
                # 如果JS文件较大，提示解析
                if len(js_content) > 50000:
                    print(f"  ↳ 解析了大型JS文件 ({len(js_content):,} 字节)")
            
            # 如果是其他可下载文件类型
            elif self._is_downloadable_file(url):
                self._download_file(url)
            
            # 如果是未知内容类型，但看起来像文件
            elif self._looks_like_file(url):
                print(f"  ↳ 未知内容类型，尝试下载: {content_type}")
                self._download_file(url)
            
        except requests.exceptions.Timeout:
            print(f"✗ 请求超时 {url}")
            self.stats['errors'] += 1
        except requests.exceptions.TooManyRedirects:
            print(f"✗ 重定向过多 {url}")
            self.stats['errors'] += 1
        except Exception as e:
            print(f"✗ 爬取失败 {url}: {e}")
            self.stats['errors'] += 1
    
    def _extract_links_enhanced(self, content: str, base_url: str, content_type: str) -> List[str]:
        """增强版链接提取（支持HTML/CSS/JS）"""
        links = []
        
        if 'text/html' in content_type:
            # HTML提取
            soup = BeautifulSoup(content, 'html.parser')
            html_links = self._extract_html_links(soup, base_url)
            links.extend(html_links)
            
            # 提取CSS中的链接
            css_links = self._extract_css_links(content, base_url)
            links.extend(css_links)
            
            # 提取JavaScript中的链接
            js_links = self._extract_js_links(content, base_url)
            links.extend(js_links)
            
            # 提取meta重定向
            meta_links = self._extract_meta_refresh_links(soup, base_url)
            links.extend(meta_links)
        
        elif 'text/css' in content_type:
            # CSS提取
            css_links = self._extract_css_urls(content, base_url)
            links.extend(css_links)
        
        elif any(js_type in content_type for js_type in ['javascript', 'application/javascript', 'text/javascript']):
            # JavaScript提取
            js_links = self._extract_js_links_enhanced(content, base_url)
            links.extend(js_links)
        
        # 去重
        unique_links = []
        seen = set()
        for link in links:
            if link and link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        return unique_links
    
    def _extract_js_links_enhanced(self, js_content: str, base_url: str) -> List[str]:
        """增强版JavaScript链接提取"""
        links = []
        
        # 更多URL模式
        url_patterns = [
            # 字符串中的URL
            r'["\'](https?://[^"\'\s]+)["\']',
            r'["\'](/[^"\'\s]+)["\']',
            r'["\'](\.{1,2}/[^"\'\s]+)["\']',
            r'["\'](//[^"\'\s]+)["\']',
            # 变量赋值中的URL
            r'\b(?:src|href|url|action)\s*[=:]\s*["\']([^"\']+)["\']',
            # 函数调用中的URL
            r'\.(?:load|get|post|ajax)\s*\(\s*["\']([^"\']+)["\']',
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'XMLHttpRequest\s*\(\s*["\']([^"\']+)["\']',
            # 模板字符串中的URL
            r'`(https?://[^`]+)`',
            r'`(/[^`]+)`',
            # 对象属性中的URL
            r'\b(?:src|href|url)\s*:\s*["\']([^"\']+)["\']',
            # 常见API端点
            r'["\'](/api/[^"\']+)["\']',
            r'["\'](/ajax/[^"\']+)["\']',
            r'["\'](/json/[^"\']+)["\']',
        ]
        
        for pattern in url_patterns:
            matches = re.finditer(pattern, js_content, re.IGNORECASE)
            for match in matches:
                url = match.group(1)
                try:
                    normalized_url = self._normalize_url(url, base_url)
                    if normalized_url not in links:
                        links.append(normalized_url)
                except:
                    pass
        
        return links
    
    def _process_extracted_links(self, links: List[str], current_depth: int, source_url: str):
        """处理提取到的链接"""
        for link in links:
            # 检查是否应该爬取
            if self._should_crawl(link, current_depth + 1):
                # 根据爬取策略添加到队列
                if self.crawl_strategy == 'depth_first':
                    # 深度优先：新链接插入到队列开头
                    self.url_queue.insert(0, (link, current_depth + 1))
                else:
                    # 广度优先：新链接添加到队列末尾（默认）
                    self.url_queue.append((link, current_depth + 1))
            
            # 如果是可下载文件，直接下载
            elif self._is_downloadable_file(link) and link not in self.visited_urls:
                self.visited_urls.add(link)
                self._download_file(link)
    
    def _save_html_file(self, url: str, html: str):
        """保存HTML文件"""
        relative_path = urllib.parse.urlparse(url).path.lstrip('/')
        if not relative_path or relative_path.endswith('/'):
            relative_path += 'index.html'
        elif not relative_path.endswith('.html') and not relative_path.endswith('.htm'):
            relative_path += '.html'
        
        file_path = self.output_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _save_css_file(self, url: str, css_content: str):
        """保存CSS文件"""
        relative_path = urllib.parse.urlparse(url).path.lstrip('/')
        if not relative_path.endswith('.css'):
            # 尝试从URL推断文件名
            filename = Path(relative_path).name
            if not filename:
                filename = 'style.css'
            elif not filename.endswith('.css'):
                filename += '.css'
            relative_path = str(Path(relative_path).parent / filename)
        
        file_path = self.output_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
    
    def _save_js_file(self, url: str, js_content: str):
        """保存JavaScript文件"""
        relative_path = urllib.parse.urlparse(url).path.lstrip('/')
        if not relative_path.endswith('.js'):
            # 尝试从URL推断文件名
            filename = Path(relative_path).name
            if not filename:
                filename = 'script.js'
            elif not filename.endswith('.js'):
                filename += '.js'
            relative_path = str(Path(relative_path).parent / filename)
        
        file_path = self.output_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(js_content)
    
    def _looks_like_file(self, url: str) -> bool:
        """通过URL判断是否像文件"""
        # 检查是否有查询参数（通常不是静态文件）
        if '?' in url:
            return False
        
        # 检查路径中是否有明显的文件特征
        path = urllib.parse.urlparse(url).path
        
        # 包含点号且最后一部分有扩展名特征
        if '.' in path:
            last_part = path.split('/')[-1]
            if '.' in last_part and len(last_part.split('.')[-1]) <= 5:
                # 排除常见动态页面扩展名
                dynamic_extensions = {'.php', '.asp', '.aspx', '.jsp', '.do', '.action'}
                ext = '.' + last_part.split('.')[-1].lower()
                if ext not in dynamic_extensions:
                    return True
        
        # 路径以常见文件扩展名结尾
        common_file_patterns = [
            '/download/', '/file/', '/static/', '/assets/', '/media/',
            '/images/', '/img/', '/css/', '/js/', '/fonts/', '/documents/',
            '/pdf/', '/doc/', '/zip/', '/rar/', '/mp3/', '/mp4/', '/avi/'
        ]
        
        for pattern in common_file_patterns:
            if pattern in url.lower():
                return True
        
        return False
    
    def crawl(self):
        """开始爬取"""
        print(f"开始爬取: {self.base_url}")
        print(f"输出目录: {self.output_dir}")
        print(f"最大深度: {self.max_depth}")
        print(f"并发数: {self.max_workers}")
        print("-" * 50)
        
        start_time = time.time()
        
        # 使用线程池并发爬取
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            with tqdm.tqdm(desc="爬取进度", unit="页") as pbar:
                while self.url_queue or futures:
                    # 提交新任务
                    while self.url_queue and len(futures) < self.max_workers * 2:
                        url, depth = self.url_queue.pop(0)
                        future = executor.submit(self._crawl_page, url, depth)
                        futures.append(future)
                    
                    # 处理完成的任务
                    completed = []
                    for future in futures:
                        if future.done():
                            try:
                                future.result()
                            except Exception as e:
                                print(f"任务执行错误: {e}")
                            completed.append(future)
                            pbar.update(1)
                    
                    # 移除已完成的任务
                    for future in completed:
                        futures.remove(future)
                    
                    # 短暂休眠
                    time.sleep(0.1)
        
        # 打印统计信息
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 60)
        print("爬取完成!")
        print(f"总用时: {elapsed_time:.2f} 秒")
        print("-" * 40)
        print(f"爬取页面: {self.stats['pages_crawled']}")
        print(f"下载文件: {self.stats['files_downloaded']}")
        print(f"CSS文件解析: {self.stats['css_files_parsed']}")
        print(f"JS文件解析: {self.stats['js_files_parsed']}")
        print(f"重定向跟踪: {self.stats['redirects_followed']}")
        print("-" * 40)
        print(f"总数据大小: {self.stats['total_size']:,} bytes")
        print(f"错误数量: {self.stats['errors']}")
        print(f"访问URL总数: {len(self.visited_urls)}")
        print("-" * 40)
        if elapsed_time > 0:
            speed = self.stats['pages_crawled'] / elapsed_time
            print(f"爬取速度: {speed:.2f} 页/秒")
        print(f"输出目录: {self.output_dir.absolute()}")
        print("=" * 60)


def main():
    """主函数"""
    print("=== 网站文件爬取工具 ===")
    print("此版本的功能:")
    print("  • 支持400+种文件格式爬取")
    print("  • 深度解析HTML/CSS/JS文件")
    print("  • 智能文件类型识别")
    print("  • 支持广度优先/深度优先策略")
    print("  • 多线程并发下载")
    print("")
    
    # 获取用户输入
    try:
        url = input("请输入目标网站URL (例如 https://example.com): ").strip()
        if not url:
            print("错误: URL不能为空")
            return
        
        # 验证URL格式
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        output_dir = input("请输入输出目录 [默认: downloads]: ").strip()
        if not output_dir:
            output_dir = "downloads"
        
        max_depth = input("请输入最大爬取深度 [默认: 10]: ").strip()
        max_depth = int(max_depth) if max_depth.isdigit() else 10
        
        max_workers = input("请输入并发线程数 [默认: 10]: ").strip()
        max_workers = int(max_workers) if max_workers.isdigit() else 10
        
        delay = input("请输入请求延迟(秒) [默认: 0.3]: ").strip()
        delay = float(delay) if delay.replace('.', '').isdigit() else 0.3
        
        respect_robots = input("是否遵守robots.txt? [y/n, 默认: y]: ").strip().lower()
        respect_robots = respect_robots != 'n'
        
        # 新增配置选项
        print("\n--- 高级配置 ---")
        
        crawl_strategy = input("爬取策略 [广度优先(b)/深度优先(d), 默认: b]: ").strip().lower()
        if crawl_strategy == 'd':
            crawl_strategy = 'depth_first'
        else:
            crawl_strategy = 'breadth_first'
        
        follow_redirects = input("是否跟踪重定向? [y/n, 默认: y]: ").strip().lower()
        follow_redirects = follow_redirects != 'n'
        
        parse_css = input("是否解析CSS文件中的链接? [y/n, 默认: y]: ").strip().lower()
        parse_css = parse_css != 'n'
        
        parse_js = input("是否解析JS文件中的链接? [y/n, 默认: y]: ").strip().lower()
        parse_js = parse_js != 'n'
        
        max_urls = input("最大爬取URL数量限制 [默认: 10000]: ").strip()
        max_urls = int(max_urls) if max_urls.isdigit() else 10000
        
        timeout = input("请求超时时间(秒) [默认: 30]: ").strip()
        timeout = int(timeout) if timeout.isdigit() else 30
        
        print("\n" + "=" * 60)
        print("配置确认:")
        print(f"目标网站: {url}")
        print(f"输出目录: {output_dir}")
        print(f"最大深度: {max_depth}")
        print(f"并发线程: {max_workers}")
        print(f"请求延迟: {delay}秒")
        print(f"遵守robots.txt: {'是' if respect_robots else '否'}")
        print(f"爬取策略: {'深度优先' if crawl_strategy == 'depth_first' else '广度优先'}")
        print(f"跟踪重定向: {'是' if follow_redirects else '否'}")
        print(f"解析CSS文件: {'是' if parse_css else '否'}")
        print(f"解析JS文件: {'是' if parse_js else '否'}")
        print(f"最大URL数量: {max_urls}")
        print(f"请求超时: {timeout}秒")
        print("=" * 60)
        
        confirm = input("\n是否开始爬取? [y/n]: ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return
        
        # 创建并运行爬虫
        crawler = WebCrawler(
            base_url=url,
            output_dir=output_dir,
            max_depth=max_depth,
            max_workers=max_workers,
            delay=delay,
            respect_robots=respect_robots,
            crawl_strategy=crawl_strategy,
            follow_redirects=follow_redirects,
            parse_css_files=parse_css,
            parse_js_files=parse_js,
            max_urls=max_urls,
            timeout=timeout
        )
        
        crawler.crawl()
        
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()