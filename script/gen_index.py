import os
import re

default_head = """---
layout: default
title: %s
parent: %s
---
"""

home_head = """---
title: Home
layout: home
---
"""


class tree:
    def __init__(self, name, depth):
        self.name = name
        self.data = {}
        self.file = None
        self.depth = depth


class docfile:
    category_map = {"speech_scrips": "演讲稿"}

    def get_category(self, key):
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
        with open("./doc/index.md", "w") as f:
            f.write(home_head)
            lines = []
            deep_first(r, lines)
            for line in lines:
                f.write(line)


def deep_first(p, lines):
    if p.file:
        path = "./" + p.file.path[6:][:-3]  # remove ./doc and .md
        lines.append("- [%s](%s)\n" % (p.file.title, path))
    else:
        lines.append(
            "\n%s %s\n\n" % ("#" * p.depth, docfile.get_category(None, p.name))
        )

    for k in p.data:
        deep_first(p.data[k], lines)


def findAllFile(base):
    file_list = []
    for root, ds, fs in os.walk(base):
        for f in fs:
            if not f.endswith(".md"):
                continue
            file_list.append(docfile(root, f))
    return file_list


def gen_tree(file_list) -> tree:
    root = tree("doc", 1)
    for df in file_list:
        p = root
        path_list = df.path.split("/")[2:]  # 取./doc/之后的部分
        for name in path_list:
            if not name in p.data:
                p.data[name] = tree(name, p.depth + 1)
            p = p.data[name]
        p.file = df
    return root


def main():
    base = "./doc"
    file_list = findAllFile(base)
    # docfile.add_head_all(None, file_list)
    docfile.gen_index(None, file_list)


if __name__ == "__main__":
    main()
