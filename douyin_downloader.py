import requests
import json
import os
import time
import random
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from typing import List, Dict

class DouyinDownloader:
    def __init__(self, delay_range=(1, 5), max_workers=3):
        """
        初始化下载器
        :param delay_range: 延迟范围(最小秒数, 最大秒数)
        :param max_workers: 最大并发数
        """
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'referer': 'https://www.douyin.com/',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'origin': 'https://www.douyin.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'x-requested-with': 'XMLHttpRequest',
            'cookie': ''
        }
        self.delay_range = delay_range
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def _random_delay(self):
        """添加随机延迟"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
        
    def get_video_list(self, user_url: str) -> List[Dict]:
        """获取视频列表"""
        try:
            if '?' in user_url:
                user_url = user_url.split('?')[0]
            sec_uid = user_url.split('user/')[1]
            
            api_url = 'https://www.douyin.com/aweme/v1/web/aweme/post/'
            params = {
                'device_platform': 'webapp',
                'aid': '6383',
                'channel': 'channel_pc_web',
                'sec_user_id': sec_uid,
                'max_cursor': '0',
                'count': '18',
                'publish_video_strategy_type': '2',
                'version_code': '290100',
                'version_name': '29.1.0',
                'cookie_enabled': 'true',
                'platform': 'PC',
                'downlink': '10'
            }
            
            headers = self.headers.copy()
            headers.update({
                'authority': 'www.douyin.com',
                'accept': 'application/json, text/plain, */*',
                'referer': 'https://www.douyin.com/',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty'
            })
            
            # 添加随机延迟
            self._random_delay()
            
            response = requests.get(api_url, headers=headers, params=params)
            
            if response.status_code != 200:
                raise Exception(f"API请求失败，状态码：{response.status_code}")
            
            data = json.loads(response.text)
            
            videos = []
            for item in data.get('aweme_list', []):
                try:
                    video_data = {
                        'desc': item['desc'],
                        'video_url': item['video']['play_addr']['url_list'][0]
                    }
                    videos.append(video_data)
                except KeyError as e:
                    print(f"处理视频数据时出错: {str(e)}, item: {item}")
                    continue
                    
            return videos
            
        except Exception as e:
            raise Exception(f"获取视频列表失败: {str(e)}")
    
    def download_video(self, video_data: Dict, output_dir: str = 'downloads'):
        """下载单个视频"""
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            desc = video_data['desc']
            video_url = video_data['video_url']
            
            # 处理文件名中的非法字符
            desc = "".join(x for x in desc if x.isalnum() or x in (' ', '-', '_'))
            
            # 添加随机延迟
            self._random_delay()
            
            video_response = requests.get(video_url, headers=self.headers)
            filepath = os.path.join(output_dir, f'{desc}.mp4')
            
            with open(filepath, 'wb') as f:
                f.write(video_response.content)
                
            return filepath
            
        except Exception as e:
            print(f"下载视频失败 [{desc}]: {str(e)}")
            return None

    def get_all_videos(self, user_url: str, page_size: int = 18) -> List[Dict]:
        """
        获取所有视频
        :param user_url: 用户主页URL
        :param page_size: 每页视频数量
        :return: 视频列表
        """
        videos = []
        max_cursor = 0
        has_more = True
        
        while has_more:
            try:
                # 添加随机延迟
                self._random_delay()
                
                params = {
                    'device_platform': 'webapp',
                    'aid': '6383',
                    'channel': 'channel_pc_web',
                    'sec_user_id': user_url.split('user/')[1],
                    'max_cursor': str(max_cursor),
                    'count': str(page_size),  # 使用传入的页面大小
                    'publish_video_strategy_type': '2',
                    'version_code': '290100',
                    'version_name': '29.1.0',
                    'cookie_enabled': 'true',
                    'platform': 'PC',
                    'downlink': '10'
                }
                
                api_url = 'https://www.douyin.com/aweme/v1/web/aweme/post/'
                headers = self.headers.copy()
                headers.update({
                    'authority': 'www.douyin.com',
                    'accept': 'application/json, text/plain, */*',
                    'referer': 'https://www.douyin.com/',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-dest': 'empty'
                })
                
                response = requests.get(api_url, headers=headers, params=params)
                data = json.loads(response.text)
                
                for item in data.get('aweme_list', []):
                    try:
                        video_data = {
                            'desc': item['desc'],
                            'video_url': item['video']['play_addr']['url_list'][0]
                        }
                        videos.append(video_data)
                    except KeyError as e:
                        print(f"处理视频数据时出错: {str(e)}")
                        continue
                
                max_cursor = data.get('max_cursor', 0)
                has_more = data.get('has_more', 0)
                
            except Exception as e:
                print(f"获取视频列表失败: {str(e)}")
                break
                
        return videos
        
    def batch_download(self, video_list: List[Dict], output_dir: str = 'downloads'):
        """并发下载多个视频"""
        futures = []
        for video_data in video_list:
            future = self.executor.submit(self.download_video, video_data, output_dir)
            futures.append(future)
            
        # 等待所有下载完成
        results = []
        for future in futures:
            try:
                filepath = future.result()
                if filepath:
                    results.append(filepath)
            except Exception as e:
                print(f"下载失败: {str(e)}")
                
        return results

def main():
    # 示例使用
    downloader = DouyinDownloader(
        delay_range=(1, 5),  # 1-5秒的随机延迟
        max_workers=3        # 最多3个并发下载
    )
    
    user_url = "https://www.douyin.com/user/{user_id}"
    
    try:
        # 获取视频列表
        print("正在获取视频列表...")
        videos = downloader.get_video_list(user_url)
        print(f"找到 {len(videos)} 个视频")
        
        # 并发下载视频
        print("开始下载视频...")
        downloaded_files = downloader.batch_download(videos)
        print(f"成功下载 {len(downloaded_files)} 个视频")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        # 关闭线程池
        downloader.executor.shutdown()

if __name__ == "__main__":
    main() 
