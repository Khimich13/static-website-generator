import os
import shutil

from markdown_logic import (
    markdown_to_html_node,
    extract_title
)

def main():
    root = "/home/khimich13/static-website-generator"
    source = os.path.join(root, "static")
    public = os.path.join(root, "public")

    if os.path.exists(public):
        shutil.rmtree(public)

    copy_directory(source, public)

    from_path = os.path.join(root, "content")
    template_path = os.path.join(root, "template.html")

    generate_pages_recursive(from_path, template_path, public)

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

def generate_page(from_path, template_path, dest_path):
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
    )

    dest_dir_path = os.path.dirname(dest_path)
    if dest_dir_path != "":
        os.makedirs(dest_dir_path, exist_ok=True)
    with open(dest_path, "w") as f:
        f.write(html_page)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    if os.path.isfile(dir_path_content):
        if dir_path_content.endswith(".md"):
            generate_page(dir_path_content, template_path, dest_dir_path[:-3] + ".html")
        return
    
    for directory in os.listdir(dir_path_content):
        cur_content_path = os.path.join(dir_path_content, directory)
        cur_dest_path = os.path.join(dest_dir_path, directory)
        generate_pages_recursive(cur_content_path, template_path, cur_dest_path)

if __name__ == "__main__":
    main()