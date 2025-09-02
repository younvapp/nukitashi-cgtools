import os
import glob
from PIL import Image
from lupa import LuaRuntime
import argparse

lua = LuaRuntime()


def load_ipt(path):
    """加载并解析一个 .ipt 文件"""
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    lua.execute(code)
    return lua.eval("ipt")


def merge_layers(ipt, img_dir, output_path):
    """根据 ipt 定义合成图片"""
    try:
        # base 层
        base_file = ipt["base"][1] + ".png"  # base[1] 是文件名
        base_path = os.path.join(img_dir, base_file)

        if not os.path.exists(base_path):
            print(f"❌ 找不到基础图片: {base_path}")
            return False

        base_img = Image.open(base_path).convert("RGBA")
        canvas = base_img.copy()

        # 差分层 (Lua 的数组是 1 开始的)
        i = 1
        while True:
            layer = ipt[i]
            if layer is None:
                break
            file = layer["file"] + ".png"
            x, y = int(layer["x"]), int(layer["y"])
            overlay_path = os.path.join(img_dir, file)

            if not os.path.exists(overlay_path):
                print(f"⚠️ 找不到图层文件: {overlay_path}")
                i += 1
                continue

            overlay = Image.open(overlay_path).convert("RGBA")
            canvas.alpha_composite(overlay, dest=(x, y))
            i += 1

        # 保存结果
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        canvas.save(output_path)
        return True

    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return False


def process_single_dir(ipt_dir, img_dir, out_dir):
    """处理单个目录下所有 .ipt 文件"""
    if not os.path.exists(ipt_dir):
        print(f"❌ 目录不存在: {ipt_dir}")
        return 0

    if not os.path.exists(img_dir):
        print(f"❌ 图片目录不存在: {img_dir}")
        return 0

    # 创建输出目录
    os.makedirs(out_dir, exist_ok=True)

    processed_count = 0
    ipt_files = [f for f in os.listdir(ipt_dir) if f.endswith(".ipt")]

    if not ipt_files:
        print(f"⚠️ 在 {ipt_dir} 中未找到 .ipt 文件")
        return 0

    print(f"📁 处理目录: {ipt_dir} (找到 {len(ipt_files)} 个 .ipt 文件)")

    for file in ipt_files:
        ipt_path = os.path.join(ipt_dir, file)
        try:
            ipt = load_ipt(ipt_path)
            out_file = os.path.splitext(file)[0] + ".png"
            output_path = os.path.join(out_dir, out_file)

            if merge_layers(ipt, img_dir, output_path):
                print(f"  ✅ 合成完成: {out_file}")
                processed_count += 1
            else:
                print(f"  ❌ 合成失败: {file}")

        except Exception as e:
            print(f"  ❌ 处理 {file} 时出错: {e}")

    return processed_count


def process_multiple_dirs(base_dirs, output_base="merged"):
    """处理多个目录

    Args:
        base_dirs: 包含 ipt 和图片文件的目录列表
        output_base: 输出根目录
    """
    total_processed = 0

    for base_dir in base_dirs:
        if not os.path.exists(base_dir):
            print(f"❌ 目录不存在，跳过: {base_dir}")
            continue

        # 创建对应的输出目录
        dir_name = os.path.basename(base_dir.rstrip("/\\"))
        out_dir = os.path.join(output_base, dir_name)

        # 处理该目录
        count = process_single_dir(base_dir, base_dir, out_dir)
        total_processed += count

        print(f"📊 目录 {base_dir} 处理完成，成功处理 {count} 个文件\n")

    print(f"🎉 全部处理完成！共成功处理 {total_processed} 个文件")


def process_with_pattern(pattern, output_base="merged"):
    """使用通配符模式处理目录

    Args:
        pattern: 目录匹配模式，如 "image/cg/*/"
        output_base: 输出根目录
    """
    dirs = glob.glob(pattern)
    dirs = [d for d in dirs if os.path.isdir(d)]

    if not dirs:
        print(f"❌ 未找到匹配模式 '{pattern}' 的目录")
        return

    print(f"🔍 找到 {len(dirs)} 个匹配的目录:")
    for d in dirs:
        print(f"  - {d}")
    print()

    process_multiple_dirs(dirs, output_base)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="合成 .ipt 定义的图片")
    parser.add_argument(
        "--pattern",
        type=str,
        default="../nukitashi_assets/image/cg/*/",
        help="目录匹配模式，默认: '../nukitashi_assets/image/cg/*/'",
    )
    parser.add_argument(
        "--output", type=str, default="merged", help="输出根目录，默认: 'merged'"
    )
    args = parser.parse_args()

    pattern = args.pattern
    output_base = args.output

    process_with_pattern(pattern, output_base)
