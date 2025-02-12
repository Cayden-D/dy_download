import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QTextEdit, QListWidget, QMessageBox, QSpinBox,
                           QGroupBox, QCheckBox, QProgressBar)
from douyin_downloader import DouyinDownloader

class DouyinDownloaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.downloader = None  # 将在应用设置时初始化
        self.init_ui()
        self.show_disclaimer()
        
    def init_ui(self):
        self.setWindowTitle('抖音视频下载器')
        self.setGeometry(300, 300, 900, 700)
        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 设置区域
        settings_group = QGroupBox("下载设置")
        settings_layout = QVBoxLayout()
        
        # 延迟设置
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel('延迟范围(秒):'))
        self.min_delay = QSpinBox()
        self.min_delay.setRange(1, 5)
        self.min_delay.setValue(1)
        self.max_delay = QSpinBox()
        self.max_delay.setRange(1, 5)
        self.max_delay.setValue(3)
        delay_layout.addWidget(self.min_delay)
        delay_layout.addWidget(QLabel('-'))
        delay_layout.addWidget(self.max_delay)
        settings_layout.addLayout(delay_layout)
        
        # 并发设置
        concurrent_layout = QHBoxLayout()
        concurrent_layout.addWidget(QLabel('最大并发数:'))
        self.max_workers = QSpinBox()
        self.max_workers.setRange(1, 5)
        self.max_workers.setValue(3)
        concurrent_layout.addWidget(self.max_workers)
        concurrent_layout.addStretch()
        settings_layout.addLayout(concurrent_layout)
        
        # 分页设置
        page_layout = QHBoxLayout()
        self.enable_paging = QCheckBox('启用分页获取')
        self.enable_paging.setChecked(True)
        self.page_size = QSpinBox()
        self.page_size.setRange(10, 30)
        self.page_size.setValue(18)
        self.page_size.setEnabled(False)
        self.enable_paging.stateChanged.connect(lambda: self.page_size.setEnabled(self.enable_paging.isChecked()))
        page_layout.addWidget(self.enable_paging)
        page_layout.addWidget(QLabel('每页数量:'))
        page_layout.addWidget(self.page_size)
        page_layout.addStretch()
        settings_layout.addLayout(page_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Cookie输入区域
        cookie_layout = QHBoxLayout()
        cookie_label = QLabel('Cookie:')
        self.cookie_input = QLineEdit()
        cookie_layout.addWidget(cookie_label)
        cookie_layout.addWidget(self.cookie_input)
        layout.addLayout(cookie_layout)
        
        # 用户URL输入区域
        url_layout = QHBoxLayout()
        url_label = QLabel('用户URL:')
        self.url_input = QLineEdit()
        self.fetch_btn = QPushButton('获取视频列表')
        self.fetch_btn.clicked.connect(self.fetch_videos)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.fetch_btn)
        layout.addLayout(url_layout)
        
        # 在视频列表和下载按钮之间添加选择控制按钮
        selection_layout = QHBoxLayout()
        
        # 全选按钮
        self.select_all_btn = QPushButton('全选')
        self.select_all_btn.clicked.connect(self.select_all_videos)
        selection_layout.addWidget(self.select_all_btn)
        
        # 反选按钮
        self.invert_select_btn = QPushButton('反选')
        self.invert_select_btn.clicked.connect(self.invert_selection)
        selection_layout.addWidget(self.invert_select_btn)
        
        # 取消选择按钮
        self.clear_select_btn = QPushButton('取消选择')
        self.clear_select_btn.clicked.connect(self.clear_selection)
        selection_layout.addWidget(self.clear_select_btn)
        
        # 添加到主布局
        layout.addLayout(selection_layout)
        
        # 视频列表区域
        self.video_list = QListWidget()
        self.video_list.setSelectionMode(QListWidget.ExtendedSelection)
        layout.addWidget(self.video_list)
        
        # 在下载按钮旁添加选择状态显示
        download_layout = QHBoxLayout()
        
        self.selection_status = QLabel('已选择: 0/0')
        download_layout.addWidget(self.selection_status)
        
        self.download_btn = QPushButton('下载选中视频')
        self.download_btn.clicked.connect(self.download_selected)
        download_layout.addWidget(self.download_btn)
        
        layout.addLayout(download_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 日志区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # 添加选择变化事件处理
        self.video_list.itemSelectionChanged.connect(self.update_selection_status)
        
    def init_downloader(self):
        """根据设置初始化下载器"""
        self.downloader = DouyinDownloader(
            delay_range=(self.min_delay.value(), self.max_delay.value()),
            max_workers=self.max_workers.value()
        )
        self.downloader.headers['cookie'] = self.cookie_input.text()
        
    def log(self, message):
        """添加日志信息"""
        self.log_text.append(message)
        
    def fetch_videos(self):
        """获取视频列表"""
        if not self.cookie_input.text() or not self.url_input.text():
            QMessageBox.warning(self, '警告', '请输入Cookie和用户URL')
            return
            
        self.init_downloader()
        self.video_list.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 显示忙碌状态
        
        try:
            self.log("正在获取视频列表...")
            if self.enable_paging.isChecked():
                videos = self.downloader.get_all_videos(
                    self.url_input.text(),
                    page_size=self.page_size.value()
                )
            else:
                videos = self.downloader.get_video_list(self.url_input.text())
                
            self.video_list.clear()
            for video in videos:
                self.video_list.addItem(f"{video['desc']} ({video['video_url']})")
            self.log(f'成功获取到 {len(videos)} 个视频')
            self.update_selection_status()  # 更新选择状态
            
        except Exception as e:
            error_msg = str(e)
            self.log(f'获取视频列表失败: {error_msg}')
            QMessageBox.critical(self, '错误', f'获取视频列表失败:\n{error_msg}')
        finally:
            self.progress_bar.setVisible(False)
            
    def download_selected(self):
        """下载选中的视频"""
        selected_items = self.video_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '警告', '请选择要下载的视频')
            return
            
        try:
            videos = []
            for item in selected_items:
                text = item.text()
                desc = text.split(' (')[0]
                url = text.split(' (')[1].rstrip(')')
                videos.append({'desc': desc, 'video_url': url})
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, len(videos))
            self.progress_bar.setValue(0)
            
            self.log(f'开始下载 {len(videos)} 个视频...')
            downloaded_files = self.downloader.batch_download(videos)
            self.log(f'成功下载 {len(downloaded_files)} 个视频')
            
            if downloaded_files:
                QMessageBox.information(self, '完成', f'成功下载 {len(downloaded_files)} 个视频')
                
        except Exception as e:
            self.log(f'下载失败: {str(e)}')
            QMessageBox.critical(self, '错误', f'下载失败:\n{str(e)}')
        finally:
            self.progress_bar.setVisible(False)

    def select_all_videos(self):
        """全选所有视频"""
        for i in range(self.video_list.count()):
            self.video_list.item(i).setSelected(True)
    
    def invert_selection(self):
        """反选视频"""
        for i in range(self.video_list.count()):
            item = self.video_list.item(i)
            item.setSelected(not item.isSelected())
    
    def clear_selection(self):
        """取消所有选择"""
        self.video_list.clearSelection()

    def update_selection_status(self):
        """更新选择状态显示"""
        total = self.video_list.count()
        selected = len(self.video_list.selectedItems())
        self.selection_status.setText(f'已选择: {selected}/{total}')

    def show_disclaimer(self):
        """显示免责声明"""
        disclaimer = (
            "免责声明：\n\n"
            "1. 本工具仅用于学习和研究目的\n"
            "2. 请遵守抖音的使用条款和规则\n"
            "3. 请不要过度频繁地使用本工具\n"
            "4. 仅下载您有权限访问的内容\n"
            "5. 下载的内容仅供个人使用，不得用于商业目的\n\n"
            "继续使用表示您同意以上条款。"
        )
        QMessageBox.warning(self, '免责声明', disclaimer)

def main():
    app = QApplication(sys.argv)
    gui = DouyinDownloaderGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 