import os
import re

default_head = """---
layout: default
title: %s
parent: %s
---
"""

home_head = """---
layout: home
title: Home
---
"""

category_head = """---
layout: home
title: %s
has_children: true
---
"""

category_head_with_parent = """---
layout: home
title: %s
parent: %s
has_children: true
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
        if len(headings) > 0:
            title = headings[0]
            return re.sub(r"^[#\s]*", "", title)
        else:
            return self.filename[:-3]

    def add_head(self):
        if not self.filename.endswith(".md"):
            return
        with open(self.path, "r+") as f:
            # 将文件指针移动到文件开头
            f.seek(0)
            old_content = f.read()
            # 将新内容添加到文件开头
            f.seek(0)
            f.write(default_head % (self.title, self.parent))
            f.write(old_content)

    def add_head_all(self, file_list):
        for df in file_list:
            df.add_head()

    def gen_index(self, file_list):
        r = gen_tree(file_list)
        # 为每个文件夹生成一个索引文件，以构建左边的导航栏
        deep_first_gen_index_file(r)


def deep_first_gen_index_file(p):  # 为所有文件夹生成一个索引文件，如果还没有的话
    if not p.file:
        # TODO 检查是否已经有该索引文件，避免覆盖
        index_path = "%s/index.md" % (p.path)
        with open(index_path, "w") as f:
            if p.depth <= 2:  # 这一级标题不收起来
                f.write(category_head % (docfile.get_category(None, p.name)))
            else:
                f.write(
                    category_head_with_parent
                    % (
                        docfile.get_category(None, p.name),
                        docfile.get_category(None, p.parent.name),
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
    docfile.add_head_all(None, file_list)
    docfile.gen_index(None, file_list)


if __name__ == "__main__":
    main()
