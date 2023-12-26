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

home_head = """---
layout: home
title: "%s"
nav_order: 1
---
"""

category_head = """---
layout: default
title: "%s"
has_children: true
---
"""

category_head_with_parent = """---
layout: default
title: "%s"
parent: "%s"
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

    def get_parent_title(self):
        return docfile.get_category(None, self.parent.name)

    def get_grand_parent_title(self):
        return docfile.get_category(None, self.parent.parent.name)


class docfile:
    category_map = {
        "doc": "目录",
        "speech_scrips": "演讲稿",
        "data_base": "数据库",
        "command": "命令",
    }

    def get_category(self, key):  # 将文件名转化为显示的名字
        if key in docfile.category_map:
            return docfile.category_map[key]
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
    if not p.file:
        # TODO 检查是否已经有该索引文件，避免覆盖
        index_path = "%s/index.md" % (p.path)
        with open(index_path, "w") as f:
            if p.depth == 1:
                f.write(home_head % (docfile.get_category(None, p.name)))
            elif p.depth == 2:  # 一级标题不设置parent
                f.write(category_head % (docfile.get_category(None, p.name)))
            else:
                has_children = "false"
                if len(p.data) > 0:
                    has_children = "true"
                f.write(
                    category_head_with_parent
                    % (
                        docfile.get_category(None, p.name),
                        docfile.get_category(None, p.parent.name),
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


def deep_first_gen_index_content(p, base_depth, lines):  # 生成给定节点下的索引文件的内容，储存在lines中
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
            if p.depth == 4:  # 目前目录只支持三层，depth 2 对应1级标题，因此depth 4 对应三级标题
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
