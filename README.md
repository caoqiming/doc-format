# doc-format

jekyll build 笔记使用的设置以及样式

主要干了以下事情

1. 在每一个文件夹生下成一个 index.md（如果有就不生成了）
2. 为每一个文件添加 just-the-docs 模板中定义的头部，主要包括层级关系，导航页面的排序
3. 因为 markdown 对 `$$` 声明的公式的处理不是很好（有些情况无法识别），而用 ` ```math ` 定义的公式段，会被 jekyll 处理成代码块，`<code class="language-math">`， 导致 MathJax 无法识别。这里通过正则匹配将` ```math `转化为`$$` 这样 markdown 和网页就都能完美显示公式了。
