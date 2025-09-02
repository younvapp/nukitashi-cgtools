import glob
import os
import argparse


def is_empty_folder(folder_path):
    """检查文件夹是否为空（包括只包含空子文件夹的情况）"""
    try:
        # 获取文件夹中的所有项目
        items = list(os.listdir(folder_path))

        # 如果文件夹完全为空
        if not items:
            return True

        # 检查是否只包含文件夹，且所有子文件夹都是空的
        for item in items:
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                # 如果包含文件，则不是空文件夹
                return False
            elif os.path.isdir(item_path):
                # 如果包含非空子文件夹，则不是空文件夹
                if not is_empty_folder(item_path):
                    return False

        # 如果只包含空文件夹或完全为空，则认为是空文件夹
        return True

    except (OSError, PermissionError) as e:
        print(f"⚠️ 无法访问文件夹 {folder_path}: {e}")
        return False


def remove_empty_folders(root_path, dry_run=False, verbose=False):
    """递归删除空文件夹

    Args:
        root_path: 要清理的根目录
        dry_run: 是否只是预览而不实际删除
        verbose: 是否显示详细信息
    """
    removed_count = 0
    checked_count = 0

    for root, dirs, _ in os.walk(root_path, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            checked_count += 1

            if is_empty_folder(dir_path):
                if dry_run:
                    print(f"🔍 [预览] 将删除空文件夹: {dir_path}")
                    removed_count += 1
                else:
                    try:
                        os.rmdir(dir_path)
                        print(f"✅ 已删除空文件夹: {dir_path}")
                        removed_count += 1
                    except OSError as e:
                        print(f"❌ 删除失败 {dir_path}: {e}")
            elif verbose:
                print(f"📁 保留非空文件夹: {dir_path}")

    return removed_count, checked_count


def remove_empty_folders_multiple_dirs(dir_list, dry_run=False, verbose=False):
    """处理多个目录"""
    total_removed = 0
    total_checked = 0

    print(f"🚀 开始处理 {len(dir_list)} 个目录...")
    if dry_run:
        print("🔍 预览模式：不会实际删除文件夹\n")

    for i, directory in enumerate(dir_list, 1):
        if not os.path.exists(directory):
            print(f"❌ 目录不存在，跳过: {directory}")
            continue

        if not os.path.isdir(directory):
            print(f"❌ 不是目录，跳过: {directory}")
            continue

        print(f"📂 [{i}/{len(dir_list)}] 处理目录: {directory}")

        removed, checked = remove_empty_folders(directory, dry_run, verbose)
        total_removed += removed
        total_checked += checked

        print(
            f"   📊 该目录统计: 检查了 {checked} 个文件夹，{'将删除' if dry_run else '删除了'} {removed} 个空文件夹\n"
        )

    print("=" * 60)
    print("🎉 处理完成！")
    print(
        f"📊 总计: 检查了 {total_checked} 个文件夹，{'将删除' if dry_run else '删除了'} {total_removed} 个空文件夹"
    )


def find_directories_by_pattern(pattern):
    """根据通配符模式查找目录"""
    paths = glob.glob(pattern)
    directories = [p for p in paths if os.path.isdir(p)]
    return directories


def main():
    parser = argparse.ArgumentParser(description="清除指定文件夹下的空文件夹")
    parser.add_argument("paths", nargs="*", help="要处理的目录路径（可指定多个）")
    parser.add_argument(
        "-p", "--pattern", help="使用通配符模式匹配目录，如 'project/*/output'"
    )
    parser.add_argument(
        "-d", "--dry-run", action="store_true", help="预览模式，不实际删除"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细信息")
    parser.add_argument("--current", action="store_true", help="处理当前目录")

    args = parser.parse_args()

    directories = []

    if args.current:
        directories.append(".")

    if args.paths:
        directories.extend(args.paths)

    if args.pattern:
        pattern_dirs = find_directories_by_pattern(args.pattern)
        directories.extend(pattern_dirs)
        print(f"🔍 通配符 '{args.pattern}' 匹配到 {len(pattern_dirs)} 个目录")

    if not directories:
        print("❌ 请指定要处理的目录路径")
        print("示例用法:")
        print("  python script.py /path/to/folder1 /path/to/folder2")
        print("  python script.py -p 'project/*/output'")
        print("  python script.py --current")
        return

    # 去重并排序
    directories = sorted(list(set(directories)))

    remove_empty_folders_multiple_dirs(directories, args.dry_run, args.verbose)


def quick_clean(directories, dry_run=True):
    """快速清理函数（用于脚本导入）"""
    if isinstance(directories, str):
        directories = [directories]

    remove_empty_folders_multiple_dirs(directories, dry_run)


if __name__ == "__main__":
    main()
