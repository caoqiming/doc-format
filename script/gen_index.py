import os
import re

default_head = """---
layout: default
title: "%s"
parent: "%s"
---
"""

default_head_with_grand_parent = """---
layout: default
title: "%s"
parent: "%s"
grand_parent: "%s"
---
"""

# 生成的home页面的头，没有子页面
home_head = """---
layout: home
title: "%s"
nav_order: %s
---
"""

# 生成的目录的头，都有子页面，且有排序
category_head = """---
layout: default
title: "%s"
nav_order: %s
has_children: true
---
"""

category_head_with_parent = """---
layout: default
title: "%s"
nav_order: %s
parent: "%s"
has_children: %s
---
"""

category_head_with_grand_parent = """---
layout: default
title: "%s"
nav_order: %s
parent: "%s"
grand_parent: "%s"
has_children: %s
---
"""


class tree:
    def __init__(self, name, path, parent):
        self.name = name  # 这里是路径里的文件名
        self.data = {}
        self.file = None
        self.path = path
        self.parent = parent
        if parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 1

    def get_title(self):
        return docfile.get_category(None, self.name)

    def get_order(self):
        return docfile.get_order(None, self.name)

    def get_parent_title(self):
        return docfile.get_category(None, self.parent.name)

    def get_grand_parent_title(self):
        return docfile.get_category(None, self.parent.parent.name)


class docfile:
    category_map = {
        # 第一层
        "doc": "Home",
        "math": "数学",
        "language": "语言",
        "linux": "linux 相关",
        "network": "计算机网络",
        "data_base": "数据库&存储",
        "kubernetes": "k8s",
        "machine_learning": "机器学习",
        "encoding_schemes": "编码",
        "project": "有用的项目",
        "speech_scrips": "演讲稿",
        "else": "其他",
        # 其他层
        "command": "命令",
    }

    order_map = {
        # 第一层
        "doc": 1,
        "math": 2,
        "language": 3,
        "linux": 4,
        "network": 5,
        "data_base": 6,
        "kubernetes": 7,
        "machine_learning": 8,
        "encoding_schemes": 9,
        "project": 10,
        "speech_scrips": 11,
        "else": 12,
        # 第二层 linux/
        "command": 1,
        # 第二层 data_base/
        "mysql": 1,
        "redis": 2,
        "transaction_isolation_levels": 3,
        # 第二层 language/
        "markdown": 1,
        "cpp": 2,
        "golang": 3,
        "python": 4,
        # 第二层 machine_learning/
        "nvidia": 1,
    }

    def get_category(self, key):  # 将文件名转化为显示的名字
        if key in docfile.category_map:
            return docfile.category_map[key]
        return key

    #  数字的总会排在字符串的前面
    def get_order(self, key):
        if key in docfile.order_map:
            return docfile.order_map[key]
        return key

    def __init__(self, root, filename) -> None:
        self.root = root
        self.filename = filename
        self.father = os.path.basename(root)
        self.path = self.root + "/" + self.filename
        with open(self.root + "/" + self.filename, "r+") as f:
            # 将文件指针移动到文件开头
            f.seek(0)
            # 读取原始内容
            old_content = f.read()
            self.title = self.get_title(old_content)
            self.parent = self.get_category(self.father)

    def get_title(self, content):
        pattern = r"^#[^#].*$"
        headings = re.findall(pattern, content, re.MULTILINE)
        title = ""
        if len(headings) > 0:
            title = headings[0]
            title = re.sub(r"^[#\s]*", "", title)
        else:
            title = self.filename[:-3]

        return title


def deep_first_gen_index_file(p):  # 为所有文件夹生成一个索引文件，如果还没有的话
    index_path = "%s/index.md" % (p.path)
    if not p.file and not os.path.exists(
        index_path
    ):  # 是文件夹且没有index文件则自动生成
        with open(index_path, "w") as f:
            has_children = "false"
            if len(p.data) > 0:
                has_children = "true"
            if p.depth == 1:
                f.write(home_head % (p.get_title(), p.get_order()))
            elif p.depth == 2:  # 一级标题不设置parent
                f.write(category_head % (p.get_title(), p.get_order()))
            elif p.depth == 3:
                f.write(
                    category_head_with_parent
                    % (
                        p.get_title(),
                        p.get_order(),
                        p.get_parent_title(),
                        has_children,
                    )
                )
            else:
                f.write(
                    category_head_with_grand_parent
                    % (
                        p.get_title(),
                        p.get_order(),
                        p.get_parent_title(),
                        p.get_grand_parent_title(),
                        has_children,
                    )
                )

            lines = []
            deep_first_gen_index_content(p, p.depth, lines)
            data = ""
            for line in lines:
                data += line
            # 如果有连续三个或以上换行，替换为两个
            data = re.sub("\n{3,}", "\n\n", data)
            f.write(data)

    for k in p.data:
        deep_first_gen_index_file(p.data[k])
    return


def deep_first_gen_index_content(
    p, base_depth, lines
):  # 生成给定节点下的索引文件的内容，储存在lines中
    if p.file:
        path = p.file.path[1:][:-3]  # remove ./doc and .md
        lines.append("- [%s](%s)\n" % (p.file.title, path))
    else:
        lines.append(
            "\n%s %s\n\n"
            % ("#" * (p.depth - base_depth + 1), docfile.get_category(None, p.name))
        )

    for k in p.data:
        deep_first_gen_index_content(p.data[k], base_depth, lines)


def deep_first_add_head(p: tree):  # 给md文件添加头
    if p.file and p.file.filename.endswith(".md"):
        with open(p.file.path, "r+") as f:
            # 将文件指针移动到文件开头
            f.seek(0)
            old_content = f.read()
            # 将新内容添加到文件开头
            f.seek(0)
            if p.depth >= 4:  # 对于多级结构添加grand_parent字段避免歧义
                f.write(
                    default_head_with_grand_parent
                    % (p.file.title, p.get_parent_title(), p.get_grand_parent_title())
                )
            else:
                f.write(default_head % (p.file.title, p.get_parent_title()))

            f.write(old_content)

    for k in p.data:
        deep_first_add_head(p.data[k])


def findAllFile(base):
    file_list = []
    for root, ds, fs in os.walk(base):
        for f in fs:
            if not f.endswith(".md"):
                continue
            file_list.append(docfile(root, f))
    return file_list


def gen_tree(file_list) -> tree:
    root = tree("doc", "./doc", None)
    for df in file_list:  # df 是文件，不包括文件夹
        p = root
        path_list = df.path.split("/")[2:]  # 取./doc/之后的部分
        for name in path_list:  # p 从root 走到 df对应的文件，把中途缺失的节点都创建出来
            if not name in p.data:
                p.data[name] = tree(name, p.path + "/" + name, p)
            p = p.data[name]
        p.file = df
    return root


def main():
    base = "./doc"
    file_list = findAllFile(base)
    r = gen_tree(file_list)
    deep_first_add_head(r)
    deep_first_gen_index_file(r)


if __name__ == "__main__":
    main()
