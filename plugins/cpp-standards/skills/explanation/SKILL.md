---
name: explanation
description: How C++ is quoted when explaining C++ code. Use when an explanation shows C++ source.
kind: contract
domain: cpp
---

# Explaining C++ code

Owns how C++ is quoted in an explanation.

Quote each file in its own top-level `cpp` block, never indented inside a list item, under
a line naming the file and starting line number. Copy the code verbatim and replace includes,
header guards, namespace wrappers, and other lines the point does not need with `...`.

Example:

`src/widget/widget.cpp:12`

````cpp
...
void Widget::resize(Size size) {
  bounds_ = size;
  ...
}
````
