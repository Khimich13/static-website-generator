import os
import shutil
import sys

from markdown_logic import (
    markdown_to_html_node,
    extract_title
)

def main():
    basepath = "/"
    if len(sys.argv) == 2:
        basepath = sys.argv[1]
    root = "/home/khimich13/static-website-generator"
    source = os.path.join(root, "static")
    target = os.path.join(root, "docs")

    if os.path.exists(target):
        shutil.rmtree(target)

    copy_directory(source, target)

    from_path = os.path.join(root, "content")
    template_path = os.path.join(root, "template.html")

    generate_pages_recursive(from_path, template_path, target, basepath)

def copy_directory(source, target):
    if not os.path.exists(target):
        os.mkdir(target)

    for directory in os.listdir(source):
        new_source = os.path.join(source, directory)
        new_target = os.path.join(target, directory)
        if os.path.isfile(new_source):
            shutil.copy(new_source, new_target)
        else:
            copy_directory(new_source, new_target)

def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path, "r") as f:
        markdown = f.read()
    with open(template_path, "r") as f:
        template = f.read()
    html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)
    html_page = (
        template
        .replace(r"{{ Title }}", title)
        .replace(r"{{ Content }}", html)
        .replace("href=\"/", f"href=\"{basepath}")
        .replace("src=\"/", f"src=\"{basepath}")
    )

    dest_dir_path = os.path.dirname(dest_path)
    if dest_dir_path != "":
        os.makedirs(dest_dir_path, exist_ok=True)
    with open(dest_path, "w") as f:
        f.write(html_page)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    if os.path.isfile(dir_path_content):
        if dir_path_content.endswith(".md"):
            generate_page(dir_path_content, template_path, dest_dir_path[:-3] + ".html", basepath)
        return
    
    for directory in os.listdir(dir_path_content):
        cur_content_path = os.path.join(dir_path_content, directory)
        cur_dest_path = os.path.join(dest_dir_path, directory)
        generate_pages_recursive(cur_content_path, template_path, cur_dest_path, basepath)

if __name__ == "__main__":
    main()