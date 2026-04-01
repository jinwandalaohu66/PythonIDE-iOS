#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相册照片统计脚本
统计相册中的照片数量，并按类型分类
"""

import photos
import dialogs
import console
from datetime import datetime

def main():
    """主函数：统计相册照片"""
    console.clear()
    print("📸 相册照片统计")
    print("=" * 40)
    
    # 检查相册权限
    if not photos.is_available():
        print("❌ 无法访问相册，请检查权限设置")
        dialogs.alert("权限错误", "无法访问相册，请检查App权限设置")
        return
    
    print("正在扫描相册...")
    
    try:
        # 获取所有照片
        all_photos = photos.get_assets(media_type='photo', limit=0)
        total_count = len(all_photos)
        
        # 获取所有视频
        all_videos = photos.get_assets(media_type='video', limit=0)
        video_count = len(all_videos)
        
        # 获取所有媒体（照片+视频）
        all_media = photos.get_assets(media_type='all', limit=0)
        media_count = len(all_media)
        
        print(f"✅ 扫描完成！")
        print()
        
        # 显示统计结果
        print("📊 统计结果：")
        print(f"   照片数量：{total_count} 张")
        print(f"   视频数量：{video_count} 个")
        print(f"   媒体总数：{media_count} 个")
        print()
        
        # 如果有照片，显示一些详细信息
        if total_count > 0:
            # 获取最近的照片
            recent_photos = photos.get_recent_images(count=min(5, total_count))
            print("📅 最近的照片：")
            for i, asset in enumerate(recent_photos, 1):
                try:
                    # 尝试获取日期信息
                    if hasattr(asset, 'creation_date'):
                        # 确保 creation_date 是 datetime 对象
                        from datetime import datetime
                        if isinstance(asset.creation_date, (int, float)):
                            # 如果是时间戳，转换为 datetime
                            date_obj = datetime.fromtimestamp(asset.creation_date)
                            date_str = date_obj.strftime("%Y-%m-%d %H:%M")
                        else:
                            # 假设是 datetime 对象
                            date_str = asset.creation_date.strftime("%Y-%m-%d %H:%M")
                    else:
                        date_str = "未知日期"
                except:
                    date_str = "日期未知"
                
                # 获取照片尺寸
                width = getattr(asset, 'pixel_width', '未知')
                height = getattr(asset, 'pixel_height', '未知')
                print(f"   {i}. {date_str} - {width}x{height}")
        
        # 获取相册信息
        print()
        print("📁 相册信息：")
        albums = photos.get_albums()
        smart_albums = photos.get_smart_albums()
        
        print(f"   普通相册：{len(albums)} 个")
        print(f"   智能相册：{len(smart_albums)} 个")
        
        # 显示一些特殊相册
        special_albums = []
        try:
            screenshots = photos.get_screenshots_album()
            if screenshots:
                special_albums.append(f"截屏 ({screenshots.count} 张)")
        except:
            pass
            
        try:
            recently_added = photos.get_recently_added_album()
            if recently_added:
                special_albums.append(f"最近添加 ({recently_added.count} 张)")
        except:
            pass
            
        try:
            selfies = photos.get_selfies_album()
            if selfies:
                special_albums.append(f"自拍 ({selfies.count} 张)")
        except:
            pass
        
        if special_albums:
            print(f"   特殊相册：{', '.join(special_albums)}")
        
        print()
        print("=" * 40)
        print("📱 操作提示：")
        print("   1. 要查看照片详情，可以使用 photos.pick_image()")
        print("   2. 要拍照，可以使用 photos.capture_image()")
        print("   3. 要保存图片到相册，可以使用 photos.save_image()")
        
        # 显示弹窗总结
        summary = f"""
照片统计完成！

📸 照片：{total_count} 张
🎬 视频：{video_count} 个
📁 相册：{len(albums)} 个普通相册
        {len(smart_albums)} 个智能相册

点击确定继续...
        """
        dialogs.alert("相册统计结果", summary.strip())
        
    except Exception as e:
        print(f"❌ 发生错误：{e}")
        dialogs.alert("错误", f"统计相册时发生错误：{e}")

if __name__ == "__main__":
    main()