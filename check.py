import argparse
import os


def find_png_only_directories(root_dir):
    """
    递归遍历指定目录，寻找其中只含有png文件的子目录

    Args:
        root_dir (str): 要遍历的根目录路径

    Returns:
        list: 只包含PNG文件的目录列表
    """
    png_only_dirs = []

    for dirpath, _, filenames in os.walk(root_dir):
        if not filenames:
            continue

        png_files = [f for f in filenames if f.lower().endswith(".png")]

        if filenames and len(png_files) == len(filenames):
            png_only_dirs.append(dirpath)

    return png_only_dirs


def main():
    parser = argparse.ArgumentParser(
        description="查找只包含PNG文件的目录",
        epilog="示例: python check.py -d ./images",
    )
    parser.add_argument(
        "-d",
        "--dir",
        type=str,
        default="merged",
        help="要搜索的目录(默认 merged)",
    )
    args = parser.parse_args()
    search_dir = args.dir

    if not search_dir:
        search_dir = os.getcwd()

    # 检查目录是否存在
    if not os.path.exists(search_dir):
        print(f"错误: 目录 '{search_dir}' 不存在")
        return

    if not os.path.isdir(search_dir):
        print(f"错误: '{search_dir}' 不是一个目录")
        return

    print(f"正在搜索目录: {search_dir}")
    print("-" * 50)

    # 查找只包含PNG文件的目录
    png_only_dirs = find_png_only_directories(search_dir)

    if png_only_dirs:
        print(f"找到 {len(png_only_dirs)} 个只包含PNG文件的目录:")
        for i, dir_path in enumerate(png_only_dirs, 1):
            # 显示相对路径（如果可能）
            try:
                rel_path = os.path.relpath(dir_path, search_dir)
                if rel_path != ".":
                    display_path = rel_path
                else:
                    display_path = dir_path
            except ValueError:
                display_path = dir_path

            # 统计PNG文件数量
            png_count = len(
                [f for f in os.listdir(dir_path) if f.lower().endswith(".png")]
            )
            print(f"{i:3d}. {display_path} ({png_count} 个PNG文件)")
    else:
        print("未找到只包含PNG文件的目录")


if __name__ == "__main__":
    main()
